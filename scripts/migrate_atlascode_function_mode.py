"""Phase 3+4 fused: bulk contract inference AND typed-testcase migration for
every problem lacking a Function Mode contract.

Evidence sources, in priority order (Phase 3):
  1. python starter_code's own stub function signature (name + param names) --
     read via `ast`, never guessed from the problem statement.
  2. Real captured argument VALUES: the starter code's own stdin-parsing
     prefix is executed (via `exec`, not reimplemented) with the target stub
     function's body replaced by a one-line capture (`locals()` at function
     entry, which for a fresh call IS exactly the bound arguments -- no
     `inspect.signature` needed). This runs once per real DB test case, so
     the inferred parameter types are grounded in every actual value the
     problem's own 40-case corpus produces, not a single guess.
  3. The already-generated `expected_output` string for each of those same
     cases (never re-derived) -- parsed according to the return-type SHAPE
     detected from the driver's own print-call structure (direct call =
     scalar, join/map = array, ternary literal = boolean, wrapped in a
     `.left`/`.right`-referencing helper = tree).
  4. Where a family factory module exists for the problem (172/216, via
     `atlascode/families/*.py`'s `_SPECS` dicts), its declared `oracle`
     callable is used as a best-effort cross-validation signal, never as the
     source of truth for the typed case values themselves (Phase 18: the
     canonical case is whatever already produced `expected_output`).

Every problem either succeeds and gets a written contract + 40 (or however
many it has) typed test cases, or is quarantined with an exact reason -- never
silently skipped, never guessed past the point evidence runs out.
"""
from __future__ import annotations

import ast
import copy
import importlib
import io
import json
import pkgutil
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

DB_PATH = REPO_ROOT / "atlas.db"


# ── Step 1: find the stub function ──────────────────────────────────────────

def _is_trivial_body(body: list[ast.stmt]) -> bool:
    stmts = body
    if stmts and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.Constant) and isinstance(stmts[0].value.value, str):
        stmts = stmts[1:]  # skip a docstring
    if not stmts:
        return False
    return all(isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis) for s in stmts)


def find_stub_function(tree: ast.Module) -> ast.FunctionDef | None:
    candidates = [
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and _is_trivial_body(n.body)
    ]
    if len(candidates) != 1:
        return None
    fn = candidates[0]
    if fn.args.vararg or fn.args.kwarg or fn.args.kwonlyargs or fn.args.defaults:
        return None
    return fn


# ── Step 2: capture real argument values by executing the starter code ─────

def _build_capture_source(source: str, target_name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == target_name:
            capture_body = ast.parse("__ATLAS_CAPTURE.append(dict(locals()))\nreturn None").body
            node.body = capture_body
            break
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def capture_arguments_for_cases(source: str, target_name: str, inputs: list[str]) -> list[dict | None]:
    capture_src = _build_capture_source(source, target_name)
    compiled = compile(capture_src, "<atlas_infer>", "exec")
    results: list[dict | None] = []
    old_stdin, old_stdout = sys.stdin, sys.stdout
    for inp in inputs:
        g: dict = {"__ATLAS_CAPTURE": []}
        sys.stdin = io.StringIO(inp)
        sys.stdout = io.StringIO()
        try:
            exec(compiled, g)
        except BaseException:
            pass
        finally:
            sys.stdin, sys.stdout = old_stdin, old_stdout
        cap = g.get("__ATLAS_CAPTURE") or []
        results.append(cap[0] if cap else None)
    return results


# ── Step 3: type inference from captured values ─────────────────────────────

def _is_tree_node(v) -> bool:
    return v is not None and hasattr(v, "val") and hasattr(v, "left") and hasattr(v, "right")


def _node_to_bfs_array(root) -> list:
    if root is None:
        return []
    out = [root.val]
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        for child in (node.left, node.right):
            if child is None:
                out.append(None)
            else:
                out.append(child.val)
                queue.append(child)
    while out and out[-1] is None:
        out.pop()
    return out


def _normalize_value(v):
    """Recursively converts tuples/sets to lists (JSON has neither) --
    applied to every captured argument value before type inference or
    storage. Sets are sorted for determinism (order is meaningless for a
    set argument; a stable order is required for JSON storage)."""
    if isinstance(v, (list, tuple)):
        return [_normalize_value(e) for e in v]
    if isinstance(v, set):
        try:
            return [_normalize_value(e) for e in sorted(v)]
        except TypeError:
            return [_normalize_value(e) for e in sorted(v, key=repr)]
    return v


def _scalar_kind(v) -> str | None:
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    return None


class TypeInferenceError(Exception):
    pass


def _infer_tuple_from_rows(rows: list) -> dict:
    """Fallback when a list-of-lists' flattened elements don't agree on one
    scalar kind (see infer_type's array branch): rather than quarantine
    immediately, check whether every row is the SAME fixed width -- if so
    this is a heterogeneous fixed-width RECORD (e.g. min-stack-simulation's
    `("PUSH", 5)` / `("POP", None)` op pairs), not a homogeneous array, and
    each COLUMN position gets its own independently-inferred type."""
    lengths = {len(r) for r in rows}
    if len(lengths) != 1:
        raise TypeInferenceError(f"inconsistent tuple arity across rows: {sorted(lengths)}")
    width = lengths.pop()
    if width == 0:
        raise TypeInferenceError("zero-width rows: cannot infer a tuple type")
    columns = [infer_type([r[i] for r in rows]) for i in range(width)]
    return {"kind": "tuple", "elements": columns}


def _infer_item_type(elems: list) -> dict:
    """The item type for an array's elements -- tries the normal homogeneous
    path first (unchanged behavior for every existing array/matrix problem),
    and only falls back to per-column tuple inference (see
    _infer_tuple_from_rows) when scalar kinds genuinely disagree AND every
    element is itself a fixed-width row, never silently for any other
    disagreement (e.g. a real int/string mismatch elsewhere still quarantines
    exactly as before)."""
    try:
        return infer_type(elems)
    except TypeInferenceError as e:
        if "inconsistent scalar kinds" in str(e) and all(isinstance(v, list) for v in elems):
            return _infer_tuple_from_rows(elems)
        raise


def infer_type(values: list) -> dict:
    """values: the observed Python objects for ONE parameter across cases
    (trees already converted to BFS arrays before this is called)."""
    non_none = [v for v in values if v is not None]
    if not non_none:
        raise TypeInferenceError("all-None: cannot infer a type with zero evidence")
    sample = non_none[0]
    if isinstance(sample, list):
        elems = [e for v in non_none for e in v]
        elem_type = _infer_item_type(elems) if elems else {"kind": "integer"}
        has_none_elem = any(e is None for v in non_none for e in v)
        item_spec = {"kind": "optional", "items": elem_type} if has_none_elem else elem_type
        base = {"kind": "array", "items": item_spec}
    else:
        kind = _scalar_kind(sample)
        if kind is None:
            raise TypeInferenceError(f"unsupported value type: {type(sample)!r}")
        # Every non-None sample must agree on scalar kind (mixed int/str etc.
        # across cases would mean the inference itself is wrong).
        for v in non_none:
            k = _scalar_kind(v)
            if k != kind:
                # int/float mixing is fine -- widen to float.
                if {k, kind} == {"integer", "float"}:
                    kind = "float"
                else:
                    raise TypeInferenceError(f"inconsistent scalar kinds: {kind} vs {k}")
        base = {"kind": kind}
    if any(v is None for v in values):
        return {"kind": "optional", "items": base}
    return base


# ── Step 4: return-type shape classification via the driver's print call ───

class _InlineNames(ast.NodeTransformer):
    def __init__(self, assigns: dict[str, ast.expr]):
        self.assigns = assigns

    def visit_Name(self, node: ast.Name):
        if node.id in self.assigns:
            return copy.deepcopy(self.assigns[node.id])
        return node


def _assign_map(tree: ast.Module) -> dict[str, ast.expr]:
    m: dict[str, ast.expr] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                m[target.id] = node.value
            elif isinstance(target, ast.Tuple):
                # `i, j = two_sum(nums, target)` -- both unpacked names map to
                # the WHOLE rhs call (imprecise about which tuple index, but
                # sufficient for shape classification, which only needs to
                # know "this print argument's dependency chain touches the
                # target function call somewhere").
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        m[elt.id] = node.value
    return m


def _contains_call(node: ast.AST, name: str) -> bool:
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name for n in ast.walk(node))


def _find_print_args(tree: ast.Module) -> list[ast.expr] | None:
    """Returns the LAST top-level-reachable print(...) call's argument list
    (as separate expressions -- `print(a, b)` has 2, matching how Python's
    print joins them with a single space, textually identical to
    `print(' '.join(map(str, [a, b])))`)."""
    found = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print" and n.args:
            found = list(n.args)
    return found


def _is_minmax_pair(exprs: list[ast.expr], target_name: str, assigns: dict[str, ast.expr]) -> bool:
    """Detects `print(min(i, j), max(i, j))` (in either min/max order) where
    i, j both trace back (via _assign_map's tuple-unpack mapping) to the
    target function's call -- Program Mode's own way of saying "this pair's
    order doesn't matter, only the values do."""
    if len(exprs) != 2:
        return False
    names = {"min", "max"}
    fn_names = set()
    for e in exprs:
        if not (isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in names):
            return False
        fn_names.add(e.func.id)
        # The min()/max() ARGUMENTS (e.g. `i, j`) are what need to trace back
        # to the target call -- inline through the assignment map to resolve
        # each Name operand to its source expression.
        expanded_operands = [_InlineNames(assigns).visit(copy.deepcopy(a)) for a in e.args]
        if not any(_contains_call(op, target_name) for op in expanded_operands):
            return False
    return fn_names == names


def classify_return_shape(source: str, target_name: str) -> str:
    """Returns one of: scalar | array | sorted_pair | boolean | tree | unknown."""
    tree = ast.parse(source)
    print_args = _find_print_args(tree)
    if not print_args:
        return "unknown"
    assigns = _assign_map(tree)

    # Check the RAW (pre-inlining) args for the min/max pattern first -- the
    # inlined/expanded version would blow the pattern apart.
    if _is_minmax_pair(print_args, target_name, assigns):
        return "sorted_pair"

    expanded_args = [print_args[0]]
    for _ in range(4):
        expanded_args = [_InlineNames(assigns).visit(copy.deepcopy(e)) for e in expanded_args]
    expanded = expanded_args[0]

    if len(print_args) == 1 and isinstance(expanded, ast.Call) and isinstance(expanded.func, ast.Name) and expanded.func.id == target_name:
        return "scalar"
    # `print(f'{fn(...):.2f}')` -- an f-string wrapping a SINGLE formatted
    # call to the target function is still semantically a scalar return, not
    # an array; found as a real bug via fractional-knapsack (its `:.2f`
    # formatting made `expanded` a JoinedStr, which fell through to the
    # generic "contains a call to fn -> array" catch-all below, corrupting
    # its stored contract to array<float>). Must be checked before that
    # catch-all, same reasoning as the array_sentinel/matrix checks above it.
    if (
        len(print_args) == 1
        and isinstance(expanded, ast.JoinedStr)
        and len(expanded.values) == 1
        and isinstance(expanded.values[0], ast.FormattedValue)
        and isinstance(expanded.values[0].value, ast.Call)
        and isinstance(expanded.values[0].value.func, ast.Name)
        and expanded.values[0].value.func.id == target_name
    ):
        return "scalar"
    for n in ast.walk(expanded):
        # Only a TRUE boolean ternary (`'true' if cond else 'false'`, both
        # branches literal constants) counts -- a ternary whose branches do
        # real computation (e.g. kmp's `' '.join(...) if result else '-1'`,
        # an array with an empty-result sentinel, not a boolean at all) must
        # fall through to the array/scalar checks below instead of being
        # misclassified just because *some* IfExp is present in the tree.
        if (
            isinstance(n, ast.IfExp)
            and isinstance(n.body, ast.Constant)
            and isinstance(n.orelse, ast.Constant)
            and _contains_call(n.test, target_name)
        ):
            return "boolean"
    func_defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for n in ast.walk(expanded):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in func_defs:
            helper_src = ast.unparse(func_defs[n.func.id])
            if ".left" in helper_src and ".right" in helper_src and _contains_call(n, target_name):
                return "tree"
    # `' '.join(map(str, result)) if result else '-1'` -- an array with an
    # empty-result SENTINEL string (not a boolean: the orelse literal isn't
    # 'true'/'false', and the body does real join/map computation, not a
    # constant). The sentinel is encoded into the shape string itself so
    # parse_expected_for_shape can special-case an exact sentinel match as
    # the empty list, not a literal one-element array.
    for n in ast.walk(expanded):
        if (
            isinstance(n, ast.IfExp)
            and isinstance(n.orelse, ast.Constant)
            and isinstance(n.orelse.value, str)
            and n.orelse.value.lower() not in ("true", "false")
            and _contains_call(n.body, target_name)
        ):
            return f"array_sentinel:{n.orelse.value}"
    # `print('\n'.join(' '.join(map(str, row)) for row in result))` -- the
    # SAME 2D-matrix shape as the `for row in fn(...): print(...)` statement
    # form checked later in this function, but as a generator expression
    # inside the print call. Must be checked BEFORE the generic array
    # catch-all below, which would otherwise match first (the genexpr's
    # `result` name resolves right back to the target call too).
    for n in ast.walk(expanded):
        if isinstance(n, (ast.GeneratorExp, ast.ListComp)):
            for gen in n.generators:
                expanded_iter = _InlineNames(assigns).visit(copy.deepcopy(gen.iter))
                if _contains_call(expanded_iter, target_name):
                    return "matrix"
    if len(print_args) > 1 and any(
        _contains_call(_InlineNames(assigns).visit(copy.deepcopy(e)), target_name) for e in print_args
    ):
        return "array"
    if _contains_call(expanded, target_name):
        return "array"

    # `for row in target_fn(...): print(...)` (one line per row -- a 2D
    # matrix return) or `for a, b in target_fn(...): print(a, b)` (a list of
    # fixed-size row-tuples, e.g. merged intervals).
    for node in tree.body:
        if isinstance(node, ast.For) and _contains_call(node.iter, target_name):
            has_print = any(
                isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"
                for n in ast.walk(node)
            )
            if has_print:
                return "matrix"
    # `print('\n'.join(' '.join(map(str, row)) for row in result))` -- the
    # SAME 2D-matrix shape as above, but as a generator expression inside
    # the print call rather than a `for` statement (a different syntactic
    # form of the identical row-per-line pattern).
    for n in ast.walk(tree):
        if isinstance(n, (ast.GeneratorExp, ast.ListComp)):
            for gen in n.generators:
                expanded_iter = _InlineNames(assigns).visit(copy.deepcopy(gen.iter))
                if _contains_call(expanded_iter, target_name):
                    return "matrix"
    return "unknown"


def detect_mutated_param_index(source: str, target_name: str) -> int | None:
    """Detects the in-place-mutation pattern used by every sorting-algorithm
    problem: `bubble_sort(nums)` (return value discarded, called as a bare
    statement) followed later by printing the SAME caller-side variable
    (`nums`), never the function's return value. Returns the 0-based
    position of the mutated argument in the CALL SITE (which must then be
    matched back to the stub function's own parameter name by the caller),
    or None if this problem doesn't follow that shape."""
    tree = ast.parse(source)
    call_args = None
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == target_name:
            call_args = node.value.args
            break
    if call_args is None:
        return None
    print_args = _find_print_args(tree)
    if not print_args:
        return None
    for idx, arg_expr in enumerate(call_args):
        if not isinstance(arg_expr, ast.Name):
            continue
        var_name = arg_expr.id
        for p in print_args:
            if any(isinstance(n, ast.Name) and n.id == var_name for n in ast.walk(p)):
                return idx
    return None


def decide_scalar_kind(raws: list[str]) -> str:
    """One consistent scalar kind for ALL of a problem's cases -- deciding
    per-case independently is wrong (e.g. prime-factorization's answer is
    always a space-joined STRING of factors, but a single-factor case like
    '17' parses as a valid integer in isolation; that must not flip the
    problem's return type case-by-case)."""
    kinds: set[str] = set()
    for raw in raws:
        s = raw.strip()
        if s.lower() in ("true", "false"):
            kinds.add("boolean")
            continue
        try:
            int(s)
            kinds.add("integer")
            continue
        except ValueError:
            pass
        try:
            float(s)
            kinds.add("float")
            continue
        except ValueError:
            pass
        kinds.add("string")
    if kinds == {"integer"}:
        return "integer"
    if kinds and kinds <= {"integer", "float"}:
        return "float"
    if kinds == {"boolean"}:
        return "boolean"
    return "string"


def parse_scalar_as(raw: str, kind: str):
    s = raw.strip()
    if kind == "boolean":
        return s.lower() == "true"
    if kind == "integer":
        return int(s)
    if kind == "float":
        return float(s)
    return s


def parse_expected_for_shape(raw: str, shape: str) -> tuple[dict, object]:
    """Returns (return_type_spec, canonical typed value) for ONE case's
    expected_output string, given the classified return shape. Raises on any
    string this shape can't parse (caller quarantines)."""
    s = raw.strip()
    if shape == "boolean":
        if s.lower() not in ("true", "false"):
            raise ValueError(f"expected boolean literal, got {s!r}")
        return {"kind": "boolean"}, s.lower() == "true"
    sentinel = None
    if shape.startswith("array_sentinel:"):
        sentinel = shape.split(":", 1)[1]
        shape = "array"
    if shape in ("array", "tree", "sorted_pair"):
        if s == "" or (sentinel is not None and s == sentinel):
            tokens: list[str] = []
        else:
            tokens = s.split()
        has_null = any(t == "null" for t in tokens)
        item_kind = "integer"
        for t in tokens:
            if t == "null":
                continue
            try:
                int(t)
            except ValueError:
                try:
                    float(t)
                    item_kind = "float"
                except ValueError:
                    item_kind = "string"
                    break
        def _conv(t: str):
            if t == "null":
                return None
            if item_kind == "integer":
                return int(t)
            if item_kind == "float":
                return float(t)
            return t
        values = [_conv(t) for t in tokens]
        item_spec = {"kind": item_kind}
        wrapped_item = {"kind": "optional", "items": item_spec} if has_null else item_spec
        outer_kind = "tree" if shape == "tree" else "array"
        result: dict = {"kind": outer_kind, "items": wrapped_item}
        if shape == "sorted_pair":
            result["comparator"] = "sorted"
        return result, values
    if shape == "matrix":
        # One row per line, space-joined ints within a row (a 2D return, or
        # a list of fixed-size row-tuples like merged intervals).
        lines = [ln for ln in s.split("\n")] if s else []
        rows = [ln.split() for ln in lines]
        item_kind = "integer"
        for row in rows:
            for t in row:
                try:
                    int(t)
                except ValueError:
                    try:
                        float(t)
                        item_kind = "float"
                    except ValueError:
                        item_kind = "string"
        def _conv_cell(t: str):
            if item_kind == "integer":
                return int(t)
            if item_kind == "float":
                return float(t)
            return t
        values = [[_conv_cell(t) for t in row] for row in rows]
        return {"kind": "array", "items": {"kind": "array", "items": {"kind": item_kind}}}, values
    raise ValueError(f"unclassified return shape: {shape}")


# ── Step 5: family oracle cross-validation (best-effort, not authoritative) ─

def load_family_oracles() -> dict[str, object]:
    """problem_id -> oracle callable, for the 172/216 problems backed by a
    simple `_SPECS`-dict family factory. Used only as corroboration."""
    import algorithm_atlas.atlascode.families as fam_pkg
    oracle_of: dict[str, object] = {}
    for m in pkgutil.iter_modules(fam_pkg.__path__):
        if m.name.endswith("_testdata") or m.name in ("searching", "sorting"):
            continue
        try:
            mod = importlib.import_module(f"algorithm_atlas.atlascode.families.{m.name}")
        except Exception:
            continue
        specs = getattr(mod, "_SPECS", None)
        if not isinstance(specs, dict):
            continue
        for pid, spec in specs.items():
            oracle = getattr(spec, "oracle", None)
            if oracle is not None:
                oracle_of[pid] = oracle
    return oracle_of


# ── Main migration ───────────────────────────────────────────────────────────

def migrate() -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, starter_code, function_contract FROM problems ORDER BY id")
    problems = cur.fetchall()

    oracle_of = load_family_oracles()

    ledger: dict[str, dict] = {}
    quarantine: dict[str, dict] = {}
    already_done = 0
    t0 = time.monotonic()
    processed = 0

    for row in problems:
        pid = row["id"]
        if row["function_contract"] is not None:
            already_done += 1
            ledger[pid] = {"status": "already_verified", "confidence": 1.0, "evidence": ["pre-existing verified contract"]}
            continue

        processed += 1
        try:
            starter = json.loads(row["starter_code"])
            py_source = starter.get("python")
            if not py_source:
                raise ValueError("no python starter_code")

            tree = ast.parse(py_source)
            stub = find_stub_function(tree)
            if stub is None:
                raise ValueError("no unique trivial-body stub function found")
            fn_name = stub.name
            param_names = [a.arg for a in stub.args.args]

            cur.execute(
                "SELECT id, input_data, expected_output FROM test_cases WHERE problem_id = ? ORDER BY \"order\"",
                (pid,),
            )
            cases = cur.fetchall()
            if not cases:
                raise ValueError("no test cases")

            captured = capture_arguments_for_cases(py_source, fn_name, [c["input_data"] for c in cases])
            n_ok = sum(1 for c in captured if c is not None)
            if n_ok < max(1, len(cases) // 2):
                raise ValueError(f"argument capture failed for {len(cases) - n_ok}/{len(cases)} cases")

            # Convert any tree Node objects to canonical BFS arrays, tuples/
            # sets to lists (JSON has neither), per parameter.
            param_values: dict[str, list] = {name: [] for name in param_names}
            tree_params: set[str] = set()
            for cap in captured:
                if cap is None:
                    continue
                for name in param_names:
                    if name not in cap:
                        raise ValueError(f"captured locals missing parameter '{name}'")
                    v = cap[name]
                    if _is_tree_node(v):
                        tree_params.add(name)
                        v = _node_to_bfs_array(v)
                    else:
                        v = _normalize_value(v)
                    param_values[name].append(v)

            parameters = []
            for name in param_names:
                if name in tree_params:
                    spec = {"kind": "tree", "items": {"kind": "integer"}}
                else:
                    spec = infer_type(param_values[name])
                parameters.append({"name": name, "type": spec})

            mutated_idx = detect_mutated_param_index(py_source, fn_name)
            mutates_argument = param_names[mutated_idx] if mutated_idx is not None and mutated_idx < len(param_names) else None

            raw_outputs = [c["expected_output"] for c in cases]
            if mutates_argument is not None:
                # Return "shape" is exactly the mutated parameter's own
                # (already-inferred) type -- the mutated argument's post-call
                # value IS the checked output, never the discarded return value.
                return_type = next(p["type"] for p in parameters if p["name"] == mutates_argument)
                case_expected = [parse_expected_for_shape(raw, "array")[1] for raw in raw_outputs] if return_type["kind"] == "array" else None
                if case_expected is None:
                    raise ValueError(f"mutated argument has unsupported non-array type: {return_type}")
            else:
                shape = classify_return_shape(py_source, fn_name)
                if shape == "unknown":
                    raise ValueError("could not classify return shape from driver's print call")

                if shape == "scalar":
                    scalar_kind = decide_scalar_kind(raw_outputs)
                    return_type = {"kind": scalar_kind}
                    case_expected = [parse_scalar_as(raw, scalar_kind) for raw in raw_outputs]
                else:
                    return_type = None
                    case_expected = []
                    for raw in raw_outputs:
                        rt, val = parse_expected_for_shape(raw, shape)
                        if return_type is None:
                            return_type = rt
                        elif return_type["kind"] != rt["kind"]:
                            raise ValueError(f"inconsistent return shape across cases: {return_type} vs {rt}")
                        elif rt["kind"] in ("array", "tree") and rt["items"] != return_type["items"]:
                            if return_type["items"].get("kind") != "optional" and rt["items"].get("kind") == "optional":
                                return_type["items"] = rt["items"]
                        case_expected.append(val)

            contract = {"function_name": fn_name, "parameters": parameters, "return_type": return_type}
            if mutates_argument is not None:
                contract["mutates_argument"] = mutates_argument

            # Best-effort oracle cross-validation (corroboration only).
            oracle_agree = None
            oracle = oracle_of.get(pid)
            if oracle is not None:
                agree = 0
                total = 0
                for i, cap in enumerate(captured):
                    if cap is None:
                        continue
                    try:
                        pos_args = [cap[name] for name in param_names]
                        result = oracle(*pos_args)
                        total += 1
                        if result == case_expected[i] or (hasattr(result, "__eq__") and result == case_expected[i]):
                            agree += 1
                    except Exception:
                        pass
                oracle_agree = f"{agree}/{total}" if total else "oracle_call_failed"

            # Write contract + typed cases.
            cur.execute("UPDATE problems SET function_contract = ? WHERE id = ?", (json.dumps(contract), pid))
            for c, cap, expected in zip(cases, captured, case_expected):
                if cap is None:
                    continue
                args_out = {}
                for name in param_names:
                    v = cap[name]
                    if name in tree_params:
                        v = _node_to_bfs_array(v)
                    else:
                        v = _normalize_value(v)
                    args_out[name] = v
                cur.execute(
                    "UPDATE test_cases SET function_args = ?, function_expected = ? WHERE id = ?",
                    (json.dumps(args_out), json.dumps(expected), c["id"]),
                )

            ledger[pid] = {
                "status": "inferred",
                "confidence": round(n_ok / len(cases), 3),
                "cases_migrated": n_ok,
                "cases_total": len(cases),
                "contract": contract,
                "oracle_cross_validation": oracle_agree,
                "evidence": ["starter_code stub AST", "exec-captured arguments", "expected_output shape classification"],
            }
        except Exception as e:
            quarantine[pid] = {
                "problem_id": pid,
                "reason": str(e),
                "failed_stage": "contract_or_case_inference",
                "next_action": "manual review or targeted family-specific extraction",
            }

        if processed % 20 == 0:
            elapsed = time.monotonic() - t0
            rate = processed / elapsed if elapsed > 0 else 0
            print(f"[{processed} processed] rate={rate:.1f}/sec inferred={len(ledger)-already_done} quarantined={len(quarantine)}")

    conn.commit()
    conn.close()

    (REPO_ROOT / "docs" / "atlascode-contracts-inferred.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    (REPO_ROOT / "docs" / "atlascode-quarantine.json").write_text(json.dumps(quarantine, indent=2), encoding="utf-8")

    return {
        "total_problems": len(problems),
        "already_verified": already_done,
        "newly_inferred": len(ledger) - already_done,
        "quarantined": len(quarantine),
    }


if __name__ == "__main__":
    summary = migrate()
    print("\nCONTRACT + TYPED-CASE MIGRATION SUMMARY")
    for k, v in summary.items():
        print(f"  {k}: {v}")
