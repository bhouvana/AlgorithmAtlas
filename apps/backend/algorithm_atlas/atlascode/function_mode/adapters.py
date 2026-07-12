"""
FunctionModeAdapter: the per-language boundary between a contract + typed
arguments and an executable program. Only PythonFunctionAdapter exists today;
every other language in notebook.py's RUNNERS registry is a documented,
honest gap (see registry.py's SUPPORTED_LANGUAGES) rather than a fake
pass-through.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from .contracts import FunctionContract, TypeSpec
from .protocol import CONTRACT_ERROR_SENTINEL, RESULT_SENTINEL


class FunctionModeAdapter(Protocol):
    def generate_starter(self, contract: FunctionContract) -> str: ...
    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str: ...


def _py_type_hint(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "int"
    if spec.kind == "float":
        return "float"
    if spec.kind == "boolean":
        return "bool"
    if spec.kind == "string":
        return "str"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_py_type_hint(spec.items)} | None"
    if spec.kind == "array":
        assert spec.items is not None
        return f"list[{_py_type_hint(spec.items)}]"
    if spec.kind == "tree":
        # Not `object` -- a Node with .val/.left/.right, matching Program
        # Mode's own locally-defined `class Node` shape exactly (same
        # attribute names) so a solution written for one mode reads
        # naturally in the other.
        return "TreeNode | None"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"tuple[{', '.join(_py_type_hint(e) for e in spec.elements)}]"
    return "object"


def _contract_uses_tree(contract: FunctionContract) -> bool:
    specs = [p.type for p in contract.parameters] + [contract.return_type]
    return any(s.kind == "tree" for s in specs)


# Shared by every tree-typed Python contract (18/216 problems). Attribute
# names (val/left/right) deliberately match Program Mode's own locally-defined
# `class Node` in each problem's stdin-parsing starter code, so a solution
# written against one mode's tree shape reads naturally in the other.
_TREE_CLASS_PY = (
    "class TreeNode:\n"
    "    def __init__(self, val=0, left=None, right=None):\n"
    "        self.val = val\n"
    "        self.left = left\n"
    "        self.right = right\n\n\n"
)

# BFS array <-> tree conversion, matching the exact trailing-null-trimmed
# level-order format Program Mode's own stdin parser/serializer already uses
# (see docs/atlascode-dual-mode-resume.md's "tree serialization format").
_TREE_HELPERS_PY = (
    "def __atlas_build_tree(arr):\n"
    "    if not arr or arr[0] is None:\n"
    "        return None\n"
    "    root = TreeNode(arr[0])\n"
    "    queue = [root]\n"
    "    i = 1\n"
    "    qi = 0\n"
    "    while qi < len(queue) and i < len(arr):\n"
    "        node = queue[qi]\n"
    "        qi += 1\n"
    "        if i < len(arr):\n"
    "            if arr[i] is not None:\n"
    "                node.left = TreeNode(arr[i])\n"
    "                queue.append(node.left)\n"
    "            i += 1\n"
    "        if i < len(arr):\n"
    "            if arr[i] is not None:\n"
    "                node.right = TreeNode(arr[i])\n"
    "                queue.append(node.right)\n"
    "            i += 1\n"
    "    return root\n"
    "def __atlas_serialize_tree(root):\n"
    "    if root is None:\n"
    "        return []\n"
    "    out = [root.val]\n"
    "    queue = [root]\n"
    "    qi = 0\n"
    "    while qi < len(queue):\n"
    "        node = queue[qi]\n"
    "        qi += 1\n"
    "        for child in (node.left, node.right):\n"
    "            if child is None:\n"
    "                out.append(None)\n"
    "            else:\n"
    "                out.append(child.val)\n"
    "                queue.append(child)\n"
    "    while out and out[-1] is None:\n"
    "        out.pop()\n"
    "    return out\n"
)


@dataclass(frozen=True)
class PythonFunctionAdapter:
    """The driver protocol, in order:
      1. user's function code (verbatim, unmodified, never sent back to the client)
      2. a server-generated block that:
         - looks up the required function by name (missing -> Contract Error sentinel)
         - binds the canonical arguments to its signature via inspect.signature
           .bind(**args) -- a signature mismatch (wrong parameter names/arity,
           e.g. the user renamed the function's parameters) is a structural
           Contract Error, NOT a Wrong Answer and NOT swallowed as a generic
           exception
         - calls the function with NO try/except around the call itself, so a
           genuine bug in the user's algorithm raises normally, exits nonzero,
           and is reported as a real Runtime Error by the existing subprocess
           runner -- exactly like Program Mode already does
         - serializes the return value as JSON behind a sentinel line so the
           driver's own output can never be confused with any debug print()
           the user's function happens to make
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name}: {_py_type_hint(p.type)}" for p in contract.parameters)
        return_hint = _py_type_hint(contract.return_type)
        prefix = _TREE_CLASS_PY if _contract_uses_tree(contract) else ""
        return f"{prefix}def {contract.function_name}({params}) -> {return_hint}:\n    pass\n"

    # %-style templating (not f-strings/.format) is deliberate: the generated
    # target code is full of literal `{`/`}` dict syntax, and %-substitution
    # is the only formatting mechanism that doesn't also use braces, so there
    # is no risk of brace-escaping mistakes corrupting the driver's own source.
    _DRIVER_TEMPLATE = (
        "import json as __atlas_json, inspect as __atlas_inspect\n"
        "%(tree_helpers)s"
        "def __atlas_main():\n"
        "    __atlas_args = __atlas_json.loads(%(args_literal)s)\n"
        "%(tree_conversions)s"
        "    __atlas_fn = globals().get(%(fn_name_literal)s)\n"
        "    if __atlas_fn is None or not callable(__atlas_fn):\n"
        "        print(%(contract_sentinel)r + __atlas_json.dumps("
        "{'reason': 'missing_function', 'message': %(missing_msg)s}))\n"
        "        return\n"
        "    try:\n"
        "        __atlas_bound = __atlas_inspect.signature(__atlas_fn).bind(**__atlas_args)\n"
        "    except TypeError as __atlas_exc:\n"
        "        print(%(contract_sentinel)r + __atlas_json.dumps("
        "{'reason': 'signature_mismatch', 'message': %(mismatch_prefix)s + str(__atlas_exc)}))\n"
        "        return\n"
        "    __atlas_result = __atlas_fn(*__atlas_bound.args, **__atlas_bound.kwargs)\n"
        "    print(%(result_sentinel)r + __atlas_json.dumps(%(result_expr)s))\n"
        "__atlas_main()\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        # TreeNode must be defined BEFORE the user's code, not after: a plain
        # `def f(root: TreeNode | None)` evaluates the annotation eagerly at
        # def-time, so TreeNode has to already exist or the user's own stub
        # would raise NameError before the driver ever runs.
        prefix = _TREE_CLASS_PY if uses_tree else ""
        tree_conversions = "".join(
            f"    __atlas_args[{name!r}] = __atlas_build_tree(__atlas_args[{name!r}])\n"
            for name in tree_params
        )
        if contract.mutates_argument is not None:
            # Program Mode's own convention for these problems: the function's
            # return value is discarded, only the (in-place-mutated) argument
            # is checked -- Function Mode mirrors that exactly rather than
            # trusting a return value the reference driver never looks at.
            result_expr = f"__atlas_args[{contract.mutates_argument!r}]"
        elif contract.return_type.kind == "tree":
            result_expr = "__atlas_serialize_tree(__atlas_result)"
        else:
            result_expr = "__atlas_result"

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_PY if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": json.dumps(json.dumps(arguments)),  # double-encode -> safe Python string literal
            "fn_name_literal": json.dumps(contract.function_name),
            "missing_msg": json.dumps(f"Required function '{contract.function_name}' was not found."),
            "mismatch_prefix": json.dumps(
                f"'{contract.function_name}' does not accept arguments {contract.parameter_names}: "
            ),
            "contract_sentinel": CONTRACT_ERROR_SENTINEL,
            "result_sentinel": RESULT_SENTINEL,
            "result_expr": result_expr,
        }
        return f"{prefix}{user_code}\n\n{driver}"


def _js_type_hint(spec: TypeSpec) -> str:
    """JSDoc-style hint only -- JS has no static types to enforce, so this is
    purely a starter-code readability aid, never validated at runtime (the
    language-agnostic contracts.validate_arguments already does real
    validation server-side before any adapter runs)."""
    if spec.kind == "integer" or spec.kind == "float":
        return "number"
    if spec.kind == "boolean":
        return "boolean"
    if spec.kind == "string":
        return "string"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_js_type_hint(spec.items)}|null"
    if spec.kind == "array":
        assert spec.items is not None
        return f"{_js_type_hint(spec.items)}[]"
    if spec.kind == "tree":
        return "TreeNode|null"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"[{', '.join(_js_type_hint(e) for e in spec.elements)}]"
    return "*"


# Mirrors _TREE_CLASS_PY/_TREE_HELPERS_PY's Python shape exactly (same
# val/left/right field names, same BFS-array wire format) -- shared by both
# JavaScriptFunctionAdapter and TypeScriptFunctionAdapter since they use the
# identical calling convention.
_TREE_HELPERS_JS = (
    "function TreeNode(val, left, right) {\n"
    "  this.val = (val === undefined ? 0 : val);\n"
    "  this.left = (left === undefined ? null : left);\n"
    "  this.right = (right === undefined ? null : right);\n"
    "}\n"
    "function __atlas_build_tree(arr) {\n"
    "  if (!arr || arr.length === 0 || arr[0] === null) { return null; }\n"
    "  var root = new TreeNode(arr[0]);\n"
    "  var queue = [root];\n"
    "  var i = 1, qi = 0;\n"
    "  while (qi < queue.length && i < arr.length) {\n"
    "    var node = queue[qi]; qi += 1;\n"
    "    if (i < arr.length) {\n"
    "      if (arr[i] !== null) { node.left = new TreeNode(arr[i]); queue.push(node.left); }\n"
    "      i += 1;\n"
    "    }\n"
    "    if (i < arr.length) {\n"
    "      if (arr[i] !== null) { node.right = new TreeNode(arr[i]); queue.push(node.right); }\n"
    "      i += 1;\n"
    "    }\n"
    "  }\n"
    "  return root;\n"
    "}\n"
    "function __atlas_serialize_tree(root) {\n"
    "  if (root === null || root === undefined) { return []; }\n"
    "  var out = [root.val];\n"
    "  var queue = [root];\n"
    "  var qi = 0;\n"
    "  while (qi < queue.length) {\n"
    "    var node = queue[qi]; qi += 1;\n"
    "    var children = [node.left, node.right];\n"
    "    for (var c = 0; c < children.length; c++) {\n"
    "      var child = children[c];\n"
    "      if (child === null || child === undefined) { out.push(null); }\n"
    "      else { out.push(child.val); queue.push(child); }\n"
    "    }\n"
    "  }\n"
    "  while (out.length > 0 && out[out.length - 1] === null) { out.pop(); }\n"
    "  return out;\n"
    "}\n"
)


@dataclass(frozen=True)
class JavaScriptFunctionAdapter:
    """
    Same driver contract as PythonFunctionAdapter (missing-function and
    signature-mismatch are Function Contract Errors, a genuine bug inside the
    user's function is an uncaught exception -> real Runtime Error, the
    result is JSON behind a sentinel line), adapted to JS's calling
    convention:

    - JS has no keyword-argument binding, so arguments are passed
      POSITIONALLY in the contract's declared parameter order. Unlike Python,
      this means the user's parameter NAMES don't have to match the
      contract's -- only position and arity do. This is a deliberate,
      documented per-language difference (Phase 6: canonical operation vs.
      language-specific callable shape), not an oversight.
    - Arity is checked via `fn.length` as a best-effort signature guard. This
      undercounts default-valued and rest parameters (a JS engine limitation,
      not something this adapter can see around) -- a user relying on those
      could bypass the check. Since a genuine arity problem still surfaces
      as either wrong results (Wrong Answer) or a thrown TypeError (Runtime
      Error) when real hidden-shape arguments are missing, this is a soft
      diagnostic, not the only correctness backstop.
    - `function_name` is reused verbatim from the (Python-authored, snake_case)
      contract rather than remapped to camelCase. snake_case is valid JS, so
      this is not a correctness gap -- just not idiomatic JS style. A real
      per-language callable-name field (Phase 6/7) would fix the style but
      requires a schema change out of scope for unblocking real execution now.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(p.name for p in contract.parameters)
        param_docs = "\n".join(f" * @param {{{_js_type_hint(p.type)}}} {p.name}" for p in contract.parameters)
        return_doc = f" * @returns {{{_js_type_hint(contract.return_type)}}}"
        return f"/**\n{param_docs}\n{return_doc}\n */\nfunction {contract.function_name}({params}) {{\n\n}}\n"

    # %-style templating for the same brace-collision reason as Python's (the
    # driver is full of literal `{`/`}` JS syntax).
    _DRIVER_TEMPLATE = (
        "%(tree_helpers)s"
        "(function () {\n"
        "  var __atlas_args = JSON.parse(%(args_literal)s);\n"
        "%(tree_conversions)s"
        "  if (typeof %(fn_name_raw)s !== 'function') {\n"
        "    console.log(%(contract_sentinel)s + JSON.stringify({reason: 'missing_function', message: %(missing_msg)s}));\n"
        "    return;\n"
        "  }\n"
        "  if (%(fn_name_raw)s.length !== %(arity)d) {\n"
        "    console.log(%(contract_sentinel)s + JSON.stringify({reason: 'signature_mismatch', message: %(mismatch_prefix)s + %(fn_name_raw)s.length + ' parameter(s).'}));\n"
        "    return;\n"
        "  }\n"
        "  var __atlas_positional = %(arg_order_literal)s.map(function (k) { return __atlas_args[k]; });\n"
        "  var __atlas_result = %(fn_name_raw)s.apply(null, __atlas_positional);\n"
        "  var __atlas_out = %(result_expr)s;\n"
        "  console.log(%(result_sentinel)s + JSON.stringify(__atlas_out === undefined ? null : __atlas_out));\n"
        "})();\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f"  __atlas_args[{json.dumps(name)}] = __atlas_build_tree(__atlas_args[{json.dumps(name)}]);\n"
            for name in tree_params
        )
        if contract.mutates_argument is not None:
            result_expr = f"__atlas_args[{json.dumps(contract.mutates_argument)}]"
        elif contract.return_type.kind == "tree":
            result_expr = "__atlas_serialize_tree(__atlas_result)"
        else:
            result_expr = "__atlas_result"

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_JS if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": json.dumps(json.dumps(arguments)),
            "fn_name_raw": contract.function_name,  # trusted, server-authored identifier -- never user input
            "arg_order_literal": json.dumps(contract.parameter_names),
            "arity": len(contract.parameters),
            "missing_msg": json.dumps(f"Required function '{contract.function_name}' was not found."),
            "mismatch_prefix": json.dumps(
                f"'{contract.function_name}' expects {len(contract.parameters)} parameter(s), got "
            ),
            "contract_sentinel": json.dumps(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": json.dumps(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"{user_code}\n\n{driver}"


def _ts_type_hint(spec: TypeSpec) -> str:
    """Real TypeScript syntax (unlike JS's JSDoc-only hint) -- `run_typescript`
    executes via `tsx`, which transpiles without type-checking, so a mismatch
    here can never block execution; it's a starter-code correctness/
    readability aid, not an enforcement mechanism (server-side
    contracts.validate_arguments is the real gate, same as the JS adapter)."""
    if spec.kind == "integer" or spec.kind == "float":
        return "number"
    if spec.kind == "boolean":
        return "boolean"
    if spec.kind == "string":
        return "string"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_ts_type_hint(spec.items)} | null"
    if spec.kind == "array":
        assert spec.items is not None
        return f"{_ts_type_hint(spec.items)}[]"
    if spec.kind == "tree":
        return "TreeNode | null"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"[{', '.join(_ts_type_hint(e) for e in spec.elements)}]"
    return "any"


@dataclass(frozen=True)
class TypeScriptFunctionAdapter:
    """
    Same driver contract and JS-family calling convention as
    JavaScriptFunctionAdapter (positional args in contract order, `fn.length`
    arity check, missing-function/signature-mismatch -> Function Contract
    Error, an uncaught exception -> real Runtime Error, sentinel-delimited
    JSON result) -- the only real difference is `generate_starter` emits
    actual TypeScript type annotations instead of JSDoc comments, since the
    language supports them.

    `run_typescript` already writes source to a temp `.ts` file and executes
    it via `tsx` (see notebook.py) -- that path never embedded source in argv,
    so unlike python/javascript/ruby/shell this adapter did not need an
    infrastructure fix first (confirmed by the 17-runner transport audit,
    docs/atlascode-runner-transport-audit.json).

    The generated driver itself is deliberately loose-typed (`any`
    throughout): `tsx` transpiles without type-checking, so this is a
    pragmatic choice, not a missed opportunity for stricter types -- the
    driver's job is to move JSON in and out, not to model the contract's
    types in TypeScript's type system.
    """

    _TS_TREE_INTERFACE = (
        "interface TreeNode {\n"
        "  val: number;\n"
        "  left: TreeNode | null;\n"
        "  right: TreeNode | null;\n"
        "}\n\n"
    )

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name}: {_ts_type_hint(p.type)}" for p in contract.parameters)
        return_hint = _ts_type_hint(contract.return_type)
        prefix = self._TS_TREE_INTERFACE if _contract_uses_tree(contract) else ""
        return f"{prefix}function {contract.function_name}({params}): {return_hint} {{\n\n}}\n"

    # %-style templating for the same brace-collision reason as JS's.
    _DRIVER_TEMPLATE = (
        "%(tree_helpers)s"
        "(function (): void {\n"
        "  const __atlas_args: any = JSON.parse(%(args_literal)s);\n"
        "%(tree_conversions)s"
        "  if (typeof %(fn_name_raw)s !== 'function') {\n"
        "    console.log(%(contract_sentinel)s + JSON.stringify({reason: 'missing_function', message: %(missing_msg)s}));\n"
        "    return;\n"
        "  }\n"
        "  if ((%(fn_name_raw)s as any).length !== %(arity)d) {\n"
        "    console.log(%(contract_sentinel)s + JSON.stringify({reason: 'signature_mismatch', message: %(mismatch_prefix)s + (%(fn_name_raw)s as any).length + ' parameter(s).'}));\n"
        "    return;\n"
        "  }\n"
        "  const __atlas_positional: any[] = (%(arg_order_literal)s as string[]).map(function (k: string): any { return __atlas_args[k]; });\n"
        "  const __atlas_result: any = (%(fn_name_raw)s as any).apply(null, __atlas_positional);\n"
        "  const __atlas_out: any = %(result_expr)s;\n"
        "  console.log(%(result_sentinel)s + JSON.stringify(__atlas_out === undefined ? null : __atlas_out));\n"
        "})();\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f"  __atlas_args[{json.dumps(name)}] = __atlas_build_tree(__atlas_args[{json.dumps(name)}]);\n"
            for name in tree_params
        )
        if contract.mutates_argument is not None:
            result_expr = f"__atlas_args[{json.dumps(contract.mutates_argument)}]"
        elif contract.return_type.kind == "tree":
            result_expr = "__atlas_serialize_tree(__atlas_result)"
        else:
            result_expr = "__atlas_result"

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_JS if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": json.dumps(json.dumps(arguments)),
            "fn_name_raw": contract.function_name,  # trusted, server-authored identifier -- never user input
            "arg_order_literal": json.dumps(contract.parameter_names),
            "arity": len(contract.parameters),
            "missing_msg": json.dumps(f"Required function '{contract.function_name}' was not found."),
            "mismatch_prefix": json.dumps(
                f"'{contract.function_name}' expects {len(contract.parameters)} parameter(s), got "
            ),
            "contract_sentinel": json.dumps(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": json.dumps(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"{user_code}\n\n{driver}"


# ── Perl ─────────────────────────────────────────────────────────────────────
# Interpreted, not compiled -- `run_perl` (notebook.py) has no isolable
# compile step to reuse via PREPARERS, so this uses compose_source (embed
# THIS case's arguments in the composed SOURCE TEXT, recompose+rerun per
# case) exactly like Python/JS/TS -- NOT the compiled adapters'
# compose_program pattern, and NOT stdin: runner.py's interpreted-adapter
# path calls `runner(source, TEST_TIMEOUT)` with no `input_bytes` at all,
# so a driver expecting piped stdin would simply hang.
#
# Genuinely the least code of any adapter so far: Perl's core JSON::PP
# module (confirmed present in this environment's Perl 5.36.1, part of core
# since 5.14 -- no extra install needed) decodes a JSON array DIRECTLY into
# a Perl arrayref, which is already exactly the right shape for arrays,
# matrices, AND tuples (a fixed-width heterogeneous array like min-stack's
# `["PUSH", 5]` is just an arrayref like any other -- Perl's dynamic typing
# means tuple decode needs no special case at all, unlike Java/C++/Rust/C).
# Mutation is free too: the decoded arrayref IS the same reference the
# user's sub receives, so `push`/`sort`/direct element assignment on it
# already mutates what the driver reads back afterward. Only tree (a
# structural concept absent from JSON entirely) needs real driver code:
# BFS-array <-> hashref-node conversion, same val/left/right convention as
# every other adapter's tree representation.

def _perl_squote(s: str) -> str:
    """Perl single-quoted string literal -- unlike json.dumps's double-quoted
    output, single quotes never interpolate `@`/`$`. Found as a real bug: the
    sentinel constants (`@@ATLASCODE_RESULT@@`) fed through json.dumps into a
    double-quoted Perl string made Perl try to interpolate an array variable
    named ATLASCODE_RESULT, fataling under `use strict` on every single run."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


_TREE_HELPERS_PERL = (
    "sub __atlas_build_tree {\n"
    "    my ($arr) = @_;\n"
    "    return undef if !@$arr || !defined $arr->[0];\n"
    "    my $root = { val => $arr->[0], left => undef, right => undef };\n"
    "    my @queue = ($root);\n"
    "    my $i = 1;\n"
    "    while (@queue && $i < scalar(@$arr)) {\n"
    "        my $node = shift @queue;\n"
    "        if ($i < scalar(@$arr)) {\n"
    "            if (defined $arr->[$i]) {\n"
    "                $node->{left} = { val => $arr->[$i], left => undef, right => undef };\n"
    "                push @queue, $node->{left};\n"
    "            }\n"
    "            $i++;\n"
    "        }\n"
    "        if ($i < scalar(@$arr)) {\n"
    "            if (defined $arr->[$i]) {\n"
    "                $node->{right} = { val => $arr->[$i], left => undef, right => undef };\n"
    "                push @queue, $node->{right};\n"
    "            }\n"
    "            $i++;\n"
    "        }\n"
    "    }\n"
    "    return $root;\n"
    "}\n"
    "sub __atlas_serialize_tree {\n"
    "    my ($root) = @_;\n"
    "    my @out = ();\n"
    "    return \\@out if !defined $root;\n"
    "    push @out, $root->{val};\n"
    "    my @queue = ($root);\n"
    "    while (@queue) {\n"
    "        my $node = shift @queue;\n"
    "        for my $child ($node->{left}, $node->{right}) {\n"
    "            if (!defined $child) { push @out, undef; }\n"
    "            else { push @out, $child->{val}; push @queue, $child; }\n"
    "        }\n"
    "    }\n"
    "    pop @out while (@out && !defined $out[-1]);\n"
    "    return \\@out;\n"
    "}\n"
)


@dataclass(frozen=True)
class PerlFunctionAdapter:
    """
    Same driver contract as the other interpreted adapters (missing
    function -> Function Contract Error, a genuine bug inside the user's
    function -> uncaught `die`/runtime exception -> real Runtime Error via
    the subprocess's nonzero exit code, sentinel-delimited JSON result) --
    Perl-specific calling convention:

    - Positional arguments in the contract's declared parameter order
      (`@_`), same rationale as JS: Perl subs don't bind by parameter name
      either.
    - No arity/signature check is emitted (unlike JS's soft `fn.length`
      check) -- Perl subroutines don't enforce a fixed arity at the
      language level (extra args are silently ignored, missing ones are
      `undef`), so there is no equivalent cheap introspection signal to
      check before calling; a real arity mismatch still surfaces
      naturally as wrong results or an `undef`-related runtime error, the
      same "soft diagnostic, not the only correctness backstop" reasoning
      the JS adapter's own docstring already accepts for its arity check.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(contract.parameter_names)
        return (
            f"# sub {contract.function_name}({params})\n"
            f"sub {contract.function_name} {{\n"
            f"    my ({params}) = @_;\n\n"
            f"}}\n"
        )

    @staticmethod
    def _encode_expr(spec: TypeSpec, value_expr: str) -> str:
        """A Perl expression coercing `value_expr` to the JSON shape its
        declared TypeSpec demands before `encode_json` ever sees it.

        This is NOT redundant with JSON::PP's own type inference: Perl hash
        KEYS are always internally string-flagged, even when every key
        originated from a JSON-decoded integer (`keys %counts` on a hash
        built from `$counts{$x}++` for integer `$x`) -- a real, common
        pattern (e.g. any frequency-counting solution) that would otherwise
        silently serialize as JSON strings ("1") instead of numbers (1),
        found as a genuine bug via this adapter's own top-k-frequent ladder
        test. Every other adapter encodes according to the DECLARED return
        type rather than trusting a generic serializer's guess (Java's
        _java_encode_expr, C++/C's typed print statements, Rust's ToJson
        trait); this closes the same gap for Perl."""
        if spec.kind == "integer":
            return f"(({value_expr}) + 0)"
        if spec.kind == "float":
            return f"(({value_expr}) + 0.0)"
        if spec.kind == "string":
            return f'("" . ({value_expr}))'
        if spec.kind == "boolean":
            return f"(({value_expr}) ? JSON::PP::true : JSON::PP::false)"
        if spec.kind == "tree":
            return f"__atlas_serialize_tree({value_expr})"
        if spec.kind == "optional":
            assert spec.items is not None
            inner = PerlFunctionAdapter._encode_expr(spec.items, "$__ov")
            return f"(defined({value_expr}) ? do {{ my $__ov = ({value_expr}); {inner} }} : undef)"
        if spec.kind == "array":
            assert spec.items is not None
            inner = PerlFunctionAdapter._encode_expr(spec.items, "$_")
            return f"[map {{ {inner} }} @{{{value_expr}}}]"
        if spec.kind == "tuple":
            assert spec.elements is not None
            parts = [
                PerlFunctionAdapter._encode_expr(e, f"({value_expr})->[{i}]")
                for i, e in enumerate(spec.elements)
            ]
            return "[" + ", ".join(parts) + "]"
        return value_expr

    _DRIVER_TEMPLATE = (
        "use strict;\nuse warnings;\nuse JSON::PP;\n\n"
        "%(tree_helpers)s"
        "my $__atlas_args = decode_json(%(args_literal)s);\n"
        "%(tree_conversions)s"
        "if (!defined &%(fn_name_raw)s) {\n"
        "    print %(contract_sentinel)s . encode_json({reason => 'missing_function', message => %(missing_msg)s}) . \"\\n\";\n"
        "    exit 0;\n"
        "}\n"
        "my @__atlas_positional = map { $__atlas_args->{$_} } @{decode_json(%(arg_order_literal)s)};\n"
        "my $__atlas_result = %(fn_name_raw)s(@__atlas_positional);\n"
        "my $__atlas_out = %(result_expr)s;\n"
        "print %(result_sentinel)s . encode_json($__atlas_out) . \"\\n\";\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f"$__atlas_args->{{{json.dumps(name)}}} = __atlas_build_tree($__atlas_args->{{{json.dumps(name)}}});\n"
            for name in tree_params
        )
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            raw_expr = f"$__atlas_args->{{{json.dumps(contract.mutates_argument)}}}"
            result_expr = self._encode_expr(contract.parameters[mutated_idx].type, raw_expr)
        else:
            result_expr = self._encode_expr(contract.return_type, "$__atlas_result")

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_PERL if uses_tree else "",
            "tree_conversions": tree_conversions,
            # Perl single-quoted, not json.dumps's double-quoted output: JSON
            # text can contain a literal `@` (e.g. a string test case value
            # like "test@example.com"), which Perl would try to interpolate
            # as an array variable inside a double-quoted string -- the same
            # class of bug _perl_squote's docstring describes for the
            # sentinels, just triggered by arbitrary test DATA instead of a
            # fixed constant. JSON text never contains an unescaped single
            # quote, so wrapping the whole json.dumps() output in Perl
            # single-quotes is always safe.
            "args_literal": _perl_squote(json.dumps(arguments)),
            "fn_name_raw": contract.function_name,  # trusted, server-authored identifier -- never user input
            "arg_order_literal": _perl_squote(json.dumps(contract.parameter_names)),
            "missing_msg": _perl_squote(f"Required function '{contract.function_name}' was not found."),
            "contract_sentinel": _perl_squote(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": _perl_squote(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"{user_code}\n\n{driver}"


# ── Ruby ─────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) -- `run_ruby` (notebook.py)
# has no isolable compile step, same as Perl.
#
# Simpler than Perl: Ruby's core `json` library (`require 'json'`) decodes a
# JSON object/array into native Hash/Array with NO analogue of Perl's hash-
# key-string-flag gotcha (Ruby Hash keys keep their real Integer/String type
# from JSON.parse, so no contract-aware re-encoding step is needed the way
# _perl_squote's sibling `PerlFunctionAdapter._encode_expr` had to add).
# Tuples are free too (a JSON array is just a Ruby Array, min-stack's
# `["PUSH", 5]` needs no special decode). Only tree needs real driver code
# (BFS-array <-> TreeNode object, same val/left/right convention as every
# other adapter) -- and even that's simpler than Perl's hashref version
# since Ruby's `class Foo; end` can be safely re-opened/redefined without
# erroring, so there's no "did the user already define this" duplicate-
# definition check to make (unlike every compiled adapter's TreeNode
# handling).

_TREE_HELPERS_RUBY = (
    "class TreeNode\n"
    "  attr_accessor :val, :left, :right\n"
    "  def initialize(val = 0, left = nil, right = nil)\n"
    "    @val = val\n"
    "    @left = left\n"
    "    @right = right\n"
    "  end\n"
    "end\n"
    "def __atlas_build_tree(arr)\n"
    "  return nil if arr.empty? || arr[0].nil?\n"
    "  root = TreeNode.new(arr[0])\n"
    "  queue = [root]\n"
    "  i = 1\n"
    "  while !queue.empty? && i < arr.length\n"
    "    node = queue.shift\n"
    "    if i < arr.length\n"
    "      unless arr[i].nil?\n"
    "        node.left = TreeNode.new(arr[i])\n"
    "        queue.push(node.left)\n"
    "      end\n"
    "      i += 1\n"
    "    end\n"
    "    if i < arr.length\n"
    "      unless arr[i].nil?\n"
    "        node.right = TreeNode.new(arr[i])\n"
    "        queue.push(node.right)\n"
    "      end\n"
    "      i += 1\n"
    "    end\n"
    "  end\n"
    "  root\n"
    "end\n"
    "def __atlas_serialize_tree(root)\n"
    "  out = []\n"
    "  return out if root.nil?\n"
    "  out.push(root.val)\n"
    "  queue = [root]\n"
    "  while !queue.empty?\n"
    "    node = queue.shift\n"
    "    [node.left, node.right].each do |child|\n"
    "      if child.nil?\n"
    "        out.push(nil)\n"
    "      else\n"
    "        out.push(child.val)\n"
    "        queue.push(child)\n"
    "      end\n"
    "    end\n"
    "  end\n"
    "  out.pop while !out.empty? && out.last.nil?\n"
    "  out\n"
    "end\n"
)


def _ruby_squote(s: str) -> str:
    """Ruby single-quoted string literal -- unlike a double-quoted string,
    single quotes never interpolate `#{...}`, and never treat backslash
    specially except before another backslash or a single quote. Used for
    the same defensive reason as Perl's `_perl_squote`: JSON test DATA
    (not just fixed sentinel constants) could coincidentally contain `#{`
    and must not be misinterpreted as Ruby interpolation syntax."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


@dataclass(frozen=True)
class RubyFunctionAdapter:
    """
    Same driver contract as the other interpreted adapters (missing method
    -> Function Contract Error, a genuine bug inside the user's method ->
    uncaught exception -> real Runtime Error via the subprocess's nonzero
    exit code, sentinel-delimited JSON result) -- Ruby-specific calling
    convention:

    - Positional arguments in the contract's declared parameter order, same
      rationale as JS/Perl: a top-level `def foo(a, b)` binds by position,
      not by the caller's argument names.
    - Missing-method detection via `respond_to?(:name, true)` on the
      top-level `main` object (top-level `def` methods become private
      instance methods of Object, hence `include_all=true` in the
      `respond_to?` call -- omitting it would report even a genuinely
      defined top-level method as "missing").
    - No arity check emitted: unlike JS's soft `fn.length` signal, Ruby DOES
      raise `ArgumentError: wrong number of arguments` automatically for a
      strict-arity method call mismatch -- a REAL Ruby-level error, not a
      missing diagnostic, so it already surfaces honestly as a Runtime
      Error without the adapter needing to check anything itself.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(contract.parameter_names)
        return f"def {contract.function_name}({params})\n\nend\n"

    _DRIVER_TEMPLATE = (
        "require 'json'\n\n"
        "%(tree_helpers)s"
        "__atlas_args = JSON.parse(%(args_literal)s)\n"
        "%(tree_conversions)s"
        "if !self.respond_to?(:%(fn_name_raw)s, true)\n"
        "  puts %(contract_sentinel)s + {reason: 'missing_function', message: %(missing_msg)s}.to_json\n"
        "  exit(0)\n"
        "end\n"
        "__atlas_positional = %(arg_order_literal)s.map { |k| __atlas_args[k] }\n"
        "__atlas_result = send(:%(fn_name_raw)s, *__atlas_positional)\n"
        "__atlas_out = %(result_expr)s\n"
        "puts %(result_sentinel)s + __atlas_out.to_json\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f"__atlas_args[{json.dumps(name)}] = __atlas_build_tree(__atlas_args[{json.dumps(name)}])\n"
            for name in tree_params
        )
        if contract.mutates_argument is not None:
            result_expr = f"__atlas_args[{json.dumps(contract.mutates_argument)}]"
        elif contract.return_type.kind == "tree":
            result_expr = "__atlas_serialize_tree(__atlas_result)"
        else:
            result_expr = "__atlas_result"

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_RUBY if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": _ruby_squote(json.dumps(arguments)),
            "fn_name_raw": contract.function_name,  # trusted, server-authored identifier -- never user input
            # A genuine Ruby array literal (not a quoted string to parse) --
            # safe as plain double-quoted Ruby string elements since
            # parameter names are trusted server-generated identifiers,
            # never containing `#{` or an unescaped quote.
            "arg_order_literal": json.dumps(contract.parameter_names),
            "missing_msg": _ruby_squote(f"Required function '{contract.function_name}' was not found."),
            "contract_sentinel": _ruby_squote(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": _ruby_squote(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"{user_code}\n\n{driver}"


# ── PHP ──────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_php -- no
# PREPARERS entry, same as Perl/Ruby.
#
# PHP's `json_decode($s, true)` gives associative arrays for both JSON
# objects and JSON arrays (PHP has one array type for both), which is
# already the right shape for arrays, matrices, AND tuples (min-stack's
# `["PUSH", 5]` decodes to `[0 => "PUSH", 1 => 5]`, indexed exactly like any
# other array -- no special tuple handling needed, same as every other
# dynamically-typed adapter). Unlike Perl, PHP array keys do NOT get a
# string-only flag -- a numeric key (even one that started as a hash/map
# key from something like `$counts[$num]++`) round-trips through
# `json_encode` as a real JSON number, confirmed directly against this
# environment's PHP 8.3.32 before writing this adapter, so no Perl-style
# contract-aware re-encoding step is needed here.
#
# Unlike Ruby (whose `class Foo; end` can be silently redeclared), PHP
# raises a FATAL ERROR on `Cannot redeclare class TreeNode` -- so tree
# support needs the same "skip if the user's own resubmitted starter code
# already declares it" guard every compiled adapter's TreeNode handling
# uses, even though this is an interpreted, not compiled, adapter.

_TREE_HELPERS_PHP = (
    "class TreeNode {\n"
    "    public $val;\n"
    "    public $left;\n"
    "    public $right;\n"
    "    function __construct($val = 0, $left = null, $right = null) {\n"
    "        $this->val = $val;\n"
    "        $this->left = $left;\n"
    "        $this->right = $right;\n"
    "    }\n"
    "}\n"
    "function __atlas_build_tree($arr) {\n"
    "    if (empty($arr) || $arr[0] === null) return null;\n"
    "    $root = new TreeNode($arr[0]);\n"
    "    $queue = [$root];\n"
    "    $i = 1;\n"
    "    $n = count($arr);\n"
    "    while (count($queue) > 0 && $i < $n) {\n"
    "        $node = array_shift($queue);\n"
    "        if ($i < $n) {\n"
    "            if ($arr[$i] !== null) {\n"
    "                $node->left = new TreeNode($arr[$i]);\n"
    "                $queue[] = $node->left;\n"
    "            }\n"
    "            $i++;\n"
    "        }\n"
    "        if ($i < $n) {\n"
    "            if ($arr[$i] !== null) {\n"
    "                $node->right = new TreeNode($arr[$i]);\n"
    "                $queue[] = $node->right;\n"
    "            }\n"
    "            $i++;\n"
    "        }\n"
    "    }\n"
    "    return $root;\n"
    "}\n"
    "function __atlas_serialize_tree($root) {\n"
    "    $out = [];\n"
    "    if ($root === null) return $out;\n"
    "    $out[] = $root->val;\n"
    "    $queue = [$root];\n"
    "    while (count($queue) > 0) {\n"
    "        $node = array_shift($queue);\n"
    "        foreach ([$node->left, $node->right] as $child) {\n"
    "            if ($child === null) { $out[] = null; }\n"
    "            else { $out[] = $child->val; $queue[] = $child; }\n"
    "        }\n"
    "    }\n"
    "    while (count($out) > 0 && end($out) === null) array_pop($out);\n"
    "    return $out;\n"
    "}\n"
)


def _php_squote(s: str) -> str:
    """PHP single-quoted string literal -- unlike a double-quoted string,
    single quotes never interpolate `$var`/`{$expr}`, and only need `\\`
    and `'` escaped. Same defensive reasoning as Perl/Ruby's equivalents:
    JSON test DATA (not just fixed sentinel constants) could coincidentally
    contain a literal `$` and must not be misread as PHP variable
    interpolation."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


@dataclass(frozen=True)
class PhpFunctionAdapter:
    """
    Same driver contract as the other interpreted adapters (missing
    function -> Function Contract Error, a genuine bug inside the user's
    function -> uncaught error/exception -> real Runtime Error via the
    subprocess's nonzero exit code, sentinel-delimited JSON result) --
    PHP-specific calling convention:

    - Positional arguments in the contract's declared parameter order,
      same rationale as JS/Perl/Ruby: PHP functions bind positionally
      (named arguments exist since PHP 8 but the contract's parameter
      names aren't guaranteed to match what a user names their own
      function's parameters).
    - Missing-function detection via `function_exists('name')`.
    - No arity check emitted: PHP raises a real `ArgumentCountError` (a
      genuine fatal error, uncaught -> nonzero exit -> honest Runtime
      Error) for a strict too-few-arguments call, the same "language
      already reports this honestly" reasoning as Ruby's adapter.
    - The call itself is a literal `function_name($arg0, $arg1)` using the
      trusted, server-authored function name directly (never
      `call_user_func_array`) -- found as a real, necessary fix: PHP's
      by-reference parameters (`function bubble_sort(&$arr)`, the 21
      in-place-sort problems' convention) only mutate the CALLER's
      variable when the argument is a genuine variable at the call site.
      `call_user_func_array($fn, $positionalArray)` passes each argument as
      an ARRAY ELEMENT, which does NOT satisfy PHP's by-reference binding
      even when the array itself holds the right value -- confirmed via
      this adapter's own bubble-sort ladder test silently returning the
      UNSORTED input before this fix. Decoding into individually-named
      `$__atlas_argN` variables and calling with a literal, non-dynamic
      call expression sidesteps the problem entirely.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"${p}" for p in contract.parameter_names)
        return f"function {contract.function_name}({params}) {{\n\n}}\n"

    _DRIVER_TEMPLATE = (
        "%(tree_helpers)s"
        "$__atlas_args = json_decode(%(args_literal)s, true);\n"
        "%(tree_conversions)s"
        "if (!function_exists(%(fn_name_quoted)s)) {\n"
        "    echo %(contract_sentinel)s . json_encode(['reason' => 'missing_function', 'message' => %(missing_msg)s]) . \"\\n\";\n"
        "    exit(0);\n"
        "}\n"
        "%(arg_decls)s"
        "%(call_statement)s\n"
        "$__atlas_out = %(result_expr)s;\n"
        "echo %(result_sentinel)s . json_encode($__atlas_out) . \"\\n\";\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f"$__atlas_args[{json.dumps(name)}] = __atlas_build_tree($__atlas_args[{json.dumps(name)}]);\n"
            for name in tree_params
        )

        arg_decls = "".join(
            f"$__atlas_arg{idx} = $__atlas_args[{json.dumps(p.name)}];\n"
            for idx, p in enumerate(contract.parameters)
        )
        call_args = ", ".join(f"$__atlas_arg{idx}" for idx in range(len(contract.parameters)))
        raw_call = f"{contract.function_name}({call_args})"

        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"{raw_call};"
            result_expr = f"$__atlas_arg{mutated_idx}"
        elif contract.return_type.kind == "tree":
            call_statement = f"$__atlas_result = {raw_call};"
            result_expr = "__atlas_serialize_tree($__atlas_result)"
        else:
            call_statement = f"$__atlas_result = {raw_call};"
            result_expr = "$__atlas_result"

        tree_prefix = "" if "class TreeNode" in user_code else _TREE_HELPERS_PHP

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": tree_prefix if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": _php_squote(json.dumps(arguments)),
            "fn_name_quoted": _php_squote(contract.function_name),  # trusted, server-authored identifier
            "arg_decls": arg_decls,
            "call_statement": call_statement,
            "missing_msg": _php_squote(f"Required function '{contract.function_name}' was not found."),
            "contract_sentinel": _php_squote(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": _php_squote(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"<?php\n{user_code}\n\n{driver}"


# ── R ────────────────────────────────────────────────────────────────────────
# Interpreted (compose_source, recomposed per case) via run_r -- no PREPARERS
# entry, same as Perl/Ruby/PHP.
#
# Real, documented environment dependency (same category of finding as a
# prior session's `tsx` global-install issue for TypeScript): base R has NO
# built-in JSON support at all, unlike every other language here. This
# adapter requires the third-party `jsonlite` CRAN package to be installed
# for whichever R this judge invokes (`install.packages("jsonlite")`, a
# one-time ~2s operation using a precompiled Windows binary, no compiler
# toolchain needed) -- confirmed installed and working in THIS environment
# during this session, but a fresh R install elsewhere would need the same
# step or every R Function Mode submission would fail at the `library(jsonlite)`
# line with a real, clear "there is no package called 'jsonlite'" error
# (not silently -- that failure is an honest Runtime Error, not a hang or a
# false pass).
#
# A second real, found-before-running-anything R quirk: unlike every other
# language here, R identifiers CANNOT start with an underscore (`_foo` is a
# syntax error) -- so this adapter's internal driver variables use a
# leading-DOT convention (`.atlas_args`, `.atlas_result`, ...) instead of
# the `__atlas_` prefix every other adapter uses, which is both valid R
# syntax and idiomatically signals "internal" the same way a leading
# underscore does in other languages.
#
# The one genuinely R-specific design decision: unlike Python/JS/Ruby/Perl/
# PHP (all mutable-by-reference for arrays/lists) or C/C++/Rust/Java/C#/Go
# (explicit pointer/ref parameters), R vectors are COPY-ON-MODIFY -- an
# ordinary function call can NEVER mutate the caller's variable, full stop
# (R has no `&`/pointer/mutable-reference-parameter mechanism for this at
# all; the only way to get reference semantics is a distinct `environment`
# object, which would force every mutation-style starter to expose a
# non-idiomatic signature real R solutions don't use). So for the 21
# in-place-sort "mutates_argument" contracts specifically, this adapter
# uses the function's RETURN VALUE as the result instead of re-reading the
# original argument -- matching how idiomatic R actually sorts (`x <- sort(x)`,
# never `sort_in_place(x)`), and documented here as a deliberate, necessary
# per-language adaptation, not an oversight that copies every other
# adapter's "read back the mutated argument" convention blindly.

_TREE_HELPERS_R = (
    # R `list`s are copy-on-modify -- `node <- queue[[qi]]; node$left <- x`
    # mutates a LOCAL COPY, not the shared structure, so a plain list-based
    # BFS tree build would silently lose every child assignment once a
    # node is re-visited through a different reference (found by reasoning
    # through R's value semantics before ever running this, not from a
    # failed test). `environment` is R's actual mutable-reference type --
    # `e$left <- x` mutates the SAME object every other reference to `e`
    # sees, exactly like every other adapter's TreeNode object/pointer.
    ".atlas_new_node <- function(v) {\n"
    "  e <- new.env()\n"
    "  e$val <- v\n"
    "  e$left <- NULL\n"
    "  e$right <- NULL\n"
    "  e\n"
    "}\n"
    ".atlas_build_tree <- function(arr) {\n"
    "  if (length(arr) == 0 || is.null(arr[[1]])) return(NULL)\n"
    "  root <- .atlas_new_node(arr[[1]])\n"
    "  queue <- list(root)\n"
    "  i <- 2\n"
    "  qi <- 1\n"
    "  n <- length(arr)\n"
    "  while (qi <= length(queue) && i <= n) {\n"
    "    node <- queue[[qi]]\n"
    "    qi <- qi + 1\n"
    "    if (i <= n) {\n"
    "      if (!is.null(arr[[i]])) {\n"
    "        node$left <- .atlas_new_node(arr[[i]])\n"
    "        queue[[length(queue) + 1]] <- node$left\n"
    "      }\n"
    "      i <- i + 1\n"
    "    }\n"
    "    if (i <= n) {\n"
    "      if (!is.null(arr[[i]])) {\n"
    "        node$right <- .atlas_new_node(arr[[i]])\n"
    "        queue[[length(queue) + 1]] <- node$right\n"
    "      }\n"
    "      i <- i + 1\n"
    "    }\n"
    "  }\n"
    "  root\n"
    "}\n"
    ".atlas_serialize_tree <- function(root) {\n"
    "  out <- list()\n"
    "  if (is.null(root)) return(out)\n"
    "  out[[length(out) + 1]] <- root$val\n"
    "  queue <- list(root)\n"
    "  qi <- 1\n"
    "  while (qi <= length(queue)) {\n"
    "    node <- queue[[qi]]\n"
    "    qi <- qi + 1\n"
    "    for (child in list(node$left, node$right)) {\n"
    "      if (is.null(child)) { out[[length(out) + 1]] <- NA }\n"
    "      else { out[[length(out) + 1]] <- child$val; queue[[length(queue) + 1]] <- child }\n"
    "    }\n"
    "  }\n"
    "  while (length(out) > 0 && (is.na(out[[length(out)]])[1])) out[[length(out)]] <- NULL\n"
    "  out\n"
    "}\n"
)


def _r_squote(s: str) -> str:
    """R single-quoted string literal -- like every other adapter's
    equivalent (Perl/Ruby/PHP), used defensively for JSON test DATA, not
    just fixed sentinel constants."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _r_encode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    """An R expression that makes `value_expr` serialize correctly for
    `spec`'s declared shape via `toJSON(..., auto_unbox = TRUE)`.

    A real, found-through-reasoning-then-confirmed bug this closes:
    jsonlite's `auto_unbox` decides array-vs-scalar PURELY from length,
    with no notion of a declared type -- a genuinely array-typed result
    that happens to have exactly one element (`bubble-sort` on a 1-element
    input, `array<int>` of length 1) collapses to a bare JSON scalar
    (`42` instead of `[42]`) UNLESS wrapped in `I()` (jsonlite's "AsIs"
    marker, confirmed experimentally to force array output regardless of
    length) -- and confirmed separately that this has to be applied AT
    EVERY NESTING LEVEL, not just the outermost: a length-1 ROW inside an
    otherwise-multi-row matrix collapses the same way if only the outer
    list is `I()`-wrapped. Scalar-kind LEAVES are deliberately left
    unwrapped (a real scalar-typed return, e.g. `maximum-subarray`, must
    stay a bare number, not become `[5]`)."""
    if spec.kind in ("integer", "float", "boolean", "string"):
        return value_expr
    if spec.kind == "tree":
        # __atlas_serialize_tree always builds its output via `out[[i]] <-`
        # (a genuine R list, not `c()`), and jsonlite already serializes
        # length-1 LISTS as single-element arrays correctly without I() --
        # confirmed separately from the atomic-vector case above.
        return f".atlas_serialize_tree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None
        # `.v0` not `__v0` -- R identifiers can't start with an underscore
        # (same real syntax constraint the module docstring already flags).
        inner = _r_encode_expr(spec.items, f".v{_depth}", _depth + 1)
        return f"(if (is.null({value_expr})) NULL else (function(.v{_depth}) {inner})({value_expr}))"
    if spec.kind == "array":
        assert spec.items is not None
        item_encode = _r_encode_expr(spec.items, f".e{_depth}", _depth + 1)
        return f"I(lapply({value_expr}, function(.e{_depth}) {item_encode}))"
    if spec.kind == "tuple":
        assert spec.elements is not None
        parts = [_r_encode_expr(e, f"({value_expr})[[{i + 1}]]", _depth + 1) for i, e in enumerate(spec.elements)]
        return f"I(list({', '.join(parts)}))"
    return value_expr


@dataclass(frozen=True)
class RFunctionAdapter:
    """
    Same driver contract as the other interpreted adapters (missing
    function -> Function Contract Error, a genuine bug inside the user's
    function -> uncaught `stop()`/error -> real Runtime Error via the
    subprocess's nonzero exit code, sentinel-delimited JSON result) --
    R-specific calling convention:

    - Positional arguments in the contract's declared parameter order,
      same rationale as every other interpreted adapter here.
    - Missing-function detection via `exists('name', mode='function')`.
    - No arity check emitted: R raises a real error ("argument ... is
      missing, with no default" / "unused argument") for a genuine arity
      mismatch, the same "language already reports this honestly" pattern
      as Ruby/Perl/PHP's adapters.
    - `mutates_argument` contracts use the call's RETURN VALUE, not a
      re-read of the original argument -- see the module-level docstring
      above for why (R has no mutable-reference function parameters).
    - Internal driver variables are dot-prefixed (`.atlas_args`, not
      `__atlas_args`) -- see the module-level docstring for why (R
      identifiers can't start with an underscore).
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(contract.parameter_names)
        return f"{contract.function_name} <- function({params}) {{\n\n}}\n"

    _DRIVER_TEMPLATE = (
        "suppressMessages(library(jsonlite))\n\n"
        "%(tree_helpers)s"
        ".atlas_args <- fromJSON(%(args_literal)s, simplifyVector = FALSE)\n"
        "%(tree_conversions)s"
        "if (!exists(%(fn_name_quoted)s, mode = 'function')) {\n"
        "  cat(paste0(%(contract_sentinel)s, toJSON(list(reason = 'missing_function', message = %(missing_msg)s), auto_unbox = TRUE)), '\\n')\n"
        "  quit(status = 0)\n"
        "}\n"
        "%(arg_decls)s"
        ".atlas_fn <- get(%(fn_name_quoted)s, mode = 'function')\n"
        ".atlas_result <- do.call(.atlas_fn, list(%(call_args)s))\n"
        ".atlas_out <- %(result_expr)s\n"
        "cat(paste0(%(result_sentinel)s, toJSON(.atlas_out, auto_unbox = TRUE)), '\\n')\n"
    )

    def compose_source(self, user_code: str, contract: FunctionContract, arguments: dict[str, Any]) -> str:
        uses_tree = _contract_uses_tree(contract)
        tree_params = [p.name for p in contract.parameters if p.type.kind == "tree"]
        tree_conversions = "".join(
            f".atlas_args[[{json.dumps(name)}]] <- .atlas_build_tree(.atlas_args[[{json.dumps(name)}]])\n"
            for name in tree_params
        )

        arg_decls = "".join(
            f".atlas_arg{idx} <- .atlas_args[[{json.dumps(p.name)}]]\n"
            for idx, p in enumerate(contract.parameters)
        )
        call_args = ", ".join(f".atlas_arg{idx}" for idx in range(len(contract.parameters)))

        if contract.mutates_argument is not None:
            # R has no mutable-reference call semantics -- use the
            # function's own return value (see class docstring).
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            result_expr = _r_encode_expr(contract.parameters[mutated_idx].type, ".atlas_result")
        else:
            result_expr = _r_encode_expr(contract.return_type, ".atlas_result")

        driver = self._DRIVER_TEMPLATE % {
            "tree_helpers": _TREE_HELPERS_R if uses_tree else "",
            "tree_conversions": tree_conversions,
            "args_literal": _r_squote(json.dumps(arguments)),
            "fn_name_quoted": _r_squote(contract.function_name),  # trusted, server-authored identifier
            "arg_decls": arg_decls,
            "call_args": call_args,
            "missing_msg": _r_squote(f"Required function '{contract.function_name}' was not found."),
            "contract_sentinel": _r_squote(CONTRACT_ERROR_SENTINEL),
            "result_sentinel": _r_squote(RESULT_SENTINEL),
            "result_expr": result_expr,
        }
        return f"{user_code}\n\n{driver}"
