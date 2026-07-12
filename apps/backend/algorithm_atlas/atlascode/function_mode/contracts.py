"""
Bounded type system + function contract schema for Function Mode.

Only the primitive/compound kinds actually required by migrated problems are
implemented (see Phase 4's "audit actual problem requirements" -- no
speculative types). A matrix is just `array<array<integer>>`; there is no
separate "matrix" kind because that would be a duplicate representation of
the same structural information.

Types are stored as plain JSON-serializable dicts (the Problem.function_contract
and TestCase.function_args/function_expected columns are JSON columns), with
thin dataclasses layered on top for validation/comparison convenience.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

TypeKind = Literal["integer", "float", "boolean", "string", "array", "optional", "tree", "tuple"]

_SCALAR_KINDS = {"integer", "float", "boolean", "string"}

# "tree" was added for the 18 tree-category problems (Phase 2: "only add
# types proven necessary by real problems" -- audited via
# scripts/infer_atlascode_contracts.py, not speculative). Its canonical wire
# representation is IDENTICAL to array<optional<items>>: a BFS-order level
# list with `null` for missing children, trailing-null-trimmed -- the exact
# same format the repo's Program Mode stdin parsing/serialization already
# uses (see docs/atlascode-dual-mode-resume.md's "tree serialization format"
# carry-forward note). The only reason it is a distinct TypeKind rather than
# reusing "array" is semantic, not structural: a Function Mode driver must
# know to reconstruct an actual Node object graph from this array before
# calling the user's function (or serialize one back to this array for a
# tree-typed return), whereas a plain array is passed through as-is.

# "tuple" was added to unquarantine min-stack-simulation (mission Phase 6):
# a FIXED-WIDTH, per-position-heterogeneous record, e.g. one stack operation
# `(command: string, value: integer | None)`. This is genuinely different
# from "array": an array's `items` is ONE type shared by every element; a
# tuple's `elements` is an ORDERED LIST of per-position types that do not
# have to agree with each other. On the wire it is just a JSON array of the
# declared width -- there is no separate transport format, only a different
# validation/comparison rule (position-by-position, not homogeneous).


class ContractError(Exception):
    """Raised for a structural mismatch between a contract and real data --
    e.g. a custom case's argument doesn't match its declared type. Distinct
    from the runtime 'Function Contract Error' verdict (missing function,
    wrong return type at execution time), though both stem from the same
    underlying contract."""


@dataclass(frozen=True)
class TypeSpec:
    kind: TypeKind
    items: "TypeSpec | None" = None  # required for kind in {"array", "optional", "tree"}
    # Only meaningful for kind == "array". None = default positional/ordered
    # comparison. "sorted" = compare_typed sorts both sides before comparing
    # -- for genuinely order-insensitive fixed-shape returns (e.g. two-sum's
    # index pair, where Program Mode's own reference driver prints
    # `min(i,j), max(i,j)` because either index order is a valid answer).
    # Discovered as real, necessary evidence during bulk contract inference
    # (scripts/migrate_atlascode_function_mode.py), not spec'd in advance.
    comparator: str | None = None
    # Required for kind == "tuple" ONLY: the ordered, per-position types of a
    # fixed-width heterogeneous record (e.g. one min-stack operation). Kept as
    # a separate field rather than overloading `items` so every existing
    # array/optional/tree TypeSpec construction site (dozens across
    # adapters.py/compiled_adapters.py) stays completely unaffected.
    elements: "tuple[TypeSpec, ...] | None" = None

    def to_dict(self) -> dict:
        d: dict[str, Any] = {"kind": self.kind}
        if self.items is not None:
            d["items"] = self.items.to_dict()
        if self.comparator is not None:
            d["comparator"] = self.comparator
        if self.elements is not None:
            d["elements"] = [e.to_dict() for e in self.elements]
        return d

    @staticmethod
    def from_dict(d: dict) -> "TypeSpec":
        kind = d["kind"]
        items = TypeSpec.from_dict(d["items"]) if d.get("items") is not None else None
        if kind in ("array", "optional", "tree") and items is None:
            raise ContractError(f"TypeSpec kind='{kind}' requires 'items'")
        elements = None
        if kind == "tuple":
            raw_elements = d.get("elements")
            if not raw_elements:
                raise ContractError("TypeSpec kind='tuple' requires non-empty 'elements'")
            elements = tuple(TypeSpec.from_dict(e) for e in raw_elements)
        return TypeSpec(kind=kind, items=items, comparator=d.get("comparator"), elements=elements)


@dataclass(frozen=True)
class Parameter:
    name: str
    type: TypeSpec

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type.to_dict()}

    @staticmethod
    def from_dict(d: dict) -> "Parameter":
        return Parameter(name=d["name"], type=TypeSpec.from_dict(d["type"]))


@dataclass(frozen=True)
class FunctionContract:
    function_name: str
    parameters: list[Parameter]
    return_type: TypeSpec
    # Set for in-place-mutation problems (e.g. the 21 sorting-algorithm
    # problems: `bubble_sort(arr)` mutates `arr` and returns nothing --
    # Program Mode's own driver prints the CALLER's now-mutated variable, not
    # a return value). When set, a Function Mode driver must read back this
    # parameter's post-call value instead of the function's return value.
    # Discovered as real, necessary evidence during bulk contract inference
    # (scripts/migrate_atlascode_function_mode.py) -- None for every problem
    # that returns a normal value.
    mutates_argument: str | None = None

    def to_dict(self) -> dict:
        d = {
            "function_name": self.function_name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type.to_dict(),
        }
        if self.mutates_argument is not None:
            d["mutates_argument"] = self.mutates_argument
        return d

    @staticmethod
    def from_dict(d: dict) -> "FunctionContract":
        return FunctionContract(
            function_name=d["function_name"],
            parameters=[Parameter.from_dict(p) for p in d["parameters"]],
            return_type=TypeSpec.from_dict(d["return_type"]),
            mutates_argument=d.get("mutates_argument"),
        )

    @property
    def parameter_names(self) -> list[str]:
        return [p.name for p in self.parameters]


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_value(value: Any, spec: TypeSpec) -> bool:
    """Structural type check -- used to reject malformed custom Function Mode
    cases BEFORE execution (Phase 14: never execute a malformed custom case)."""
    if spec.kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if spec.kind == "float":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if spec.kind == "boolean":
        return isinstance(value, bool)
    if spec.kind == "string":
        return isinstance(value, str)
    if spec.kind == "optional":
        assert spec.items is not None
        return value is None or validate_value(value, spec.items)
    if spec.kind == "array":
        assert spec.items is not None
        return isinstance(value, list) and all(validate_value(v, spec.items) for v in value)
    if spec.kind == "tree":
        assert spec.items is not None
        return isinstance(value, list) and all(
            v is None or validate_value(v, spec.items) for v in value
        )
    if spec.kind == "tuple":
        assert spec.elements is not None
        if not isinstance(value, list) or len(value) != len(spec.elements):
            return False
        return all(validate_value(v, e) for v, e in zip(value, spec.elements))
    return False


def validate_arguments(args: dict[str, Any], contract: FunctionContract) -> list[str]:
    """Returns a list of human-readable errors; empty list means valid.
    Checks parameter names match exactly (no missing, no unexpected) and every
    value matches its declared type -- Phase 14's "reject wrong parameter
    names / wrong types / invalid nested structures"."""
    errors: list[str] = []
    expected_names = set(contract.parameter_names)
    given_names = set(args.keys())

    for missing in expected_names - given_names:
        errors.append(f"Missing argument '{missing}'")
    for extra in given_names - expected_names:
        errors.append(f"Unexpected argument '{extra}'")

    for p in contract.parameters:
        if p.name not in args:
            continue
        if not validate_value(args[p.name], p.type):
            errors.append(f"Argument '{p.name}' does not match declared type '{p.type.kind}'")
    return errors


# ── Comparison ─────────────────────────────────────────────────────────────────

_FLOAT_TOL = 1e-6


def compare_typed(actual: Any, expected: Any, spec: TypeSpec) -> bool:
    """Semantic comparison per Phase 11: exact equality for integer/boolean/
    string, explicit tolerance for float, ORDERED structural equality for
    arrays (never silently sorted -- order only doesn't matter when the
    problem contract says so, which isn't modeled here because none of the
    migrated problems need it yet)."""
    if spec.kind == "float":
        try:
            return abs(float(actual) - float(expected)) <= _FLOAT_TOL
        except (TypeError, ValueError):
            return False
    if spec.kind == "optional":
        assert spec.items is not None
        if actual is None or expected is None:
            return actual is expected
        return compare_typed(actual, expected, spec.items)
    if spec.kind == "array":
        assert spec.items is not None
        if not isinstance(actual, list) or not isinstance(expected, list):
            return False
        if len(actual) != len(expected):
            return False
        a_cmp, e_cmp = actual, expected
        if spec.comparator == "sorted":
            try:
                a_cmp, e_cmp = sorted(actual), sorted(expected)
            except TypeError:
                return False
        return all(compare_typed(a, e, spec.items) for a, e in zip(a_cmp, e_cmp))
    if spec.kind == "tree":
        # Same ordered structural comparison as "array", element-wise
        # None-aware (a tree's BFS array can contain `null` gaps) -- both
        # sides are expected to already be trailing-null-trimmed by whatever
        # produced them (matching the repo's existing serialize() behavior),
        # so no re-trimming happens here.
        assert spec.items is not None
        if not isinstance(actual, list) or not isinstance(expected, list):
            return False
        if len(actual) != len(expected):
            return False
        return all(
            (a is None and e is None) or (a is not None and e is not None and compare_typed(a, e, spec.items))
            for a, e in zip(actual, expected)
        )
    if spec.kind == "tuple":
        # Position-by-position comparison against each element's OWN type --
        # never sorted (a tuple's positions are not interchangeable the way
        # a "sorted"-comparator array's elements can be).
        assert spec.elements is not None
        if not isinstance(actual, list) or not isinstance(expected, list):
            return False
        if len(actual) != len(expected) or len(actual) != len(spec.elements):
            return False
        return all(compare_typed(a, e, t) for a, e, t in zip(actual, expected, spec.elements))
    # integer / boolean / string: exact equality
    return actual == expected
