"""
Function Mode adapters for COMPILED languages (Phase 7/29 of the dual-mode
completion pass). These are structurally different from the interpreted
adapters in adapters.py:

  - `FunctionModeAdapter` (interpreted): `compose_source(user_code, contract,
    arguments)` embeds ONE case's arguments directly into the source text --
    fine when composing+running full source per case is cheap, but for a
    compiled language that means recompiling from scratch per test case
    (40 compiles/submission -- unacceptable, see runner.py's old docstring).

  - `CompiledFunctionModeAdapter` (this module): `compose_program(user_code,
    contract)` takes NO arguments and returns ONE program that reads its
    case's arguments from STDIN at runtime (JSON on one line) and prints the
    sentinel-prefixed JSON result to stdout -- exactly Program Mode's own
    stdin/stdout convention. This lets runner.py reuse notebook.py's existing
    PREPARERS/_run_prepared compile-once infrastructure UNCHANGED: compile
    the driver ONCE, then invoke the same compiled artifact once per case
    with different stdin, never recompiling. This is the same mechanism
    Program Mode's submission/evaluator.py already relies on for cpp/c/java/
    rust/kotlin -- proven, not new infrastructure.

Since compiled languages are statically typed, a missing/renamed required
method or wrong parameter types is a COMPILE ERROR (caught by javac itself),
not a runtime sentinel -- runner.py surfaces that as verdict="Compilation
Error", never silently as a generic Runtime Error.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from .contracts import FunctionContract, TypeSpec
from .protocol import CONTRACT_ERROR_SENTINEL, RESULT_SENTINEL


class CompiledFunctionModeAdapter(Protocol):
    def generate_starter(self, contract: FunctionContract) -> str: ...
    def compose_program(self, user_code: str, contract: FunctionContract) -> str: ...


# ── Java ─────────────────────────────────────────────────────────────────────

def _java_scalar_type(kind: str) -> str:
    return {"integer": "int", "float": "double", "boolean": "boolean", "string": "String"}[kind]


def _java_boxed_type(kind: str) -> str:
    return {"integer": "Integer", "float": "Double", "boolean": "Boolean", "string": "String"}[kind]


def _java_type(spec: TypeSpec) -> str:
    """Java type name for a contract TypeSpec -- bounded to the exact shapes
    actually present in the migrated 216-problem corpus (audited via
    docs/atlascode-contracts-inferred.json): scalars, 1-3D arrays of
    int/string/double, tree<integer>, and optional<T> (boxed)."""
    if spec.kind in ("integer", "float", "boolean", "string"):
        return _java_scalar_type(spec.kind)
    if spec.kind == "optional":
        assert spec.items is not None
        if spec.items.kind in ("integer", "float", "boolean", "string"):
            return _java_boxed_type(spec.items.kind)
        return _java_type(spec.items)  # optional<array<...>> -- null already representable
    if spec.kind == "array":
        assert spec.items is not None
        return f"{_java_type(spec.items)}[]"
    if spec.kind == "tree":
        return "TreeNode"
    if spec.kind == "tuple":
        # No native Java tuple -- a fixed-width heterogeneous record is
        # represented as a boxed Object[] (each slot already the correct
        # boxed type: Long/Double/Boolean/String/null), the same
        # already-JSON-serializable shape __atlas.write's `instanceof
        # Object[]` branch handles generically. This mirrors min-stack's
        # ONLY current tuple use (a stack op record); a future tuple with
        # nested array/tree elements would still decode correctly since
        # _java_decode_expr recurses per-position, but is not exercised by
        # today's corpus.
        return "Object[]"
    raise ValueError(f"unsupported TypeSpec for Java: {spec}")


def _java_decode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    """A Java expression that decodes a parsed-JSON `Object` (`value_expr`)
    into the concrete typed value `_java_type(spec)` describes.

    `_depth` only exists to keep generated lambda parameter names unique when
    an array-of-tuple decode (the `Object[]` stream branch below) is nested
    inside another one -- not exercised by today's corpus (only one level of
    array<tuple<...>> exists, min-stack-simulation's `ops`), but cheap to get
    right rather than leaving a latent name-collision bug for the next
    tuple-shaped problem."""
    if spec.kind == "integer":
        return f"((Number) {value_expr}).intValue()"
    if spec.kind == "float":
        return f"((Number) {value_expr}).doubleValue()"
    if spec.kind == "boolean":
        return f"((Boolean) {value_expr})"
    if spec.kind == "string":
        return f"((String) {value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None
        inner = _java_decode_expr(spec.items, value_expr, _depth)
        return f"({value_expr} == null ? null : {inner})"
    if spec.kind == "tree":
        return f"__atlas.buildTree({value_expr})"
    if spec.kind == "tuple":
        assert spec.elements is not None
        parts = [
            _java_decode_expr(elem, f"((java.util.List<Object>) ({value_expr})).get({idx})", _depth)
            for idx, elem in enumerate(spec.elements)
        ]
        return "new Object[]{" + ", ".join(parts) + "}"
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        if item.kind == "integer":
            return f"__atlas.asIntArray({value_expr})"
        if item.kind == "float":
            return f"__atlas.asDoubleArray({value_expr})"
        if item.kind == "string":
            return f"__atlas.asStringArray({value_expr})"
        if item.kind == "boolean":
            return f"__atlas.asBoolArray({value_expr})"
        if item.kind == "optional" and item.items is not None and item.items.kind == "integer":
            return f"__atlas.asIntOptArray({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "integer":
            return f"__atlas.asIntArray2({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "string":
            return f"__atlas.asStringArray2({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "array" and item.items.items is not None and item.items.items.kind == "integer":
            return f"__atlas.asIntArray3({value_expr})"
        if item.kind == "tuple":
            lambda_var = f"__t{_depth}"
            inner = _java_decode_expr(item, lambda_var, _depth + 1)
            return (
                f"((java.util.List<Object>) ({value_expr})).stream()"
                f".map(({lambda_var}) -> (Object[]) ({inner}))"
                f".toArray(Object[][]::new)"
            )
        raise ValueError(f"unsupported nested array item type for Java: {item}")
    raise ValueError(f"unsupported TypeSpec for Java decode: {spec}")


def _java_encode_expr(spec: TypeSpec, value_expr: str) -> str:
    """A Java expression converting a value of type `_java_type(spec)` back
    into a JSON-encodable `Object` (Long/Double/Boolean/String/List<Object>/
    null) for __atlas.toJson()."""
    if spec.kind == "tree":
        return f"__atlas.serializeTree({value_expr})"
    # Everything else (scalars, arrays of any depth, optional) is already
    # directly representable by __atlas.toJson via reflection-free instanceof
    # checks on the boxed/array value itself.
    return value_expr


_JAVA_TREE_CLASS = (
    "class TreeNode {\n"
    "    int val;\n"
    "    TreeNode left;\n"
    "    TreeNode right;\n"
    "    TreeNode() {}\n"
    "    TreeNode(int val) { this.val = val; }\n"
    "    TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; }\n"
    "}\n\n"
)

# Shared runtime: minimal JSON parser/writer + array/tree coercion helpers.
# Bounded to exactly the type shapes the real corpus needs (see _java_type's
# docstring) -- not a general-purpose JSON library.
#
# NOTE: no `import` here -- Java requires all imports at the very top of the
# COMPILATION UNIT (before any type declaration), and since the user's
# `Solution` class is emitted first in compose_program's output, `import
# java.util.*;` is hoisted to the very top of the whole composed file
# instead (one import block covers every class in the file regardless of
# declaration order after it).
_JAVA_RUNTIME_CLASS = r'''
final class __atlas {
    // ---- minimal JSON parser: text -> Long/Double/Boolean/String/ArrayList<Object>/LinkedHashMap<String,Object>/null ----
    static final class P {
        final String s; int i = 0;
        P(String s) { this.s = s; }
        void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
        Object parse() { ws(); Object v = value(); ws(); return v; }
        Object value() {
            ws();
            char c = s.charAt(i);
            if (c == '{') return obj();
            if (c == '[') return arr();
            if (c == '"') return str();
            if (c == 't') { i += 4; return Boolean.TRUE; }
            if (c == 'f') { i += 5; return Boolean.FALSE; }
            if (c == 'n') { i += 4; return null; }
            return num();
        }
        Map<String, Object> obj() {
            LinkedHashMap<String, Object> m = new LinkedHashMap<>();
            i++; ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) {
                ws();
                String k = str();
                ws(); i++; // ':'
                Object v = value();
                m.put(k, v);
                ws();
                if (s.charAt(i) == ',') { i++; continue; }
                i++; break; // '}'
            }
            return m;
        }
        List<Object> arr() {
            ArrayList<Object> list = new ArrayList<>();
            i++; ws();
            if (s.charAt(i) == ']') { i++; return list; }
            while (true) {
                list.add(value());
                ws();
                if (s.charAt(i) == ',') { i++; continue; }
                i++; break; // ']'
            }
            return list;
        }
        String str() {
            i++; // opening quote
            StringBuilder sb = new StringBuilder();
            while (s.charAt(i) != '"') {
                char c = s.charAt(i);
                if (c == '\\') {
                    i++;
                    char e = s.charAt(i);
                    switch (e) {
                        case 'n': sb.append('\n'); break;
                        case 't': sb.append('\t'); break;
                        case 'r': sb.append('\r'); break;
                        case '"': sb.append('"'); break;
                        case '\\': sb.append('\\'); break;
                        case '/': sb.append('/'); break;
                        case 'u':
                            sb.append((char) Integer.parseInt(s.substring(i + 1, i + 5), 16));
                            i += 4;
                            break;
                        default: sb.append(e);
                    }
                } else sb.append(c);
                i++;
            }
            i++; // closing quote
            return sb.toString();
        }
        Object num() {
            int start = i;
            while (i < s.length() && (Character.isDigit(s.charAt(i)) || "+-.eE".indexOf(s.charAt(i)) >= 0)) i++;
            String t = s.substring(start, i);
            if (t.indexOf('.') >= 0 || t.indexOf('e') >= 0 || t.indexOf('E') >= 0) return Double.parseDouble(t);
            try { return Long.parseLong(t); } catch (NumberFormatException ex) { return new java.math.BigInteger(t); }
        }
    }

    static Object parseJson(String s) { return new P(s).parse(); }

    // ---- array/tree coercion (bounded to the shapes the real corpus needs) ----
    @SuppressWarnings("unchecked")
    static int[] asIntArray(Object o) {
        List<Object> l = (List<Object>) o;
        int[] out = new int[l.size()];
        for (int i = 0; i < l.size(); i++) out[i] = ((Number) l.get(i)).intValue();
        return out;
    }
    @SuppressWarnings("unchecked")
    static double[] asDoubleArray(Object o) {
        List<Object> l = (List<Object>) o;
        double[] out = new double[l.size()];
        for (int i = 0; i < l.size(); i++) out[i] = ((Number) l.get(i)).doubleValue();
        return out;
    }
    @SuppressWarnings("unchecked")
    static boolean[] asBoolArray(Object o) {
        List<Object> l = (List<Object>) o;
        boolean[] out = new boolean[l.size()];
        for (int i = 0; i < l.size(); i++) out[i] = (Boolean) l.get(i);
        return out;
    }
    @SuppressWarnings("unchecked")
    static String[] asStringArray(Object o) {
        List<Object> l = (List<Object>) o;
        String[] out = new String[l.size()];
        for (int i = 0; i < l.size(); i++) out[i] = (String) l.get(i);
        return out;
    }
    @SuppressWarnings("unchecked")
    static Integer[] asIntOptArray(Object o) {
        List<Object> l = (List<Object>) o;
        Integer[] out = new Integer[l.size()];
        for (int i = 0; i < l.size(); i++) { Object v = l.get(i); out[i] = v == null ? null : ((Number) v).intValue(); }
        return out;
    }
    @SuppressWarnings("unchecked")
    static int[][] asIntArray2(Object o) {
        List<Object> l = (List<Object>) o;
        int[][] out = new int[l.size()][];
        for (int i = 0; i < l.size(); i++) out[i] = asIntArray(l.get(i));
        return out;
    }
    @SuppressWarnings("unchecked")
    static String[][] asStringArray2(Object o) {
        List<Object> l = (List<Object>) o;
        String[][] out = new String[l.size()][];
        for (int i = 0; i < l.size(); i++) out[i] = asStringArray(l.get(i));
        return out;
    }
    @SuppressWarnings("unchecked")
    static int[][][] asIntArray3(Object o) {
        List<Object> l = (List<Object>) o;
        int[][][] out = new int[l.size()][][];
        for (int i = 0; i < l.size(); i++) out[i] = asIntArray2(l.get(i));
        return out;
    }

    @SuppressWarnings("unchecked")
    static TreeNode buildTree(Object o) {
        List<Object> arr = (List<Object>) o;
        if (arr.isEmpty() || arr.get(0) == null) return null;
        TreeNode root = new TreeNode(((Number) arr.get(0)).intValue());
        ArrayDeque<TreeNode> queue = new ArrayDeque<>();
        queue.add(root);
        int i = 1;
        while (!queue.isEmpty() && i < arr.size()) {
            TreeNode node = queue.poll();
            if (i < arr.size()) {
                Object v = arr.get(i);
                if (v != null) { node.left = new TreeNode(((Number) v).intValue()); queue.add(node.left); }
                i++;
            }
            if (i < arr.size()) {
                Object v = arr.get(i);
                if (v != null) { node.right = new TreeNode(((Number) v).intValue()); queue.add(node.right); }
                i++;
            }
        }
        return root;
    }

    static List<Object> serializeTree(TreeNode root) {
        ArrayList<Object> out = new ArrayList<>();
        if (root == null) return out;
        out.add((long) root.val);
        ArrayDeque<TreeNode> queue = new ArrayDeque<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            TreeNode[] children = { node.left, node.right };
            for (TreeNode child : children) {
                if (child == null) out.add(null);
                else { out.add((long) child.val); queue.add(child); }
            }
        }
        while (!out.isEmpty() && out.get(out.size() - 1) == null) out.remove(out.size() - 1);
        return out;
    }

    // ---- JSON writer: Object (any of the above, plus native arrays) -> JSON text ----
    static String toJson(Object o) {
        StringBuilder sb = new StringBuilder();
        write(o, sb);
        return sb.toString();
    }
    static void write(Object o, StringBuilder sb) {
        if (o == null) { sb.append("null"); return; }
        if (o instanceof Boolean) { sb.append(((Boolean) o) ? "true" : "false"); return; }
        if (o instanceof String) { writeString((String) o, sb); return; }
        if (o instanceof Double || o instanceof Float) { sb.append(o.toString()); return; }
        if (o instanceof Number) { sb.append(o.toString()); return; }
        if (o instanceof int[]) {
            int[] a = (int[]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(a[i]); }
            sb.append(']'); return;
        }
        if (o instanceof double[]) {
            double[] a = (double[]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(a[i]); }
            sb.append(']'); return;
        }
        if (o instanceof boolean[]) {
            boolean[] a = (boolean[]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(a[i]); }
            sb.append(']'); return;
        }
        // NOTE ordering: int[][] and int[][][] are BOTH `instanceof Object[]`
        // (an array of a reference/array type is always Object[]-compatible
        // in Java, even though int[] itself isn't) -- these specific checks
        // MUST come before the generic `instanceof Object[]` catch-all below
        // or a 2D/3D int array would be misrouted into it.
        if (o instanceof int[][][]) {
            int[][][] a = (int[][][]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); write(a[i], sb); }
            sb.append(']'); return;
        }
        if (o instanceof int[][]) {
            int[][] a = (int[][]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); write(a[i], sb); }
            sb.append(']'); return;
        }
        if (o instanceof Object[]) {
            Object[] a = (Object[]) o; sb.append('[');
            for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); write(a[i], sb); }
            sb.append(']'); return;
        }
        if (o instanceof List) {
            List<?> l = (List<?>) o; sb.append('[');
            for (int i = 0; i < l.size(); i++) { if (i > 0) sb.append(','); write(l.get(i), sb); }
            sb.append(']'); return;
        }
        throw new RuntimeException("__atlas.toJson: unsupported result type " + o.getClass());
    }
    static void writeString(String s, StringBuilder sb) {
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
            }
        }
        sb.append('"');
    }
}
'''


@dataclass(frozen=True)
class JavaFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: the user writes
    `class Solution { public <ReturnType> <function_name>(<params>) { ... } }`
    (LeetCode's exact convention -- familiar, and Java requires SOME class
    structure since it has no bare top-level functions). `Solution` is
    intentionally NOT `public` so it can share a file with the driver's
    `public class Main` (the class name notebook.py's `_wrap_java_source`/
    `_prepare_java` already expects) with no filename-vs-public-class
    conflict.

    Missing method / wrong parameter types are Java COMPILE ERRORS (caught by
    javac before the driver ever runs) -- runner.py surfaces this as
    verdict="Compilation Error", the correct distinct category for a
    statically-typed language, not a runtime Function Contract Error.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{_java_type(p.type)} {p.name}" for p in contract.parameters)
        # Mutation-style contracts (the 21 in-place-sort problems) declare
        # `void`, not the mutated argument's own type -- Java, unlike Python,
        # is statically typed and would FORCE a return statement from a
        # non-void method even though the driver never looks at it (it reads
        # the post-call mutated argument instead, exactly like Program
        # Mode's own reference driver). `void` is also the idiomatic Java
        # signature for "sort this array in place" regardless.
        if contract.mutates_argument is not None:
            return_type = "void"
            body = ""
        else:
            return_type = _java_type(contract.return_type)
            body = f"        return {_java_default_return(contract.return_type)};\n"
        # TreeNode is only emitted in the visible starter when actually
        # needed -- unlike compose_program's driver, which always includes
        # it unconditionally since __atlas's shared runtime references it
        # regardless of whether THIS problem's contract uses tree types.
        tree_prefix = _JAVA_TREE_CLASS if _uses_tree(contract) else ""
        return (
            f"{tree_prefix}"
            f"class Solution {{\n"
            f"    public {return_type} {contract.function_name}({params}) {{\n"
            f"{body}"
            f"    }}\n"
            f"}}\n"
        )

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        params_decl = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"__arg{idx}"
            decode = _java_decode_expr(p.type, f"__args.get({idx})")
            params_decl.append(f"        {_java_type(p.type)} {var} = {decode};")
            call_args.append(var)

        raw_call = f"new Solution().{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            result_java_expr = f"__arg{mutated_idx}"
        else:
            result_java_expr = raw_call

        # For a mutates_argument contract, the function must still actually
        # be INVOKED (for its in-place side effect on the argument array) --
        # only its return value is discarded, never the call itself.
        call_statement = f"        {raw_call};\n" if contract.mutates_argument is not None else ""

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"__atlas.serializeTree({result_java_expr})"
        else:
            json_ready_expr = result_java_expr

        # The shared __atlas runtime class's buildTree/serializeTree methods
        # reference TreeNode unconditionally, so SOMETHING must define it --
        # but generate_starter ALREADY includes it for tree contracts, and a
        # real submission naturally keeps whatever's in the starter it was
        # given. Defining it a second time here would be a duplicate-class
        # compile error on every genuine tree-problem submission (caught by
        # this session's own compile-sanity sweep: 18/18 tree problems
        # failed exactly this way before this check existed). Only add it if
        # the user's code doesn't already declare it.
        tree_prefix = "" if "class TreeNode" in user_code else _JAVA_TREE_CLASS
        order_java_literal = "{" + ", ".join(json.dumps(n) for n in contract.parameter_names) + "}"

        driver = f'''
{_JAVA_RUNTIME_CLASS}

public class Main {{
    public static void main(String[] args) throws Exception {{
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder inputSb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) inputSb.append(line).append('\\n');
        Object parsed = __atlas.parseJson(inputSb.toString());
        @SuppressWarnings("unchecked")
        java.util.Map<String, Object> __argsMap = (java.util.Map<String, Object>) parsed;
        String[] __order = {order_java_literal};
        java.util.List<Object> __args = new java.util.ArrayList<>();
        for (String k : __order) __args.add(__argsMap.get(k));

{chr(10).join(params_decl)}

{call_statement}        Object __result = {json_ready_expr};
        System.out.println("{RESULT_SENTINEL}" + __atlas.toJson(__result));
    }}
}}
'''
        # `import` must be the first thing in the compilation unit (Java
        # forbids it after any class declaration), so it goes before
        # EVERYTHING, including the user's own Solution class.
        return f"import java.util.*;\n\n{tree_prefix}{user_code}\n\n{driver}"


def _uses_tree(contract: FunctionContract) -> bool:
    specs = [p.type for p in contract.parameters] + [contract.return_type]
    return any(s.kind == "tree" for s in specs)


def _java_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind in ("array", "optional", "tree"):
        return "null"
    return "null"


# ── C++ ──────────────────────────────────────────────────────────────────────
# Second compiled adapter -- proves the compile-once architecture generalizes
# beyond Java, not just a one-off. Simpler than Java on the OUTPUT side: C++
# has no reflection, but it also doesn't need any -- the return type is known
# at codegen time, so the driver emits a DIRECT typed printer for that exact
# shape instead of a generic Object->JSON writer. The INPUT side still needs
# a small generic JSON value type (JVal) since args arrive as one opaque
# JSON blob on stdin.

def _cpp_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "int"
    if spec.kind == "float":
        return "double"
    if spec.kind == "boolean":
        return "bool"
    if spec.kind == "string":
        return "std::string"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"std::optional<{_cpp_type(spec.items)}>"
    if spec.kind == "array":
        assert spec.items is not None
        return f"std::vector<{_cpp_type(spec.items)}>"
    if spec.kind == "tree":
        return "TreeNode*"
    if spec.kind == "tuple":
        # std::tuple is a NATIVE fit here (unlike Java's boxed Object[]
        # workaround) -- C++ has real fixed-width heterogeneous product
        # types, so no generated wrapper class is needed at all.
        assert spec.elements is not None
        return f"std::tuple<{', '.join(_cpp_type(e) for e in spec.elements)}>"
    raise ValueError(f"unsupported TypeSpec for C++: {spec}")


def _cpp_decode_expr(spec: TypeSpec, value_expr: str) -> str:
    if spec.kind == "integer":
        return f"__atlas::asInt({value_expr})"
    if spec.kind == "float":
        return f"__atlas::asDouble({value_expr})"
    if spec.kind == "boolean":
        return f"__atlas::asBool({value_expr})"
    if spec.kind == "string":
        return f"__atlas::asStr({value_expr})"
    if spec.kind == "tree":
        return f"__atlas::buildTree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"__atlas::asOpt<{_cpp_type(spec.items)}>({value_expr})"
    if spec.kind == "tuple":
        # `value_expr` is a `const JVal&` whose own `.arr` holds the
        # per-position values (JVal's array storage doubles as both a JSON
        # array and this fixed-width record -- on the wire a tuple IS just a
        # JSON array, see contracts.py's TypeSpec docstring).
        assert spec.elements is not None
        parts = [_cpp_decode_expr(e, f"({value_expr}).arr[{i}]") for i, e in enumerate(spec.elements)]
        return f"std::make_tuple({', '.join(parts)})"
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        if item.kind == "integer":
            return f"__atlas::asIntVec({value_expr})"
        if item.kind == "float":
            return f"__atlas::asDoubleVec({value_expr})"
        if item.kind == "string":
            return f"__atlas::asStrVec({value_expr})"
        if item.kind == "boolean":
            return f"__atlas::asBoolVec({value_expr})"
        if item.kind == "optional" and item.items is not None and item.items.kind == "integer":
            return f"__atlas::asIntOptVec({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "integer":
            return f"__atlas::asIntMatrix({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "string":
            return f"__atlas::asStrMatrix({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "array" and item.items.items is not None and item.items.items.kind == "integer":
            return f"__atlas::asIntCube({value_expr})"
        if item.kind == "tuple":
            # No pre-generated vector<tuple<...>> overload exists (unlike the
            # concrete vec/matrix/cube helpers above) since the tuple's own
            # element shape isn't known until codegen time -- an inline IIFE
            # lambda does the same loop-and-collect a named helper would,
            # without needing one generated C++ function per tuple shape.
            item_cpp_type = _cpp_type(item)
            inner = _cpp_decode_expr(item, "__e")
            return (
                f"[&]{{ std::vector<{item_cpp_type}> __out; "
                f"for (auto &__e : ({value_expr}).arr) __out.push_back({inner}); "
                f"return __out; }}()"
            )
        raise ValueError(f"unsupported nested array item type for C++: {item}")
    raise ValueError(f"unsupported TypeSpec for C++ decode: {spec}")


def _cpp_print_stmt(spec: TypeSpec, value_expr: str) -> str:
    """A complete C++ statement printing the sentinel + JSON-encoded value."""
    if spec.kind == "tree":
        return f'std::cout << "{RESULT_SENTINEL}" << __atlas::treeToJson({value_expr}) << std::endl;'
    if spec.kind in ("integer", "float", "boolean", "string"):
        return f'std::cout << "{RESULT_SENTINEL}" << __atlas::scalarToJson({value_expr}) << std::endl;'
    if spec.kind == "array":
        return f'std::cout << "{RESULT_SENTINEL}" << __atlas::arrToJson({value_expr}) << std::endl;'
    raise ValueError(f"unsupported TypeSpec for C++ print: {spec}")


_CPP_TREE_STRUCT = (
    "struct TreeNode {\n"
    "    int val;\n"
    "    TreeNode *left;\n"
    "    TreeNode *right;\n"
    "    TreeNode() : val(0), left(nullptr), right(nullptr) {}\n"
    "    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}\n"
    "    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}\n"
    "};\n\n"
)

# Shared runtime: minimal JSON value type + parser + typed coercion/printing
# helpers. Bounded to exactly the shapes the real corpus needs (see
# _cpp_type's callers) -- not a general-purpose JSON library. Placed in a
# `__atlas` namespace so it can never collide with a user's own identifiers.
_CPP_RUNTIME = r'''
namespace __atlas {

struct JVal {
    enum Kind { NUL, BOOLEAN, NUM, STR, ARR } kind = NUL;
    bool b = false;
    double num = 0;
    std::string str;
    std::vector<JVal> arr;
};

struct JParser {
    const std::string &s;
    size_t i = 0;
    explicit JParser(const std::string &s_) : s(s_) {}
    void ws() { while (i < s.size() && std::isspace((unsigned char) s[i])) i++; }
    JVal parse() { ws(); JVal v = value(); return v; }
    JVal value() {
        ws();
        char c = s[i];
        if (c == '{') return object();
        if (c == '[') return array();
        if (c == '"') { JVal v; v.kind = JVal::STR; v.str = str(); return v; }
        if (c == 't') { i += 4; JVal v; v.kind = JVal::BOOLEAN; v.b = true; return v; }
        if (c == 'f') { i += 5; JVal v; v.kind = JVal::BOOLEAN; v.b = false; return v; }
        if (c == 'n') { i += 4; JVal v; v.kind = JVal::NUL; return v; }
        return number();
    }
    JVal object() {
        JVal v; v.kind = JVal::ARR;  // objects are only ever the top-level args map; store as parallel arrays
        std::vector<std::string> keys;
        i++; ws();
        if (s[i] == '}') { i++; obj_keys = keys; return v; }
        while (true) {
            ws();
            std::string k = str();
            ws(); i++;  // ':'
            JVal val = value();
            keys.push_back(k);
            v.arr.push_back(val);
            ws();
            if (s[i] == ',') { i++; continue; }
            i++; break;  // '}'
        }
        obj_keys = keys;
        return v;
    }
    std::vector<std::string> obj_keys;
    JVal array() {
        JVal v; v.kind = JVal::ARR;
        i++; ws();
        if (s[i] == ']') { i++; return v; }
        while (true) {
            v.arr.push_back(value());
            ws();
            if (s[i] == ',') { i++; continue; }
            i++; break;
        }
        return v;
    }
    std::string str() {
        i++;
        std::string out;
        while (s[i] != '"') {
            char c = s[i];
            if (c == '\\') {
                i++;
                char e = s[i];
                switch (e) {
                    case 'n': out += '\n'; break;
                    case 't': out += '\t'; break;
                    case 'r': out += '\r'; break;
                    case '"': out += '"'; break;
                    case '\\': out += '\\'; break;
                    case '/': out += '/'; break;
                    default: out += e;
                }
            } else out += c;
            i++;
        }
        i++;
        return out;
    }
    JVal number() {
        size_t start = i;
        while (i < s.size() && (std::isdigit((unsigned char) s[i]) || std::string("+-.eE").find(s[i]) != std::string::npos)) i++;
        JVal v; v.kind = JVal::NUM; v.num = std::stod(s.substr(start, i - start));
        return v;
    }
};

inline JVal parseArgsMap(const std::string &text, std::vector<std::string> &orderOut, const std::vector<std::string> &order) {
    JParser p(text);
    JVal v = p.parse();
    orderOut = p.obj_keys;
    (void) order;
    return v;
}

inline const JVal &lookup(const JVal &argsObj, const std::vector<std::string> &keys, const std::string &name) {
    for (size_t k = 0; k < keys.size(); k++) if (keys[k] == name) return argsObj.arr[k];
    throw std::runtime_error("missing argument: " + name);
}

inline int asInt(const JVal &v) { return (int) llround(v.num); }
inline double asDouble(const JVal &v) { return v.num; }
inline bool asBool(const JVal &v) { return v.b; }
inline std::string asStr(const JVal &v) { return v.str; }

template <typename T> std::optional<T> asOpt(const JVal &v);
template <> inline std::optional<int> asOpt<int>(const JVal &v) { if (v.kind == JVal::NUL) return std::nullopt; return asInt(v); }

inline std::vector<int> asIntVec(const JVal &v) { std::vector<int> out; for (auto &e : v.arr) out.push_back(asInt(e)); return out; }
inline std::vector<double> asDoubleVec(const JVal &v) { std::vector<double> out; for (auto &e : v.arr) out.push_back(asDouble(e)); return out; }
inline std::vector<bool> asBoolVec(const JVal &v) { std::vector<bool> out; for (auto &e : v.arr) out.push_back(asBool(e)); return out; }
inline std::vector<std::string> asStrVec(const JVal &v) { std::vector<std::string> out; for (auto &e : v.arr) out.push_back(asStr(e)); return out; }
inline std::vector<std::optional<int>> asIntOptVec(const JVal &v) {
    std::vector<std::optional<int>> out;
    for (auto &e : v.arr) out.push_back(e.kind == JVal::NUL ? std::nullopt : std::optional<int>(asInt(e)));
    return out;
}
inline std::vector<std::vector<int>> asIntMatrix(const JVal &v) { std::vector<std::vector<int>> out; for (auto &e : v.arr) out.push_back(asIntVec(e)); return out; }
inline std::vector<std::vector<std::string>> asStrMatrix(const JVal &v) { std::vector<std::vector<std::string>> out; for (auto &e : v.arr) out.push_back(asStrVec(e)); return out; }
inline std::vector<std::vector<std::vector<int>>> asIntCube(const JVal &v) { std::vector<std::vector<std::vector<int>>> out; for (auto &e : v.arr) out.push_back(asIntMatrix(e)); return out; }

inline TreeNode *buildTree(const JVal &v) {
    if (v.arr.empty() || v.arr[0].kind == JVal::NUL) return nullptr;
    TreeNode *root = new TreeNode(asInt(v.arr[0]));
    std::vector<TreeNode *> queue = { root };
    size_t i = 1, qi = 0;
    while (qi < queue.size() && i < v.arr.size()) {
        TreeNode *node = queue[qi++];
        if (i < v.arr.size()) {
            if (v.arr[i].kind != JVal::NUL) { node->left = new TreeNode(asInt(v.arr[i])); queue.push_back(node->left); }
            i++;
        }
        if (i < v.arr.size()) {
            if (v.arr[i].kind != JVal::NUL) { node->right = new TreeNode(asInt(v.arr[i])); queue.push_back(node->right); }
            i++;
        }
    }
    return root;
}

inline std::string escapeJsonStr(const std::string &s) {
    std::string out = "\"";
    for (char c : s) {
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c;
        }
    }
    out += "\"";
    return out;
}

inline std::string scalarToJson(int v) { return std::to_string(v); }
inline std::string scalarToJson(double v) { std::ostringstream oss; oss << v; return oss.str(); }
inline std::string scalarToJson(bool v) { return v ? "true" : "false"; }
inline std::string scalarToJson(const std::string &v) { return escapeJsonStr(v); }

inline std::string arrToJson(const std::vector<int> &v) {
    std::string out = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) out += ","; out += std::to_string(v[i]); }
    return out + "]";
}
inline std::string arrToJson(const std::vector<double> &v) {
    std::string out = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) out += ","; out += scalarToJson(v[i]); }
    return out + "]";
}
inline std::string arrToJson(const std::vector<std::string> &v) {
    std::string out = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) out += ","; out += escapeJsonStr(v[i]); }
    return out + "]";
}
inline std::string arrToJson(const std::vector<std::vector<int>> &v) {
    std::string out = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) out += ","; out += arrToJson(v[i]); }
    return out + "]";
}

inline std::string treeToJson(TreeNode *root) {
    std::vector<std::optional<int>> out;
    if (root == nullptr) return "[]";
    out.push_back(root->val);
    std::vector<TreeNode *> queue = { root };
    size_t qi = 0;
    while (qi < queue.size()) {
        TreeNode *node = queue[qi++];
        TreeNode *children[2] = { node->left, node->right };
        for (auto *child : children) {
            if (child == nullptr) out.push_back(std::nullopt);
            else { out.push_back(child->val); queue.push_back(child); }
        }
    }
    while (!out.empty() && !out.back().has_value()) out.pop_back();
    std::string res = "[";
    for (size_t i = 0; i < out.size(); i++) {
        if (i) res += ",";
        res += out[i].has_value() ? std::to_string(*out[i]) : "null";
    }
    return res + "]";
}

}  // namespace __atlas
'''


@dataclass(frozen=True)
class CppFunctionAdapter:
    """
    Compile-once Function Mode adapter (second compiled language, after
    Java -- proves the architecture generalizes). Calling convention:
    `class Solution { public: <ReturnType> <function_name>(<params>) {...} };`
    (LeetCode's exact C++ convention).

    Unlike Java, missing-method/wrong-signature failures are still COMPILE
    ERRORS (g++ itself), but the message shape differs (no reflection-based
    "cannot find symbol" -- g++ reports an undeclared identifier / no
    matching function for call) -- still surfaced as verdict="Compilation
    Error", never misclassified as a runtime error.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        # C++ passes by value by default -- unlike Python/JS, where a list/
        # array argument is always a reference, a `std::vector<int> arr`
        # parameter would mutate only a local copy. The mutated parameter
        # MUST be declared as a reference (`std::vector<int>&`) or an
        # in-place-sort solution's mutation would never reach the caller's
        # variable that the driver reads back afterward.
        params = ", ".join(
            f"{_cpp_type(p.type)}{'&' if p.name == contract.mutates_argument else ''} {p.name}"
            for p in contract.parameters
        )
        if contract.mutates_argument is not None:
            return_type = "void"
            body = ""
        else:
            return_type = _cpp_type(contract.return_type)
            body = f"        return {_cpp_default_return(contract.return_type)};\n"
        tree_prefix = _CPP_TREE_STRUCT if _uses_tree(contract) else ""
        return (
            f"{tree_prefix}"
            f"class Solution {{\n"
            f"public:\n"
            f"    {return_type} {contract.function_name}({params}) {{\n"
            f"{body}"
            f"    }}\n"
            f"}};\n"
        )

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        params_decl = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"__arg{idx}"
            decode = _cpp_decode_expr(p.type, f"__atlas::lookup(__argsObj, __keys, {json.dumps(p.name)})")
            params_decl.append(f"    {_cpp_type(p.type)} {var} = {decode};")
            call_args.append(var)

        raw_call = f"__sol.{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"    {raw_call};"
            mutated_param = contract.parameters[mutated_idx]
            print_stmt = _cpp_print_stmt(mutated_param.type, f"__arg{mutated_idx}")
        else:
            call_statement = ""
            print_stmt = _cpp_print_stmt(contract.return_type, f"({raw_call})") if contract.return_type.kind != "tree" else _cpp_print_stmt(contract.return_type, raw_call)

        # A reasonably broad common-header set (matching what competitive-
        # programming/LeetCode-style judges conventionally pre-include) so a
        # typical solution doesn't need to add its own #includes for the
        # standard containers/algorithms it almost certainly uses.
        header = (
            "#include <iostream>\n"
            "#include <sstream>\n"
            "#include <string>\n"
            "#include <vector>\n"
            "#include <optional>\n"
            "#include <tuple>\n"
            "#include <cmath>\n"
            "#include <cctype>\n"
            "#include <stdexcept>\n"
            "#include <algorithm>\n"
            "#include <map>\n"
            "#include <unordered_map>\n"
            "#include <set>\n"
            "#include <unordered_set>\n"
            "#include <utility>\n"
            "#include <queue>\n"
            "#include <stack>\n"
            "#include <numeric>\n"
            "#include <climits>\n\n"
        )
        # Same double-definition hazard as Java's compose_program (see its
        # comment): generate_starter already emits `struct TreeNode` for
        # tree contracts, and a real submission naturally keeps it -- only
        # add it here if the user's code doesn't already declare it.
        tree_prefix = "" if "struct TreeNode" in user_code else _CPP_TREE_STRUCT

        driver = f'''
{_CPP_RUNTIME}

int main() {{
    std::ostringstream inputBuf;
    inputBuf << std::cin.rdbuf();
    std::string inputText = inputBuf.str();
    std::vector<std::string> __keys;
    std::vector<std::string> __order;
    __atlas::JVal __argsObj = __atlas::parseArgsMap(inputText, __keys, __order);

{chr(10).join(params_decl)}

    Solution __sol;
{call_statement}
    {print_stmt}
    return 0;
}}
'''
        return f"{header}{tree_prefix}{user_code}\n\n{driver}"


def _cpp_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return "\"\""
    if spec.kind == "array":
        return f"{_cpp_type(spec)}()"
    if spec.kind == "tree":
        return "nullptr"
    return "{}"


# ── Rust ─────────────────────────────────────────────────────────────────────
# Third compiled adapter (mission Phase 9 reordering: toolchain audit
# (docs/atlascode-toolchain-report.json) found `go` NOT installed in this
# environment but `rustc` IS, so Rust -- not Go -- is the honest next
# language: implementing an adapter for a toolchain that can't run here
# would violate the "never mark verified without real execution" rule
# before a single case ran). Reuses the SAME compile-once PREPARERS path as
# Java/C++ -- notebook.py already has `_prepare_rust` wired for Program
# Mode, no infra change needed.
#
# Simpler than both Java and C++ on the OUTPUT side: Rust's trait system
# gives a genuinely generic `ToJson` implementation (one recursive impl for
# `Vec<T> where T: ToJson`, one for `Option<T>`) instead of either Java's
# runtime-instanceof writer or C++'s bounded set of concrete `arrToJson`
# overloads -- arbitrary array nesting depth "just works" without adding a
# new helper per shape. `std::tuple`'s Rust equivalent (a native tuple type)
# and `Option<Box<TreeNode>>` (the actual LeetCode-Rust-track convention)
# are both direct, idiomatic fits.

def _rust_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "i32"
    if spec.kind == "float":
        return "f64"
    if spec.kind == "boolean":
        return "bool"
    if spec.kind == "string":
        return "String"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"Option<{_rust_type(spec.items)}>"
    if spec.kind == "array":
        assert spec.items is not None
        return f"Vec<{_rust_type(spec.items)}>"
    if spec.kind == "tree":
        return "Option<Box<TreeNode>>"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"({', '.join(_rust_type(e) for e in spec.elements)})"
    raise ValueError(f"unsupported TypeSpec for Rust: {spec}")


def _rust_decode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    """A Rust expression decoding `value_expr` (of type `&__atlas::JVal`)
    into the concrete typed value `_rust_type(spec)` describes. `_depth`
    keeps generated closure parameter names unique across nested
    array<tuple<...>> decodes -- same reasoning as Java's `_depth`
    (compiled_adapters.py's Java section), not exercised by today's corpus
    beyond one level."""
    if spec.kind == "integer":
        return f"__atlas::as_int({value_expr})"
    if spec.kind == "float":
        return f"__atlas::as_float({value_expr})"
    if spec.kind == "boolean":
        return f"__atlas::as_bool({value_expr})"
    if spec.kind == "string":
        return f"__atlas::as_str({value_expr})"
    if spec.kind == "tree":
        return f"__atlas::build_tree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None
        inner_fn = f"|__v{_depth}: &__atlas::JVal| {_rust_decode_expr(spec.items, f'__v{_depth}', _depth + 1)}"
        return f"__atlas::as_opt({value_expr}, {inner_fn})"
    if spec.kind == "tuple":
        assert spec.elements is not None
        row_var = f"__row{_depth}"
        parts = [_rust_decode_expr(e, f"&{row_var}[{idx}]", _depth + 1) for idx, e in enumerate(spec.elements)]
        return (
            f"{{ let {row_var} = __atlas::as_arr({value_expr}); "
            f"({', '.join(parts)}) }}"
        )
    if spec.kind == "array":
        assert spec.items is not None
        item_var = f"__e{_depth}"
        inner = _rust_decode_expr(spec.items, item_var, _depth + 1)
        inner_fn = f"|{item_var}: &__atlas::JVal| {inner}"
        return f"__atlas::as_vec({value_expr}, {inner_fn})"
    raise ValueError(f"unsupported TypeSpec for Rust decode: {spec}")


_RUST_TREE_STRUCT = (
    "#[derive(Debug, Clone)]\n"
    "pub struct TreeNode {\n"
    "    pub val: i32,\n"
    "    pub left: Option<Box<TreeNode>>,\n"
    "    pub right: Option<Box<TreeNode>>,\n"
    "}\n"
    "impl TreeNode {\n"
    "    #[inline]\n"
    "    pub fn new(val: i32) -> Self {\n"
    "        TreeNode { val, left: None, right: None }\n"
    "    }\n"
    "}\n\n"
)

# Shared runtime: minimal JSON value type + hand-rolled parser + generic
# decode/encode helpers. Bounded to exactly the shapes the real corpus needs
# (mirrors _rust_type's docstring reasoning) -- not a general-purpose JSON
# crate (no external dependencies -- rustc compiles this with zero crates,
# matching every other language adapter's from-scratch-runtime philosophy).
_RUST_RUNTIME = r'''
#[allow(dead_code)]
mod __atlas {
    #[derive(Debug, Clone)]
    pub enum JVal {
        Null,
        Bool(bool),
        Num(f64),
        Str(String),
        Arr(Vec<JVal>),
        Obj(Vec<(String, JVal)>),
    }

    pub struct Parser {
        chars: Vec<char>,
        i: usize,
    }

    impl Parser {
        pub fn new(s: &str) -> Self {
            Parser { chars: s.chars().collect(), i: 0 }
        }
        fn ws(&mut self) {
            while self.i < self.chars.len() && self.chars[self.i].is_whitespace() { self.i += 1; }
        }
        pub fn parse(&mut self) -> JVal {
            self.ws();
            self.value()
        }
        fn value(&mut self) -> JVal {
            self.ws();
            match self.chars[self.i] {
                '{' => self.object(),
                '[' => self.array(),
                '"' => JVal::Str(self.string()),
                't' => { self.i += 4; JVal::Bool(true) }
                'f' => { self.i += 5; JVal::Bool(false) }
                'n' => { self.i += 4; JVal::Null }
                _ => self.number(),
            }
        }
        fn object(&mut self) -> JVal {
            let mut out: Vec<(String, JVal)> = Vec::new();
            self.i += 1; self.ws();
            if self.chars[self.i] == '}' { self.i += 1; return JVal::Obj(out); }
            loop {
                self.ws();
                let k = self.string();
                self.ws(); self.i += 1; // ':'
                let v = self.value();
                out.push((k, v));
                self.ws();
                if self.chars[self.i] == ',' { self.i += 1; continue; }
                self.i += 1; break; // '}'
            }
            JVal::Obj(out)
        }
        fn array(&mut self) -> JVal {
            let mut out: Vec<JVal> = Vec::new();
            self.i += 1; self.ws();
            if self.chars[self.i] == ']' { self.i += 1; return JVal::Arr(out); }
            loop {
                out.push(self.value());
                self.ws();
                if self.chars[self.i] == ',' { self.i += 1; continue; }
                self.i += 1; break; // ']'
            }
            JVal::Arr(out)
        }
        fn string(&mut self) -> String {
            self.i += 1; // opening quote
            let mut out = String::new();
            while self.chars[self.i] != '"' {
                let c = self.chars[self.i];
                if c == '\\' {
                    self.i += 1;
                    let e = self.chars[self.i];
                    match e {
                        'n' => out.push('\n'),
                        't' => out.push('\t'),
                        'r' => out.push('\r'),
                        '"' => out.push('"'),
                        '\\' => out.push('\\'),
                        '/' => out.push('/'),
                        'u' => {
                            let hex: String = self.chars[self.i + 1..self.i + 5].iter().collect();
                            let code = u32::from_str_radix(&hex, 16).unwrap_or(0);
                            if let Some(ch) = char::from_u32(code) { out.push(ch); }
                            self.i += 4;
                        }
                        _ => out.push(e),
                    }
                } else {
                    out.push(c);
                }
                self.i += 1;
            }
            self.i += 1; // closing quote
            out
        }
        fn number(&mut self) -> JVal {
            let start = self.i;
            while self.i < self.chars.len() {
                let c = self.chars[self.i];
                if c.is_ascii_digit() || c == '+' || c == '-' || c == '.' || c == 'e' || c == 'E' { self.i += 1; } else { break; }
            }
            let text: String = self.chars[start..self.i].iter().collect();
            JVal::Num(text.parse::<f64>().unwrap_or(0.0))
        }
    }

    pub fn parse_json(s: &str) -> JVal {
        Parser::new(s).parse()
    }

    pub fn lookup<'a>(obj: &'a JVal, name: &str) -> &'a JVal {
        if let JVal::Obj(pairs) = obj {
            for (k, v) in pairs {
                if k == name { return v; }
            }
        }
        panic!("missing argument: {}", name);
    }

    pub fn as_int(v: &JVal) -> i32 { if let JVal::Num(n) = v { *n as i32 } else { panic!("expected number") } }
    pub fn as_float(v: &JVal) -> f64 { if let JVal::Num(n) = v { *n } else { panic!("expected number") } }
    pub fn as_bool(v: &JVal) -> bool { if let JVal::Bool(b) = v { *b } else { panic!("expected bool") } }
    pub fn as_str(v: &JVal) -> String { if let JVal::Str(s) = v { s.clone() } else { panic!("expected string") } }
    pub fn as_arr(v: &JVal) -> &Vec<JVal> { if let JVal::Arr(a) = v { a } else { panic!("expected array") } }

    pub fn as_opt<T>(v: &JVal, f: impl Fn(&JVal) -> T) -> Option<T> {
        if let JVal::Null = v { None } else { Some(f(v)) }
    }
    pub fn as_vec<T>(v: &JVal, f: impl Fn(&JVal) -> T) -> Vec<T> {
        as_arr(v).iter().map(|e| f(e)).collect()
    }

    pub fn build_tree(v: &JVal) -> Option<Box<super::TreeNode>> {
        let arr = as_arr(v);
        if arr.is_empty() || matches!(arr[0], JVal::Null) { return None; }
        let mut root = Box::new(super::TreeNode::new(as_int(&arr[0])));
        let mut queue: std::collections::VecDeque<*mut super::TreeNode> = std::collections::VecDeque::new();
        queue.push_back(root.as_mut() as *mut super::TreeNode);
        let mut i = 1;
        while let Some(node_ptr) = queue.pop_front() {
            if i >= arr.len() { break; }
            unsafe {
                if i < arr.len() {
                    if !matches!(arr[i], JVal::Null) {
                        (*node_ptr).left = Some(Box::new(super::TreeNode::new(as_int(&arr[i]))));
                        queue.push_back((*node_ptr).left.as_mut().unwrap().as_mut() as *mut super::TreeNode);
                    }
                    i += 1;
                }
                if i < arr.len() {
                    if !matches!(arr[i], JVal::Null) {
                        (*node_ptr).right = Some(Box::new(super::TreeNode::new(as_int(&arr[i]))));
                        queue.push_back((*node_ptr).right.as_mut().unwrap().as_mut() as *mut super::TreeNode);
                    }
                    i += 1;
                }
            }
        }
        Some(root)
    }

    pub fn serialize_tree(root: &Option<Box<super::TreeNode>>) -> Vec<Option<i32>> {
        let mut out: Vec<Option<i32>> = Vec::new();
        if root.is_none() { return out; }
        out.push(Some(root.as_ref().unwrap().val));
        let mut queue: std::collections::VecDeque<&Box<super::TreeNode>> = std::collections::VecDeque::new();
        queue.push_back(root.as_ref().unwrap());
        while let Some(node) = queue.pop_front() {
            for child in [&node.left, &node.right] {
                match child {
                    Some(c) => { out.push(Some(c.val)); queue.push_back(c); }
                    None => out.push(None),
                }
            }
        }
        while let Some(None) = out.last() { out.pop(); }
        out
    }

    fn escape_json_str(s: &str) -> String {
        let mut out = String::from("\"");
        for c in s.chars() {
            match c {
                '"' => out.push_str("\\\""),
                '\\' => out.push_str("\\\\"),
                '\n' => out.push_str("\\n"),
                '\r' => out.push_str("\\r"),
                '\t' => out.push_str("\\t"),
                c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
                c => out.push(c),
            }
        }
        out.push('"');
        out
    }

    pub trait ToJson {
        fn to_json(&self) -> String;
    }
    impl ToJson for i32 { fn to_json(&self) -> String { self.to_string() } }
    impl ToJson for f64 {
        fn to_json(&self) -> String {
            if self.fract() == 0.0 && self.is_finite() { format!("{:.1}", self) } else { self.to_string() }
        }
    }
    impl ToJson for bool { fn to_json(&self) -> String { if *self { "true".to_string() } else { "false".to_string() } } }
    impl ToJson for String { fn to_json(&self) -> String { escape_json_str(self) } }
    impl ToJson for &str { fn to_json(&self) -> String { escape_json_str(self) } }
    impl<T: ToJson> ToJson for Vec<T> {
        fn to_json(&self) -> String {
            let parts: Vec<String> = self.iter().map(|x| x.to_json()).collect();
            format!("[{}]", parts.join(","))
        }
    }
    impl<T: ToJson> ToJson for Option<T> {
        fn to_json(&self) -> String {
            match self { Some(v) => v.to_json(), None => "null".to_string() }
        }
    }
    impl ToJson for Option<Box<super::TreeNode>> {
        fn to_json(&self) -> String { serialize_tree(self).to_json() }
    }
}
'''


@dataclass(frozen=True)
class RustFunctionAdapter:
    """
    Compile-once Function Mode adapter (3rd, after Java/C++). Calling
    convention: the user writes a plain top-level `fn <function_name>(...)`
    -- no class/impl-block wrapper needed, unlike Java/C++'s `Solution`
    (Rust doesn't require one for free functions, and LeetCode's own Rust
    track uses bare functions too).

    Missing function / wrong parameter types are Rust COMPILE ERRORS
    (caught by rustc before the driver ever runs), surfaced by runner.py as
    verdict="Compilation Error" via the same compile-once PREPARERS path
    Java/C++ already use (`_prepare_rust`, `notebook.py`) -- no new
    infrastructure.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name}: {_rust_type(p.type)}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            # `&mut Vec<T>` -- Rust's own in-place-mutation convention;
            # matches Java/C++'s reference-parameter approach for the same
            # 21 in-place-sort problems.
            params = ", ".join(
                f"{p.name}: {'&mut ' if p.name == contract.mutates_argument else ''}{_rust_type(p.type)}"
                for p in contract.parameters
            )
            return_type = "()"
            body = ""
        else:
            return_type = _rust_type(contract.return_type)
            body = f"    {_rust_default_return(contract.return_type)}\n"
        tree_prefix = _RUST_TREE_STRUCT if _uses_tree(contract) else ""
        return (
            f"{tree_prefix}"
            f"fn {contract.function_name}({params}) -> {return_type} {{\n"
            f"{body}"
            f"}}\n"
        )

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        params_decl = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"__arg{idx}"
            decode = _rust_decode_expr(p.type, f"__atlas::lookup(&__args, {json.dumps(p.name)})")
            mut_kw = "mut " if p.name == contract.mutates_argument else ""
            params_decl.append(f"    let {mut_kw}{var}: {_rust_type(p.type)} = {decode};")
            call_args.append(f"&mut {var}" if p.name == contract.mutates_argument else var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"    {raw_call};"
            result_expr = f"__arg{mutated_idx}"
        else:
            call_statement = ""
            result_expr = raw_call

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready = f"__atlas::serialize_tree(&({result_expr}))"
        else:
            json_ready = f"({result_expr})"

        tree_prefix = "" if "struct TreeNode" in user_code else _RUST_TREE_STRUCT

        driver = f'''
{tree_prefix}
{_RUST_RUNTIME}

fn main() {{
    let mut input_text = String::new();
    std::io::Read::read_to_string(&mut std::io::stdin(), &mut input_text).unwrap();
    let __args = __atlas::parse_json(&input_text);

{chr(10).join(params_decl)}

{call_statement}
    let __result = {json_ready};
    println!("{RESULT_SENTINEL}{{}}", __atlas::ToJson::to_json(&__result));
}}
'''
        return f"{user_code}\n\n{driver}"


def _rust_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return "String::new()"
    if spec.kind == "array":
        return "Vec::new()"
    if spec.kind in ("optional", "tree"):
        return "None"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"({', '.join(_rust_default_return(e) for e in spec.elements)})"
    return "Default::default()"


# ── C ────────────────────────────────────────────────────────────────────────
# Fourth compiled adapter. Reuses the same compile-once PREPARERS path as
# Java/C++/Rust (`_prepare_c`, already wired in notebook.py for Program Mode).
#
# Structurally closest to C++'s adapter (both hand-roll a JSON value type
# since neither language has one built in) but with one deliberate scope
# reduction: NO tuple support yet. C has no generics and no native product
# type -- representing `array<tuple<string, optional<integer>>>` would need
# a bespoke per-contract struct generated at codegen time (a real, larger
# design task, not a mechanical extension of the fixed-shape runtime below).
# Every other language shipped without tuple support first too (min-stack was
# quarantined until Phase 6 built the IR for it); C simply hasn't had that
# follow-up pass yet -- an honest, temporary gap, not an oversight.
#
# Memory is deliberately never freed: every generated program is a single-
# shot CLI process that parses one JSON blob, computes one answer, prints
# it, and exits immediately -- the OS reclaims everything on exit. Adding
# manual free() bookkeeping would only add bug surface for a process whose
# entire lifetime is under a second.

def _c_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "int"
    if spec.kind == "float":
        return "double"
    if spec.kind == "boolean":
        return "int"
    if spec.kind == "string":
        return "char*"
    if spec.kind == "optional":
        assert spec.items is not None
        if spec.items.kind == "integer":
            return "AtlasOptInt"
        raise ValueError(f"unsupported optional<{spec.items.kind}> for C -- corpus audit found only optional<integer>")
    if spec.kind == "tree":
        return "struct TreeNode*"
    if spec.kind == "tuple":
        raise ValueError("C Function Mode does not support tuple-typed contracts yet (see module docstring)")
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        if item.kind == "integer":
            return "AtlasIntArray"
        if item.kind == "float":
            return "AtlasDoubleArray"
        if item.kind == "boolean":
            return "AtlasBoolArray"
        if item.kind == "string":
            return "AtlasStringArray"
        if item.kind == "optional" and item.items is not None and item.items.kind == "integer":
            return "AtlasOptIntArray"
        if item.kind == "array" and item.items is not None and item.items.kind == "integer":
            return "AtlasIntMatrix"
        if item.kind == "array" and item.items is not None and item.items.kind == "string":
            return "AtlasStringMatrix"
        if item.kind == "array" and item.items is not None and item.items.kind == "array" and item.items.items is not None and item.items.items.kind == "integer":
            return "AtlasIntCube"
        raise ValueError(f"unsupported nested array item type for C: {item}")
    raise ValueError(f"unsupported TypeSpec for C: {spec}")


def _c_decode_expr(spec: TypeSpec, value_expr: str) -> str:
    """A C expression decoding `value_expr` (an `AtlasJVal`) into the
    concrete typed value `_c_type(spec)` describes -- every decode is a
    plain function call into the fixed runtime below (no inline loops
    needed in generated code, unlike a naive statement-based approach: the
    loop lives ONCE inside each atlas_as_*_array function, not regenerated
    per contract)."""
    if spec.kind == "integer":
        return f"atlas_as_int({value_expr})"
    if spec.kind == "float":
        return f"atlas_as_double({value_expr})"
    if spec.kind == "boolean":
        return f"atlas_as_bool({value_expr})"
    if spec.kind == "string":
        return f"atlas_as_str({value_expr})"
    if spec.kind == "tree":
        return f"atlas_build_tree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None and spec.items.kind == "integer"
        return f"atlas_as_opt_int({value_expr})"
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        if item.kind == "integer":
            return f"atlas_as_int_array({value_expr})"
        if item.kind == "float":
            return f"atlas_as_double_array({value_expr})"
        if item.kind == "boolean":
            return f"atlas_as_bool_array({value_expr})"
        if item.kind == "string":
            return f"atlas_as_string_array({value_expr})"
        if item.kind == "optional" and item.items is not None and item.items.kind == "integer":
            return f"atlas_as_opt_int_array({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "integer":
            return f"atlas_as_int_matrix({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "string":
            return f"atlas_as_string_matrix({value_expr})"
        if item.kind == "array" and item.items is not None and item.items.kind == "array" and item.items.items is not None and item.items.items.kind == "integer":
            return f"atlas_as_int_cube({value_expr})"
        raise ValueError(f"unsupported nested array item type for C decode: {item}")
    raise ValueError(f"unsupported TypeSpec for C decode: {spec}")


def _c_print_stmt(spec: TypeSpec, value_expr: str) -> str:
    """A complete C statement printing the sentinel + JSON-encoded value."""
    if spec.kind == "integer":
        return f'printf("{RESULT_SENTINEL}%d\\n", {value_expr});'
    if spec.kind == "float":
        return f'printf("{RESULT_SENTINEL}%s\\n", atlas_double_to_json({value_expr}));'
    if spec.kind == "boolean":
        return f'printf("{RESULT_SENTINEL}%s\\n", ({value_expr}) ? "true" : "false");'
    if spec.kind == "string":
        return f'printf("{RESULT_SENTINEL}%s\\n", atlas_string_to_json({value_expr}));'
    if spec.kind == "tree":
        return f'printf("{RESULT_SENTINEL}%s\\n", atlas_tree_to_json({value_expr}));'
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        if item.kind == "integer":
            return f'printf("{RESULT_SENTINEL}%s\\n", atlas_int_array_to_json({value_expr}));'
        if item.kind == "float":
            return f'printf("{RESULT_SENTINEL}%s\\n", atlas_double_array_to_json({value_expr}));'
        if item.kind == "boolean":
            return f'printf("{RESULT_SENTINEL}%s\\n", atlas_bool_array_to_json({value_expr}));'
        if item.kind == "string":
            return f'printf("{RESULT_SENTINEL}%s\\n", atlas_string_array_to_json({value_expr}));'
        if item.kind == "array" and item.items is not None and item.items.kind == "integer":
            return f'printf("{RESULT_SENTINEL}%s\\n", atlas_int_matrix_to_json({value_expr}));'
        raise ValueError(f"unsupported array return item type for C print: {item}")
    raise ValueError(f"unsupported TypeSpec for C print: {spec}")


_C_TREE_STRUCT = (
    "struct TreeNode {\n"
    "    int val;\n"
    "    struct TreeNode *left;\n"
    "    struct TreeNode *right;\n"
    "};\n\n"
)

# Shared runtime: minimal JSON value type + hand-rolled parser (dynamic
# buffers via realloc doubling -- no fixed-size buffer limits) + a FIXED set
# of decode/encode functions bounded to exactly the shapes the real corpus
# needs (same audited scope as Java/C++/Rust: scalars, 1-3D arrays of
# int/string/double/bool, tree<integer>, optional<integer>). Prefixed
# `Atlas`/`atlas_` throughout so nothing can collide with a user's own
# identifiers -- C has no namespaces.
# Split into TYPES (must precede the user's own function signature, which
# directly uses AtlasIntArray/AtlasOptInt/etc. as parameter/return types --
# C has no built-in dynamic-array/optional type, unlike every other
# adapter's language, so these ARE the parameter types, not just internal
# driver plumbing) and FUNCS (the parser + decode/encode functions, which
# only the driver's main() calls -- safe to place after user_code, which
# matters because atlas_build_tree/atlas_tree_to_json reference `struct
# TreeNode`, and that struct is defined by EITHER the synthesized
# tree_prefix OR the user's own resubmitted starter code, whichever one
# compose_program actually emits -- FUNCS must come after both to guarantee
# it's already declared no matter which source defined it).
_C_TYPES = r'''
typedef enum { ATLAS_NULL, ATLAS_BOOL, ATLAS_NUM, ATLAS_STR, ATLAS_ARR, ATLAS_OBJ } AtlasKind;

typedef struct AtlasJVal {
    AtlasKind kind;
    int b;
    double num;
    char *str;
    struct AtlasJVal *items;  /* ARR: elements; OBJ: values */
    char **keys;              /* OBJ only */
    int len;
} AtlasJVal;

typedef struct { int has_value; int value; } AtlasOptInt;
typedef struct { int *data; int size; } AtlasIntArray;
typedef struct { double *data; int size; } AtlasDoubleArray;
typedef struct { int *data; int size; } AtlasBoolArray;
typedef struct { char **data; int size; } AtlasStringArray;
typedef struct { AtlasOptInt *data; int size; } AtlasOptIntArray;
typedef struct { AtlasIntArray *data; int size; } AtlasIntMatrix;
typedef struct { AtlasStringArray *data; int size; } AtlasStringMatrix;
typedef struct { AtlasIntMatrix *data; int size; } AtlasIntCube;
'''

_C_FUNCS = r'''
typedef struct { const char *s; int i; } AtlasParser;

static void atlas_ws(AtlasParser *p) {
    while (isspace((unsigned char) p->s[p->i])) p->i++;
}

static AtlasJVal atlas_parse_value(AtlasParser *p);

static char *atlas_parse_raw_string(AtlasParser *p) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    p->i++; /* opening quote */
    while (p->s[p->i] != '"') {
        char c = p->s[p->i];
        char emit;
        if (c == '\\') {
            p->i++;
            char e = p->s[p->i];
            switch (e) {
                case 'n': emit = '\n'; break;
                case 't': emit = '\t'; break;
                case 'r': emit = '\r'; break;
                case '"': emit = '"'; break;
                case '\\': emit = '\\'; break;
                case '/': emit = '/'; break;
                default: emit = e;
            }
        } else {
            emit = c;
        }
        if (len + 1 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        out[len++] = emit;
        p->i++;
    }
    p->i++; /* closing quote */
    out[len] = '\0';
    return out;
}

static AtlasJVal atlas_parse_array(AtlasParser *p) {
    AtlasJVal v; v.kind = ATLAS_ARR; v.len = 0;
    int cap = 8;
    v.items = (AtlasJVal *) malloc(cap * sizeof(AtlasJVal));
    p->i++; atlas_ws(p);
    if (p->s[p->i] == ']') { p->i++; return v; }
    while (1) {
        if (v.len >= cap) { cap *= 2; v.items = (AtlasJVal *) realloc(v.items, cap * sizeof(AtlasJVal)); }
        v.items[v.len++] = atlas_parse_value(p);
        atlas_ws(p);
        if (p->s[p->i] == ',') { p->i++; continue; }
        p->i++; break; /* ']' */
    }
    return v;
}

static AtlasJVal atlas_parse_object(AtlasParser *p) {
    AtlasJVal v; v.kind = ATLAS_OBJ; v.len = 0;
    int cap = 8;
    v.items = (AtlasJVal *) malloc(cap * sizeof(AtlasJVal));
    v.keys = (char **) malloc(cap * sizeof(char *));
    p->i++; atlas_ws(p);
    if (p->s[p->i] == '}') { p->i++; return v; }
    while (1) {
        atlas_ws(p);
        char *k = atlas_parse_raw_string(p);
        atlas_ws(p); p->i++; /* ':' */
        AtlasJVal val = atlas_parse_value(p);
        if (v.len >= cap) {
            cap *= 2;
            v.items = (AtlasJVal *) realloc(v.items, cap * sizeof(AtlasJVal));
            v.keys = (char **) realloc(v.keys, cap * sizeof(char *));
        }
        v.keys[v.len] = k;
        v.items[v.len] = val;
        v.len++;
        atlas_ws(p);
        if (p->s[p->i] == ',') { p->i++; continue; }
        p->i++; break; /* '}' */
    }
    return v;
}

static AtlasJVal atlas_parse_number(AtlasParser *p) {
    int start = p->i;
    while (isdigit((unsigned char) p->s[p->i]) || p->s[p->i] == '+' || p->s[p->i] == '-'
           || p->s[p->i] == '.' || p->s[p->i] == 'e' || p->s[p->i] == 'E') p->i++;
    int len = p->i - start;
    char *buf = (char *) malloc(len + 1);
    memcpy(buf, p->s + start, len);
    buf[len] = '\0';
    AtlasJVal v; v.kind = ATLAS_NUM; v.num = atof(buf);
    free(buf);
    return v;
}

static AtlasJVal atlas_parse_value(AtlasParser *p) {
    atlas_ws(p);
    char c = p->s[p->i];
    AtlasJVal v;
    if (c == '{') return atlas_parse_object(p);
    if (c == '[') return atlas_parse_array(p);
    if (c == '"') { v.kind = ATLAS_STR; v.str = atlas_parse_raw_string(p); return v; }
    if (c == 't') { p->i += 4; v.kind = ATLAS_BOOL; v.b = 1; return v; }
    if (c == 'f') { p->i += 5; v.kind = ATLAS_BOOL; v.b = 0; return v; }
    if (c == 'n') { p->i += 4; v.kind = ATLAS_NULL; return v; }
    return atlas_parse_number(p);
}

static AtlasJVal atlas_parse_json(const char *s) {
    AtlasParser p; p.s = s; p.i = 0;
    return atlas_parse_value(&p);
}

static AtlasJVal atlas_lookup(AtlasJVal obj, const char *name) {
    for (int i = 0; i < obj.len; i++) {
        if (strcmp(obj.keys[i], name) == 0) return obj.items[i];
    }
    fprintf(stderr, "missing argument: %s\n", name);
    exit(1);
}

static int atlas_as_int(AtlasJVal v) { return (int) llround(v.num); }
static double atlas_as_double(AtlasJVal v) { return v.num; }
static int atlas_as_bool(AtlasJVal v) { return v.b; }
static char *atlas_as_str(AtlasJVal v) { return v.str; }
static AtlasOptInt atlas_as_opt_int(AtlasJVal v) {
    AtlasOptInt o;
    if (v.kind == ATLAS_NULL) { o.has_value = 0; o.value = 0; }
    else { o.has_value = 1; o.value = atlas_as_int(v); }
    return o;
}

static AtlasIntArray atlas_as_int_array(AtlasJVal v) {
    AtlasIntArray a; a.size = v.len; a.data = (int *) malloc(sizeof(int) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_int(v.items[i]);
    return a;
}
static AtlasDoubleArray atlas_as_double_array(AtlasJVal v) {
    AtlasDoubleArray a; a.size = v.len; a.data = (double *) malloc(sizeof(double) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_double(v.items[i]);
    return a;
}
static AtlasBoolArray atlas_as_bool_array(AtlasJVal v) {
    AtlasBoolArray a; a.size = v.len; a.data = (int *) malloc(sizeof(int) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_bool(v.items[i]);
    return a;
}
static AtlasStringArray atlas_as_string_array(AtlasJVal v) {
    AtlasStringArray a; a.size = v.len; a.data = (char **) malloc(sizeof(char *) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_str(v.items[i]);
    return a;
}
static AtlasOptIntArray atlas_as_opt_int_array(AtlasJVal v) {
    AtlasOptIntArray a; a.size = v.len; a.data = (AtlasOptInt *) malloc(sizeof(AtlasOptInt) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_opt_int(v.items[i]);
    return a;
}
static AtlasIntMatrix atlas_as_int_matrix(AtlasJVal v) {
    AtlasIntMatrix a; a.size = v.len; a.data = (AtlasIntArray *) malloc(sizeof(AtlasIntArray) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_int_array(v.items[i]);
    return a;
}
static AtlasStringMatrix atlas_as_string_matrix(AtlasJVal v) {
    AtlasStringMatrix a; a.size = v.len; a.data = (AtlasStringArray *) malloc(sizeof(AtlasStringArray) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_string_array(v.items[i]);
    return a;
}
static AtlasIntCube atlas_as_int_cube(AtlasJVal v) {
    AtlasIntCube a; a.size = v.len; a.data = (AtlasIntMatrix *) malloc(sizeof(AtlasIntMatrix) * (v.len ? v.len : 1));
    for (int i = 0; i < v.len; i++) a.data[i] = atlas_as_int_matrix(v.items[i]);
    return a;
}

static struct TreeNode *atlas_build_tree(AtlasJVal v) {
    if (v.len == 0 || v.items[0].kind == ATLAS_NULL) return NULL;
    struct TreeNode *root = (struct TreeNode *) malloc(sizeof(struct TreeNode));
    root->val = atlas_as_int(v.items[0]); root->left = NULL; root->right = NULL;
    struct TreeNode **queue = (struct TreeNode **) malloc(sizeof(struct TreeNode *) * (v.len + 1));
    int qh = 0, qt = 0;
    queue[qt++] = root;
    int i = 1;
    while (qh < qt && i < v.len) {
        struct TreeNode *node = queue[qh++];
        if (i < v.len) {
            if (v.items[i].kind != ATLAS_NULL) {
                node->left = (struct TreeNode *) malloc(sizeof(struct TreeNode));
                node->left->val = atlas_as_int(v.items[i]); node->left->left = NULL; node->left->right = NULL;
                queue[qt++] = node->left;
            }
            i++;
        }
        if (i < v.len) {
            if (v.items[i].kind != ATLAS_NULL) {
                node->right = (struct TreeNode *) malloc(sizeof(struct TreeNode));
                node->right->val = atlas_as_int(v.items[i]); node->right->left = NULL; node->right->right = NULL;
                queue[qt++] = node->right;
            }
            i++;
        }
    }
    return root;
}

static char *atlas_escape_json_str(const char *s) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '"';
    for (const char *c = s; *c; c++) {
        const char *rep = NULL;
        char buf6[8];
        switch (*c) {
            case '"': rep = "\\\""; break;
            case '\\': rep = "\\\\"; break;
            case '\n': rep = "\\n"; break;
            case '\r': rep = "\\r"; break;
            case '\t': rep = "\\t"; break;
            default:
                if ((unsigned char) *c < 0x20) { snprintf(buf6, sizeof(buf6), "\\u%04x", *c); rep = buf6; }
        }
        int add_len = rep ? (int) strlen(rep) : 1;
        while (len + add_len + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        if (rep) { memcpy(out + len, rep, add_len); len += add_len; }
        else { out[len++] = *c; }
    }
    out[len++] = '"'; out[len] = '\0';
    return out;
}

static char *atlas_string_to_json(const char *s) { return atlas_escape_json_str(s); }

static char *atlas_double_to_json(double d) {
    char *buf = (char *) malloc(64);
    if (d == (long long) d) snprintf(buf, 64, "%.1f", d);
    else snprintf(buf, 64, "%g", d);
    return buf;
}

static char *atlas_int_array_to_json(AtlasIntArray a) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '[';
    for (int i = 0; i < a.size; i++) {
        char num[32]; int n = snprintf(num, sizeof(num), "%s%d", i ? "," : "", a.data[i]);
        while (len + n + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        memcpy(out + len, num, n); len += n;
    }
    out[len++] = ']'; out[len] = '\0';
    return out;
}

static char *atlas_double_array_to_json(AtlasDoubleArray a) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '[';
    for (int i = 0; i < a.size; i++) {
        if (i) out[len++] = ',';
        char *d = atlas_double_to_json(a.data[i]);
        int n = (int) strlen(d);
        while (len + n + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        memcpy(out + len, d, n); len += n;
    }
    out[len++] = ']'; out[len] = '\0';
    return out;
}

static char *atlas_bool_array_to_json(AtlasBoolArray a) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '[';
    for (int i = 0; i < a.size; i++) {
        const char *tok = a.data[i] ? "true" : "false";
        int n = (int) strlen(tok);
        while (len + n + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        if (i) out[len++] = ',';
        memcpy(out + len, tok, n); len += n;
    }
    out[len++] = ']'; out[len] = '\0';
    return out;
}

static char *atlas_string_array_to_json(AtlasStringArray a) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '[';
    for (int i = 0; i < a.size; i++) {
        if (i) { if (len + 1 >= cap) { cap *= 2; out = (char *) realloc(out, cap); } out[len++] = ','; }
        char *s = atlas_escape_json_str(a.data[i]);
        int n = (int) strlen(s);
        while (len + n + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        memcpy(out + len, s, n); len += n;
    }
    out[len++] = ']'; out[len] = '\0';
    return out;
}

static char *atlas_int_matrix_to_json(AtlasIntMatrix a) {
    int cap = 64, len = 0;
    char *out = (char *) malloc(cap);
    out[len++] = '[';
    for (int i = 0; i < a.size; i++) {
        if (i) { if (len + 1 >= cap) { cap *= 2; out = (char *) realloc(out, cap); } out[len++] = ','; }
        char *row = atlas_int_array_to_json(a.data[i]);
        int n = (int) strlen(row);
        while (len + n + 2 >= cap) { cap *= 2; out = (char *) realloc(out, cap); }
        memcpy(out + len, row, n); len += n;
    }
    out[len++] = ']'; out[len] = '\0';
    return out;
}

static char *atlas_tree_to_json(struct TreeNode *root) {
    if (root == NULL) { char *e = (char *) malloc(3); strcpy(e, "[]"); return e; }
    int cap = 16, size = 0;
    AtlasOptInt *out = (AtlasOptInt *) malloc(sizeof(AtlasOptInt) * cap);
    AtlasOptInt rootVal; rootVal.has_value = 1; rootVal.value = root->val;
    out[size++] = rootVal;
    struct TreeNode **queue = (struct TreeNode **) malloc(sizeof(struct TreeNode *) * 4096);
    int qh = 0, qt = 0;
    queue[qt++] = root;
    while (qh < qt) {
        struct TreeNode *node = queue[qh++];
        struct TreeNode *children[2]; children[0] = node->left; children[1] = node->right;
        for (int c = 0; c < 2; c++) {
            if (size >= cap) { cap *= 2; out = (AtlasOptInt *) realloc(out, sizeof(AtlasOptInt) * cap); }
            if (children[c] == NULL) {
                AtlasOptInt none; none.has_value = 0; none.value = 0;
                out[size++] = none;
            } else {
                AtlasOptInt some; some.has_value = 1; some.value = children[c]->val;
                out[size++] = some;
                queue[qt++] = children[c];
            }
        }
    }
    while (size > 0 && out[size - 1].has_value == 0) size--;
    int bcap = 64, blen = 0;
    char *buf = (char *) malloc(bcap);
    buf[blen++] = '[';
    for (int i = 0; i < size; i++) {
        char num[32];
        int n = out[i].has_value
            ? snprintf(num, sizeof(num), "%s%d", i ? "," : "", out[i].value)
            : snprintf(num, sizeof(num), "%snull", i ? "," : "");
        while (blen + n + 2 >= bcap) { bcap *= 2; buf = (char *) realloc(buf, bcap); }
        memcpy(buf + blen, num, n); blen += n;
    }
    buf[blen++] = ']'; buf[blen] = '\0';
    return buf;
}
'''


@dataclass(frozen=True)
class CFunctionAdapter:
    """
    Compile-once Function Mode adapter (4th, after Java/C++/Rust). Calling
    convention: the user writes a plain top-level C function -- no
    class/struct wrapper (C has no classes; a free function IS the
    idiomatic shape, matching Rust's approach more than Java/C++'s
    `Solution` class).

    A missing/renamed function, or a wrong parameter count/type, is caught
    by gcc as a genuine COMPILE ERROR (implicit-function-declaration is a
    hard error under the -Werror=implicit-function-declaration-equivalent
    strictness modern gcc defaults to for undeclared calls, and a type
    mismatch on a declared-elsewhere signature also fails compilation) --
    surfaced by runner.py as verdict="Compilation Error" via the same
    compile-once PREPARERS path as every other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{_c_type(p.type)} {p.name}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            params = ", ".join(
                f"{_c_type(p.type)}{'*' if p.name == contract.mutates_argument else ''} {p.name}"
                for p in contract.parameters
            )
            return_type = "void"
            body = ""
        else:
            return_type = _c_type(contract.return_type)
            body = f"    return {_c_default_return(contract.return_type)};\n"
        tree_prefix = _C_TREE_STRUCT if _uses_tree(contract) else ""
        return f"{tree_prefix}{return_type} {contract.function_name}({params}) {{\n{body}}}\n"

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        params_decl = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"__arg{idx}"
            decode = _c_decode_expr(p.type, f"atlas_lookup(__args, {json.dumps(p.name)})")
            params_decl.append(f"    {_c_type(p.type)} {var} = {decode};")
            call_args.append(f"&{var}" if p.name == contract.mutates_argument else var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"    {raw_call};"
            print_stmt = _c_print_stmt(contract.parameters[mutated_idx].type, f"__arg{mutated_idx}")
        else:
            call_statement = ""
            print_stmt = _c_print_stmt(contract.return_type, f"__result")

        result_decl = "" if contract.mutates_argument is not None else f"    {_c_type(contract.return_type)} __result = {raw_call};\n"

        tree_prefix = "" if "struct TreeNode" in user_code else _C_TREE_STRUCT

        header = (
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include <ctype.h>\n"
            "#include <math.h>\n\n"
        )

        driver = f'''
{_C_FUNCS}

int main(void) {{
    char *inputText = (char *) malloc(1);
    inputText[0] = '\\0';
    int cap = 1, len = 0;
    char chunk[65536];
    size_t n;
    while ((n = fread(chunk, 1, sizeof(chunk), stdin)) > 0) {{
        while (len + (int) n + 1 >= cap) {{ cap *= 2; inputText = (char *) realloc(inputText, cap); }}
        memcpy(inputText + len, chunk, n);
        len += (int) n;
        inputText[len] = '\\0';
    }}
    AtlasJVal __args = atlas_parse_json(inputText);

{chr(10).join(params_decl)}

{call_statement}
{result_decl}
    {print_stmt}
    return 0;
}}
'''
        # Ordering is load-bearing (C has no forward declarations for
        # typedefs, unlike every other compiled adapter's language):
        #   1. _C_TYPES -- AtlasIntArray/AtlasOptInt/etc., since the user's
        #      OWN function signature uses them directly as parameter/
        #      return types (C has no built-in dynamic-array/optional type
        #      to reuse the way Java/C++/Rust's std/collection types are).
        #   2. tree_prefix -- struct TreeNode, only synthesized if the
        #      user's code doesn't already redeclare it (a real submission
        #      built on generate_starter's tree-problem starter keeps its
        #      own copy -- re-adding it would be a duplicate-definition
        #      compile error, the exact bug the same check already fixed
        #      for Java/C++).
        #   3. user_code -- may itself be the thing that defines TreeNode.
        #   4. driver (_C_FUNCS + main) -- _C_FUNCS's atlas_build_tree/
        #      atlas_tree_to_json reference `struct TreeNode`, so this MUST
        #      come after both 2 and 3, whichever one actually defined it.
        return f"{header}{_C_TYPES}{tree_prefix}{user_code}\n\n{driver}"


def _c_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "0"
    if spec.kind == "string":
        return '""'
    if spec.kind == "tree":
        return "NULL"
    return "{0}"


# ── C# ───────────────────────────────────────────────────────────────────────
# Fifth compiled adapter. Genuinely simpler than C/C++/Java/Rust: .NET ships
# a real JSON parser (System.Text.Json) and a real tuple type (ValueTuple,
# `(T1, T2)` syntax) in the standard library, so this adapter needs NO
# hand-rolled JSON parser and NO boxed-Object/std::tuple/generic-trait
# workaround for tuple support -- it is supported from day one here, unlike
# C's temporary gap. Uses the SAME compile-once PREPARERS path as Java/C++/
# Rust/C (`_prepare_csharp` in notebook.py, added this session -- see that
# function's docstring for why `dotnet build -o out` + reusing the DLL is a
# real isolable compile step, contradicting this codebase's prior
# documented assumption that csharp couldn't have one).

def _csharp_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "int"
    if spec.kind == "float":
        return "double"
    if spec.kind == "boolean":
        return "bool"
    if spec.kind == "string":
        return "string"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_csharp_type(spec.items)}?"
    if spec.kind == "array":
        assert spec.items is not None
        return f"{_csharp_type(spec.items)}[]"
    if spec.kind == "tree":
        return "TreeNode"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"({', '.join(_csharp_type(e) for e in spec.elements)})"
    raise ValueError(f"unsupported TypeSpec for C#: {spec}")


def _csharp_decode_expr(spec: TypeSpec, value_expr: str) -> str:
    """A C# expression decoding `value_expr` (a `JsonElement`) into the
    concrete typed value `_csharp_type(spec)` describes."""
    if spec.kind == "integer":
        return f"({value_expr}).GetInt32()"
    if spec.kind == "float":
        return f"({value_expr}).GetDouble()"
    if spec.kind == "boolean":
        return f"({value_expr}).GetBoolean()"
    if spec.kind == "string":
        return f"({value_expr}).GetString()"
    if spec.kind == "tree":
        return f"AtlasHelpers.BuildTree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None
        inner = _csharp_decode_expr(spec.items, value_expr)
        return f"(({value_expr}).ValueKind == JsonValueKind.Null ? ({_csharp_type(spec)}) null : {inner})"
    if spec.kind == "tuple":
        assert spec.elements is not None
        parts = [_csharp_decode_expr(e, f"AtlasHelpers.At({value_expr}, {i})") for i, e in enumerate(spec.elements)]
        return f"({', '.join(parts)})"
    if spec.kind == "array":
        assert spec.items is not None
        item = spec.items
        item_type = _csharp_type(item)
        item_expr = _csharp_decode_expr(item, "__e")
        return (
            f"System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select("
            f"({value_expr}).EnumerateArray(), __e => {item_expr}))"
        )
    raise ValueError(f"unsupported TypeSpec for C# decode: {spec}")


_CSHARP_TREE_CLASS = (
    "public class TreeNode {\n"
    "    public int val;\n"
    "    public TreeNode left;\n"
    "    public TreeNode right;\n"
    "    public TreeNode() {}\n"
    "    public TreeNode(int val) { this.val = val; }\n"
    "    public TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; }\n"
    "}\n\n"
)

# Shared runtime: only the handful of helpers System.Text.Json doesn't give
# for free -- tuple element access by index (JsonElement has no int
# indexer), and tree build/serialize (structural, not a JSON built-in
# concept in any language's standard library). Everything else (parsing,
# scalar/array decode, scalar/array JSON encoding) is genuinely just
# `System.Text.Json.JsonSerializer`/`JsonElement`, not reimplemented.
_CSHARP_RUNTIME = r'''
public static class AtlasHelpers {
    public static System.Text.Json.JsonElement At(System.Text.Json.JsonElement arr, int i) {
        return System.Linq.Enumerable.ElementAt(arr.EnumerateArray(), i);
    }

    public static TreeNode BuildTree(System.Text.Json.JsonElement v) {
        var arr = System.Linq.Enumerable.ToArray(v.EnumerateArray());
        if (arr.Length == 0 || arr[0].ValueKind == System.Text.Json.JsonValueKind.Null) return null;
        var root = new TreeNode(arr[0].GetInt32());
        var queue = new System.Collections.Generic.Queue<TreeNode>();
        queue.Enqueue(root);
        int i = 1;
        while (queue.Count > 0 && i < arr.Length) {
            var node = queue.Dequeue();
            if (i < arr.Length) {
                if (arr[i].ValueKind != System.Text.Json.JsonValueKind.Null) {
                    node.left = new TreeNode(arr[i].GetInt32());
                    queue.Enqueue(node.left);
                }
                i++;
            }
            if (i < arr.Length) {
                if (arr[i].ValueKind != System.Text.Json.JsonValueKind.Null) {
                    node.right = new TreeNode(arr[i].GetInt32());
                    queue.Enqueue(node.right);
                }
                i++;
            }
        }
        return root;
    }

    public static System.Collections.Generic.List<int?> SerializeTree(TreeNode root) {
        var outList = new System.Collections.Generic.List<int?>();
        if (root == null) return outList;
        outList.Add(root.val);
        var queue = new System.Collections.Generic.Queue<TreeNode>();
        queue.Enqueue(root);
        while (queue.Count > 0) {
            var node = queue.Dequeue();
            foreach (var child in new[] { node.left, node.right }) {
                if (child == null) { outList.Add(null); }
                else { outList.Add(child.val); queue.Enqueue(child); }
            }
        }
        while (outList.Count > 0 && outList[outList.Count - 1] == null) outList.RemoveAt(outList.Count - 1);
        return outList;
    }
}
'''


@dataclass(frozen=True)
class CSharpFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: a plain static
    method on a non-public `Solution` class (mirrors Java's convention --
    C#, like Java, has no bare top-level functions outside top-level
    statements). `Solution` is not `public` for the same file-sharing
    reason as Java/C++'s (coexists in one file with the driver's own
    `Program` class).

    Missing/renamed method or wrong parameter types are C# COMPILE ERRORS
    (Roslyn's CS0103/CS1503 etc.), surfaced by runner.py as
    verdict="Compilation Error" via the same compile-once path as every
    other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{_csharp_type(p.type)} {p.name}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            params = ", ".join(
                f"{'ref ' if p.name == contract.mutates_argument else ''}{_csharp_type(p.type)} {p.name}"
                for p in contract.parameters
            )
            return_type = "void"
            body = ""
        else:
            return_type = _csharp_type(contract.return_type)
            body = f"        return {_csharp_default_return(contract.return_type)};\n"
        tree_prefix = _CSHARP_TREE_CLASS if _uses_tree(contract) else ""
        return (
            f"{tree_prefix}"
            f"class Solution {{\n"
            f"    public static {return_type} {contract.function_name}({params}) {{\n"
            f"{body}"
            f"    }}\n"
            f"}}\n"
        )

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        params_decl = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"__arg{idx}"
            decode = _csharp_decode_expr(p.type, f"__args.GetProperty({json.dumps(p.name)})")
            params_decl.append(f"        {_csharp_type(p.type)} {var} = {decode};")
            call_args.append(f"ref {var}" if p.name == contract.mutates_argument else var)

        raw_call = f"Solution.{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"        {raw_call};"
            result_expr = f"__arg{mutated_idx}"
        else:
            call_statement = ""
            result_expr = raw_call

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"AtlasHelpers.SerializeTree({result_expr})"
        else:
            json_ready_expr = result_expr

        tree_prefix = "" if "class TreeNode" in user_code else _CSHARP_TREE_CLASS

        # `using` directives are only legal before any type declaration in
        # the file (CS1529) -- unlike every other language here, they can't
        # just live inside the driver block that follows user_code; they
        # have to be the very first thing in the composed source.
        header = "using System;\nusing System.Text.Json;\n\n"

        driver = f'''
{_CSHARP_RUNTIME}

class Program {{
    static void Main() {{
        string inputText = Console.In.ReadToEnd();
        JsonElement __args = JsonDocument.Parse(inputText).RootElement;

{chr(10).join(params_decl)}

{call_statement}
        var __result = {json_ready_expr};
        Console.WriteLine("{RESULT_SENTINEL}" + JsonSerializer.Serialize(__result));
    }}
}}
'''
        return f"{header}{tree_prefix}{user_code}\n\n{driver}"


def _csharp_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind == "array":
        return f"new {_csharp_type(spec)} {{}}"
    if spec.kind in ("optional", "tree"):
        return "null"
    if spec.kind == "tuple":
        assert spec.elements is not None
        return f"({', '.join(_csharp_default_return(e) for e in spec.elements)})"
    return "default"


# ── Go ───────────────────────────────────────────────────────────────────────
# Sixth compiled adapter. Toolchain installed THIS session (mission Phase 7:
# was TOOLCHAIN_UNAVAILABLE in the original probe -- docs/atlascode-
# toolchain-report.json -- go.dev's official zip extracted to a fresh GOROOT,
# separate from the default GOPATH to avoid the two colliding, since this
# environment has no package manager (no winget/choco/scoop) to handle that
# automatically). Uses the same compile-once PREPARERS path as every other
# compiled adapter (`_prepare_go` in notebook.py, `go build` once, rerun the
# resulting .exe per case).
#
# Like C#/Perl, leans on the standard library's real JSON support
# (`encoding/json`) instead of a hand-rolled parser -- Unmarshal/Marshal
# handle arbitrary array nesting and scalars generically. Unlike C#/Perl, Go
# has no native tuple type (same gap as C, for the same reason: no generics-
# free way to represent a fixed-width heterogeneous record without a
# generated per-contract struct) -- min-stack-simulation is excluded here
# too, an honest temporary gap matching C's.
#
# Go's DECLARE-then-Unmarshal idiom means decode is STATEMENTS, not a single
# expression like every interpreted/std-json-backed adapter above -- closer
# to C's statement-based approach than to C#/Perl/Rust/C++'s expression
# builders, but each statement is just one Unmarshal call (Go's own stdlib
# does the recursive array/nesting work), not a hand-written loop.

# (import path, detection substring) -- checked against the user's raw
# source text. Bounded to the packages a typical LeetCode-style algorithm
# solution plausibly needs (sort/search, string building, math, common
# containers); not an exhaustive stdlib list.
_GO_OPTIONAL_PACKAGES: list[tuple[str, str]] = [
    ("sort", "sort."),
    ("strconv", "strconv."),
    ("strings", "strings."),
    ("math", "math."),
    ("unicode", "unicode."),
    ("container/heap", "heap."),
    ("container/list", "list."),
    ("bytes", "bytes."),
    ("errors", "errors."),
]


def _go_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "int"
    if spec.kind == "float":
        return "float64"
    if spec.kind == "boolean":
        return "bool"
    if spec.kind == "string":
        return "string"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"*{_go_type(spec.items)}"
    if spec.kind == "array":
        assert spec.items is not None
        return f"[]{_go_type(spec.items)}"
    if spec.kind == "tree":
        return "*TreeNode"
    if spec.kind == "tuple":
        raise ValueError("Go Function Mode does not support tuple-typed contracts yet (see module docstring)")
    raise ValueError(f"unsupported TypeSpec for Go: {spec}")


def _go_decode_stmt(spec: TypeSpec, raw_expr: str, var_name: str) -> str:
    """Go statement(s) declaring `var_name` and populating it from `raw_expr`
    (a `json.RawMessage`). Tree is the only shape needing a second step
    (build the node graph from a decoded `[]*int` BFS array) -- everything
    else is one `json.Unmarshal` call, since encoding/json already handles
    arbitrary array nesting and scalar types generically."""
    if spec.kind == "tree":
        return (
            f"var {var_name}Raw []*int\n"
            f"json.Unmarshal({raw_expr}, &{var_name}Raw)\n"
            f"{var_name} := atlasBuildTree({var_name}Raw)\n"
        )
    go_type = _go_type(spec)
    return f"var {var_name} {go_type}\njson.Unmarshal({raw_expr}, &{var_name})\n"


_GO_TREE_STRUCT = (
    "type TreeNode struct {\n"
    "\tVal   int       `json:\"val\"`\n"
    "\tLeft  *TreeNode `json:\"left\"`\n"
    "\tRight *TreeNode `json:\"right\"`\n"
    "}\n\n"
)

# Shared runtime: only what encoding/json doesn't give for free -- tree
# build/serialize (structural, not a JSON built-in concept in any
# language's standard library).
_GO_RUNTIME = r'''
func atlasBuildTree(arr []*int) *TreeNode {
	if len(arr) == 0 || arr[0] == nil {
		return nil
	}
	root := &TreeNode{Val: *arr[0]}
	queue := []*TreeNode{root}
	i := 1
	for len(queue) > 0 && i < len(arr) {
		node := queue[0]
		queue = queue[1:]
		if i < len(arr) {
			if arr[i] != nil {
				node.Left = &TreeNode{Val: *arr[i]}
				queue = append(queue, node.Left)
			}
			i++
		}
		if i < len(arr) {
			if arr[i] != nil {
				node.Right = &TreeNode{Val: *arr[i]}
				queue = append(queue, node.Right)
			}
			i++
		}
	}
	return root
}

func atlasSerializeTree(root *TreeNode) []*int {
	out := []*int{}
	if root == nil {
		return out
	}
	v := root.Val
	out = append(out, &v)
	queue := []*TreeNode{root}
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		children := []*TreeNode{node.Left, node.Right}
		for _, child := range children {
			if child == nil {
				out = append(out, nil)
			} else {
				cv := child.Val
				out = append(out, &cv)
				queue = append(queue, child)
			}
		}
	}
	for len(out) > 0 && out[len(out)-1] == nil {
		out = out[:len(out)-1]
	}
	return out
}
'''


@dataclass(frozen=True)
class GoFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: a plain
    top-level `func` -- Go, like Rust, has no bare-function restriction
    requiring a class/impl wrapper.

    A missing/renamed function, or wrong parameter types, is a genuine Go
    COMPILE ERROR (`undefined: name` / type mismatch), surfaced by
    runner.py as verdict="Compilation Error" via the same compile-once path
    as every other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name} {_go_type(p.type)}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            return_type = ""
            body = ""
        else:
            return_type = f" {_go_type(contract.return_type)}"
            body = f"\treturn {_go_default_return(contract.return_type)}\n"
        tree_prefix = _GO_TREE_STRUCT if _uses_tree(contract) else ""
        return (
            f"{tree_prefix}"
            f"func {contract.function_name}({params}){return_type} {{\n"
            f"{body}"
            f"}}\n"
        )

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        decode_stmts = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"arg{idx}"
            decode_stmts.append(
                self._decode_lookup(p.name, p.type, var)
            )
            call_args.append(var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"\t{raw_call}"
            result_source = f"arg{mutated_idx}"
        else:
            call_statement = f"\tresult := {raw_call}"
            result_source = "result"

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"atlasSerializeTree({result_source})"
        else:
            json_ready_expr = result_source

        tree_prefix = "" if "type TreeNode struct" in user_code else _GO_TREE_STRUCT

        driver = f'''
{_GO_RUNTIME}

func main() {{
\tinputBytes, _ := io.ReadAll(os.Stdin)
\tvar argsMap map[string]json.RawMessage
\tjson.Unmarshal(inputBytes, &argsMap)

{chr(10).join(decode_stmts)}
{call_statement}
\tencoded, _ := json.Marshal({json_ready_expr})
\tfmt.Println("{RESULT_SENTINEL}" + string(encoded))
}}
'''
        # Go hard-errors on an unused import ("imported and not used") --
        # unlike C++'s "include a broad common set, harmless if unused"
        # philosophy, Go can't just pre-import everything a solution might
        # plausibly need. Only add a package if the user's code actually
        # references it (same substring-detection approach notebook.py's
        # own `run_go` already uses for Program Mode's bare `fmt.` check --
        # generalized here to the other packages a LeetCode-style solution
        # commonly needs).
        extra_imports = "".join(
            f'\t"{pkg}"\n' for pkg, marker in _GO_OPTIONAL_PACKAGES if marker in user_code
        )
        header = f"package main\n\nimport (\n\t\"encoding/json\"\n\t\"fmt\"\n\t\"io\"\n\t\"os\"\n{extra_imports})\n\n"
        return f"{header}{tree_prefix}{user_code}\n\n{driver}"

    @staticmethod
    def _decode_lookup(param_name: str, spec: TypeSpec, var_name: str) -> str:
        # Indentation is cosmetic only -- `go build` doesn't require gofmt
        # formatting, just valid syntax.
        raw_expr = f"argsMap[{json.dumps(param_name)}]"
        return _go_decode_stmt(spec, raw_expr, var_name)


def _go_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind == "array":
        return "nil"
    if spec.kind == "tree":
        return "nil"
    return "nil"


# ── Kotlin ───────────────────────────────────────────────────────────────────
# Seventh compiled adapter. Toolchain (kotlinc) installed this session --
# was TOOLCHAIN_UNAVAILABLE in the original probe (no `kotlinc` binary
# found, though the `java` it needs was already present). Uses an EXISTING
# compile-once PREPARERS entry (`_prepare_kotlin` in notebook.py already
# existed for Program Mode before this session -- confirmed via `kotlinc
# main.kt -include-runtime -d main.jar` then `java -jar main.jar`, both
# proven working against this session's newly-installed kotlinc).
#
# Structurally closest to Java (same JVM target, same need for a hand-rolled
# JSON parser -- Kotlin's stdlib has no more built-in JSON support than
# Java's does), but genuinely simpler in two respects: no class/Solution
# wrapper needed (top-level `fun` is idiomatic Kotlin, same as Rust/Go), and
# tuple support comes essentially for free via Kotlin's built-in `Pair`
# type (no generated-per-contract-struct workaround like C, no boxed-Object[]
# workaround like Java) -- min-stack-simulation IS supported here.

def _kotlin_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "Int"
    if spec.kind == "float":
        return "Double"
    if spec.kind == "boolean":
        return "Boolean"
    if spec.kind == "string":
        return "String"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_kotlin_type(spec.items)}?"
    if spec.kind == "array":
        assert spec.items is not None
        return f"List<{_kotlin_type(spec.items)}>"
    if spec.kind == "tree":
        return "TreeNode?"
    if spec.kind == "tuple":
        assert spec.elements is not None
        if len(spec.elements) != 2:
            raise ValueError("Kotlin Function Mode only supports 2-element tuples (via Pair) -- corpus audit found no wider tuple shape")
        return f"Pair<{_kotlin_type(spec.elements[0])}, {_kotlin_type(spec.elements[1])}>"
    raise ValueError(f"unsupported TypeSpec for Kotlin: {spec}")


def _kotlin_decode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    if spec.kind == "integer":
        return f"atlasAsInt({value_expr})"
    if spec.kind == "float":
        return f"atlasAsDouble({value_expr})"
    if spec.kind == "boolean":
        return f"atlasAsBool({value_expr})"
    if spec.kind == "string":
        return f"atlasAsStr({value_expr})"
    if spec.kind == "tree":
        return f"atlasBuildTree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None and spec.items.kind == "integer"
        return f"atlasAsOptInt({value_expr})"
    if spec.kind == "tuple":
        assert spec.elements is not None
        row_var = f"row{_depth}"
        e0 = _kotlin_decode_expr(spec.elements[0], f"{row_var}[0]", _depth + 1)
        e1 = _kotlin_decode_expr(spec.elements[1], f"{row_var}[1]", _depth + 1)
        return f"(({value_expr}) as JVal.Arr).v.let {{ {row_var} -> Pair({e0}, {e1}) }}"
    if spec.kind == "array":
        assert spec.items is not None
        item_var = f"e{_depth}"
        inner = _kotlin_decode_expr(spec.items, item_var, _depth + 1)
        return f"atlasAsList({value_expr}) {{ {item_var} -> {inner} }}"
    raise ValueError(f"unsupported TypeSpec for Kotlin decode: {spec}")


_KOTLIN_TREE_CLASS = "class TreeNode(var v: Int, var left: TreeNode? = null, var right: TreeNode? = null)\n\n"

# Shared runtime: minimal JSON value type + parser + decode helpers + one
# generic `atlasToJson` encoder that dispatches on Kotlin's real runtime
# type (Int/Double/Boolean/String/List/Pair) -- unlike Perl/R, the JVM's
# actual boxed types are unambiguous at runtime, so ONE generic encoder
# suffices instead of a contract-driven recursive expression builder.
_KOTLIN_RUNTIME = r'''
sealed class JVal {
    object Null : JVal()
    data class Bool(val v: Boolean) : JVal()
    data class Num(val v: Double) : JVal()
    data class Str(val v: String) : JVal()
    data class Arr(val v: MutableList<JVal>) : JVal()
    data class Obj(val v: MutableMap<String, JVal>) : JVal()
}

class JParser(val s: String) {
    var i = 0
    fun ws() { while (i < s.length && s[i].isWhitespace()) i++ }
    fun parse(): JVal { ws(); return value() }
    fun value(): JVal {
        ws()
        return when (s[i]) {
            '{' -> obj()
            '[' -> arr()
            '"' -> JVal.Str(str())
            't' -> { i += 4; JVal.Bool(true) }
            'f' -> { i += 5; JVal.Bool(false) }
            'n' -> { i += 4; JVal.Null }
            else -> num()
        }
    }
    fun obj(): JVal {
        val m = LinkedHashMap<String, JVal>()
        i++; ws()
        if (s[i] == '}') { i++; return JVal.Obj(m) }
        while (true) {
            ws()
            val k = str()
            ws(); i++
            val v = value()
            m[k] = v
            ws()
            if (s[i] == ',') { i++; continue }
            i++; break
        }
        return JVal.Obj(m)
    }
    fun arr(): JVal {
        val l = mutableListOf<JVal>()
        i++; ws()
        if (s[i] == ']') { i++; return JVal.Arr(l) }
        while (true) {
            l.add(value())
            ws()
            if (s[i] == ',') { i++; continue }
            i++; break
        }
        return JVal.Arr(l)
    }
    fun str(): String {
        i++
        val sb = StringBuilder()
        while (s[i] != '"') {
            val c = s[i]
            if (c == '\\') {
                i++
                when (s[i]) {
                    'n' -> sb.append('\n')
                    't' -> sb.append('\t')
                    'r' -> sb.append('\r')
                    '"' -> sb.append('"')
                    '\\' -> sb.append('\\')
                    '/' -> sb.append('/')
                    'u' -> { sb.append(s.substring(i + 1, i + 5).toInt(16).toChar()); i += 4 }
                    else -> sb.append(s[i])
                }
            } else sb.append(c)
            i++
        }
        i++
        return sb.toString()
    }
    fun num(): JVal {
        val start = i
        while (i < s.length && (s[i].isDigit() || "+-.eE".indexOf(s[i]) >= 0)) i++
        return JVal.Num(s.substring(start, i).toDouble())
    }
}

fun atlasParse(s: String): JVal = JParser(s).parse()
fun atlasLookup(o: JVal, name: String): JVal = (o as JVal.Obj).v[name]!!

fun atlasAsInt(v: JVal): Int = (v as JVal.Num).v.toInt()
fun atlasAsDouble(v: JVal): Double = (v as JVal.Num).v
fun atlasAsBool(v: JVal): Boolean = (v as JVal.Bool).v
fun atlasAsStr(v: JVal): String = (v as JVal.Str).v
fun atlasAsOptInt(v: JVal): Int? = if (v is JVal.Null) null else atlasAsInt(v)
fun <T> atlasAsList(v: JVal, f: (JVal) -> T): List<T> = (v as JVal.Arr).v.map(f)

fun atlasBuildTree(v: JVal): TreeNode? {
    val arr = (v as JVal.Arr).v
    if (arr.isEmpty() || arr[0] is JVal.Null) return null
    val root = TreeNode(atlasAsInt(arr[0]))
    val queue = ArrayDeque<TreeNode>()
    queue.add(root)
    var i = 1
    while (queue.isNotEmpty() && i < arr.size) {
        val node = queue.removeFirst()
        if (i < arr.size) {
            if (arr[i] !is JVal.Null) {
                node.left = TreeNode(atlasAsInt(arr[i]))
                queue.add(node.left!!)
            }
            i++
        }
        if (i < arr.size) {
            if (arr[i] !is JVal.Null) {
                node.right = TreeNode(atlasAsInt(arr[i]))
                queue.add(node.right!!)
            }
            i++
        }
    }
    return root
}

fun atlasSerializeTree(root: TreeNode?): List<Int?> {
    val out = mutableListOf<Int?>()
    if (root == null) return out
    out.add(root.v)
    val queue = ArrayDeque<TreeNode>()
    queue.add(root)
    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        for (child in listOf(node.left, node.right)) {
            if (child == null) out.add(null)
            else { out.add(child.v); queue.add(child) }
        }
    }
    while (out.isNotEmpty() && out.last() == null) out.removeAt(out.size - 1)
    return out
}

fun atlasEscapeStr(s: String): String {
    val sb = StringBuilder("\"")
    for (c in s) {
        when (c) {
            '"' -> sb.append("\\\"")
            '\\' -> sb.append("\\\\")
            '\n' -> sb.append("\\n")
            '\r' -> sb.append("\\r")
            '\t' -> sb.append("\\t")
            else -> sb.append(c)
        }
    }
    sb.append("\"")
    return sb.toString()
}

fun atlasToJson(o: Any?): String {
    return when (o) {
        null -> "null"
        is Boolean -> if (o) "true" else "false"
        is Int -> o.toString()
        is Double -> o.toString()
        is String -> atlasEscapeStr(o)
        is List<*> -> "[" + o.joinToString(",") { atlasToJson(it) } + "]"
        is Pair<*, *> -> "[" + atlasToJson(o.first) + "," + atlasToJson(o.second) + "]"
        else -> throw RuntimeException("atlasToJson: unsupported type " + (o?.javaClass?.name ?: "null"))
    }
}
'''


@dataclass(frozen=True)
class KotlinFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: a plain
    top-level `fun` -- no class wrapper needed (Kotlin, like Rust/Go,
    allows top-level functions).

    A missing/renamed function, or wrong parameter types, is a genuine
    Kotlin COMPILE ERROR (`unresolved reference`), surfaced by runner.py as
    verdict="Compilation Error" via the same compile-once path as every
    other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name}: {_kotlin_type(p.type)}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            params = ", ".join(
                f"{p.name}: {'MutableList<Int>' if p.name == contract.mutates_argument else _kotlin_type(p.type)}"
                for p in contract.parameters
            )
            return_type = ""
            body = ""
        else:
            return_type = f": {_kotlin_type(contract.return_type)}"
            body = f"    return {_kotlin_default_return(contract.return_type)}\n"
        tree_prefix = _KOTLIN_TREE_CLASS if _uses_tree(contract) else ""
        return f"{tree_prefix}fun {contract.function_name}({params}){return_type} {{\n{body}}}\n"

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        decode_stmts = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"arg{idx}"
            decode = _kotlin_decode_expr(p.type, f"atlasLookup(argsObj, {json.dumps(p.name)})")
            if p.name == contract.mutates_argument:
                # A mutable-sort contract needs a genuinely mutable
                # collection -- MutableList, not the read-only List every
                # other array parameter decodes to.
                decode_stmts.append(f"    val {var} = atlasAsList(atlasLookup(argsObj, {json.dumps(p.name)})) {{ e -> atlasAsInt(e) }}.toMutableList()")
            else:
                decode_stmts.append(f"    val {var}: {_kotlin_type(p.type)} = {decode}")
            call_args.append(var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"    {raw_call}"
            result_source = f"arg{mutated_idx}"
        else:
            call_statement = f"    val result = {raw_call}"
            result_source = "result"

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"atlasSerializeTree({result_source})"
        else:
            json_ready_expr = result_source

        tree_prefix = "" if "class TreeNode" in user_code else _KOTLIN_TREE_CLASS

        driver = f'''
{_KOTLIN_RUNTIME}

fun main() {{
    val inputText = generateSequence(::readLine).joinToString("\\n")
    val argsObj = atlasParse(inputText)

{chr(10).join(decode_stmts)}
{call_statement}
    println("{RESULT_SENTINEL}" + atlasToJson({json_ready_expr}))
}}
'''
        return f"{tree_prefix}{user_code}\n\n{driver}"


def _kotlin_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind == "array":
        return "emptyList()"
    if spec.kind in ("optional", "tree"):
        return "null"
    return "nil"


# ── Scala ────────────────────────────────────────────────────────────────────
# Eighth compiled adapter. Toolchain (scala-cli) installed this session --
# was TOOLCHAIN_UNAVAILABLE in the original probe. Uses a NEW compile-once
# PREPARERS entry (`_prepare_scala` in notebook.py, added this session) --
# contradicts this codebase's prior documented assumption that scala-cli
# "compile+run as one indivisible step": `scala-cli --power package <src>
# -o <jar>` DOES have a real, isolable compile step (confirmed directly:
# ~2-3 min the very first time ever run on this machine, a one-time Maven
# dependency download for the Scala 3 compiler/runtime, but ~1.5s on every
# build after that cache is warm), then `java -jar <jar>` reruns the same
# artifact per case -- the exact same PreparedProgram pattern C#'s
# `dotnet build` fix already established this session.
#
# Structurally almost identical to Kotlin (both target the JVM, both need
# a hand-rolled JSON parser since neither's standard library includes one,
# both get tuple support natively -- Scala's built-in `(A, B)` tuple type
# instead of Kotlin's `Pair`). Scala 3's top-level `def` (a genuinely new
# Scala 3 feature vs Scala 2) means no class/object wrapper is needed,
# same as Kotlin/Rust/Go.

def _scala_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "Int"
    if spec.kind == "float":
        return "Double"
    if spec.kind == "boolean":
        return "Boolean"
    if spec.kind == "string":
        return "String"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"Option[{_scala_type(spec.items)}]"
    if spec.kind == "array":
        assert spec.items is not None
        return f"List[{_scala_type(spec.items)}]"
    if spec.kind == "tree":
        return "TreeNode"
    if spec.kind == "tuple":
        assert spec.elements is not None
        if len(spec.elements) != 2:
            raise ValueError("Scala Function Mode only supports 2-element tuples -- corpus audit found no wider tuple shape")
        return f"({_scala_type(spec.elements[0])}, {_scala_type(spec.elements[1])})"
    raise ValueError(f"unsupported TypeSpec for Scala: {spec}")


def _scala_decode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    if spec.kind == "integer":
        return f"atlasAsInt({value_expr})"
    if spec.kind == "float":
        return f"atlasAsDouble({value_expr})"
    if spec.kind == "boolean":
        return f"atlasAsBool({value_expr})"
    if spec.kind == "string":
        return f"atlasAsStr({value_expr})"
    if spec.kind == "tree":
        return f"atlasBuildTree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None and spec.items.kind == "integer"
        return f"atlasAsOptInt({value_expr})"
    if spec.kind == "tuple":
        assert spec.elements is not None
        row_var = f"row{_depth}"
        e0 = _scala_decode_expr(spec.elements[0], f"{row_var}(0)", _depth + 1)
        e1 = _scala_decode_expr(spec.elements[1], f"{row_var}(1)", _depth + 1)
        return f"{{ val {row_var} = atlasAsArr({value_expr}); ({e0}, {e1}) }}"
    if spec.kind == "array":
        assert spec.items is not None
        item_var = f"e{_depth}"
        inner = _scala_decode_expr(spec.items, item_var, _depth + 1)
        return f"atlasAsList({value_expr}, ({item_var}: JVal) => {inner})"
    raise ValueError(f"unsupported TypeSpec for Scala decode: {spec}")


_SCALA_TREE_CLASS = "class TreeNode(var v: Int, var left: TreeNode = null, var right: TreeNode = null)\n\n"

_SCALA_RUNTIME = r'''
enum JVal:
  case JNull
  case JBool(v: Boolean)
  case JNum(v: Double)
  case JStr(v: String)
  case JArr(v: scala.collection.mutable.ListBuffer[JVal])
  case JObj(v: scala.collection.mutable.LinkedHashMap[String, JVal])

class JParser(s: String):
  var i = 0
  def ws(): Unit = while i < s.length && s(i).isWhitespace do i += 1
  def parse(): JVal = { ws(); value() }
  def value(): JVal =
    ws()
    s(i) match
      case '{' => obj()
      case '[' => arr()
      case '"' => JVal.JStr(str())
      case 't' => i += 4; JVal.JBool(true)
      case 'f' => i += 5; JVal.JBool(false)
      case 'n' => i += 4; JVal.JNull
      case _ => num()
  def obj(): JVal =
    val m = scala.collection.mutable.LinkedHashMap[String, JVal]()
    i += 1; ws()
    if s(i) == '}' then
      i += 1
      JVal.JObj(m)
    else
      var cont = true
      while cont do
        ws()
        val k = str()
        ws(); i += 1
        val v = value()
        m(k) = v
        ws()
        if s(i) == ',' then i += 1
        else { i += 1; cont = false }
      JVal.JObj(m)
  def arr(): JVal =
    val l = scala.collection.mutable.ListBuffer[JVal]()
    i += 1; ws()
    if s(i) == ']' then
      i += 1
      JVal.JArr(l)
    else
      var cont = true
      while cont do
        l += value()
        ws()
        if s(i) == ',' then i += 1
        else { i += 1; cont = false }
      JVal.JArr(l)
  def str(): String =
    i += 1
    val sb = new StringBuilder()
    while s(i) != '"' do
      val c = s(i)
      if c == '\\' then
        i += 1
        s(i) match
          case 'n' => sb.append('\n')
          case 't' => sb.append('\t')
          case 'r' => sb.append('\r')
          case '"' => sb.append('"')
          case '\\' => sb.append('\\')
          case '/' => sb.append('/')
          case 'u' => sb.append(Integer.parseInt(s.substring(i + 1, i + 5), 16).toChar); i += 4
          case other => sb.append(other)
      else sb.append(c)
      i += 1
    i += 1
    sb.toString()
  def num(): JVal =
    val start = i
    while i < s.length && (s(i).isDigit || "+-.eE".contains(s(i))) do i += 1
    JVal.JNum(s.substring(start, i).toDouble)

def atlasParse(s: String): JVal = JParser(s).parse()
def atlasLookup(o: JVal, name: String): JVal = o match
  case JVal.JObj(m) => m(name)
  case _ => throw RuntimeException("not an object")
def atlasAsArr(v: JVal): scala.collection.mutable.ListBuffer[JVal] = v match
  case JVal.JArr(l) => l
  case _ => throw RuntimeException("expected array")

def atlasAsInt(v: JVal): Int = v match { case JVal.JNum(n) => n.toInt; case _ => throw RuntimeException("expected number") }
def atlasAsDouble(v: JVal): Double = v match { case JVal.JNum(n) => n; case _ => throw RuntimeException("expected number") }
def atlasAsBool(v: JVal): Boolean = v match { case JVal.JBool(b) => b; case _ => throw RuntimeException("expected bool") }
def atlasAsStr(v: JVal): String = v match { case JVal.JStr(s) => s; case _ => throw RuntimeException("expected string") }
def atlasAsOptInt(v: JVal): Option[Int] = v match { case JVal.JNull => None; case _ => Some(atlasAsInt(v)) }
def atlasAsList[T](v: JVal, f: JVal => T): List[T] = atlasAsArr(v).map(f).toList

def atlasBuildTree(v: JVal): TreeNode =
  val arr = atlasAsArr(v)
  if arr.isEmpty || arr(0) == JVal.JNull then null
  else
    val root = new TreeNode(atlasAsInt(arr(0)))
    val queue = scala.collection.mutable.Queue[TreeNode](root)
    var i = 1
    while queue.nonEmpty && i < arr.length do
      val node = queue.dequeue()
      if i < arr.length then
        if arr(i) != JVal.JNull then
          node.left = new TreeNode(atlasAsInt(arr(i)))
          queue.enqueue(node.left)
        i += 1
      if i < arr.length then
        if arr(i) != JVal.JNull then
          node.right = new TreeNode(atlasAsInt(arr(i)))
          queue.enqueue(node.right)
        i += 1
    root

def atlasSerializeTree(root: TreeNode): List[Option[Int]] =
  val out = scala.collection.mutable.ListBuffer[Option[Int]]()
  if root == null then out.toList
  else
    out += Some(root.v)
    val queue = scala.collection.mutable.Queue[TreeNode](root)
    while queue.nonEmpty do
      val node = queue.dequeue()
      for child <- List(node.left, node.right) do
        if child == null then out += None
        else
          out += Some(child.v)
          queue.enqueue(child)
    while out.nonEmpty && out.last.isEmpty do out.remove(out.length - 1)
    out.toList

def atlasEscapeStr(s: String): String =
  val sb = new StringBuilder("\"")
  for c <- s do
    c match
      case '"' => sb.append("\\\"")
      case '\\' => sb.append("\\\\")
      case '\n' => sb.append("\\n")
      case '\r' => sb.append("\\r")
      case '\t' => sb.append("\\t")
      case other => sb.append(other)
  sb.append("\"")
  sb.toString()

def atlasToJson(o: Any): String = o match
  case null => "null"
  case None => "null"
  case Some(x) => atlasToJson(x)
  case b: Boolean => if b then "true" else "false"
  case i: Int => i.toString
  case d: Double => d.toString
  case s: String => atlasEscapeStr(s)
  case l: List[?] => "[" + l.map(atlasToJson).mkString(",") + "]"
  case (a, b) => "[" + atlasToJson(a) + "," + atlasToJson(b) + "]"
  case other => throw RuntimeException("atlasToJson: unsupported " + other.getClass.getName)
'''


@dataclass(frozen=True)
class ScalaFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: a plain
    top-level `def` -- Scala 3 (unlike Scala 2) allows top-level functions
    outside any object/class, same as Kotlin/Rust/Go.

    A missing/renamed function, or wrong parameter types, is a genuine
    Scala COMPILE ERROR (`not found: value`/type mismatch), surfaced by
    runner.py as verdict="Compilation Error" via the same compile-once path
    as every other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        params = ", ".join(f"{p.name}: {_scala_type(p.type)}" for p in contract.parameters)
        if contract.mutates_argument is not None:
            params = ", ".join(
                f"{p.name}: {'scala.collection.mutable.ListBuffer[Int]' if p.name == contract.mutates_argument else _scala_type(p.type)}"
                for p in contract.parameters
            )
            return_type = "Unit"
            body = "  ()\n"
        else:
            return_type = _scala_type(contract.return_type)
            body = f"  {_scala_default_return(contract.return_type)}\n"
        tree_prefix = _SCALA_TREE_CLASS if _uses_tree(contract) else ""
        return f"{tree_prefix}def {contract.function_name}({params}): {return_type} =\n{body}"

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        decode_stmts = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"arg{idx}"
            if p.name == contract.mutates_argument:
                decode_stmts.append(
                    f"  val {var} = scala.collection.mutable.ListBuffer.from("
                    f"atlasAsList(atlasLookup(argsObj, {json.dumps(p.name)}), (e: JVal) => atlasAsInt(e)))"
                )
            else:
                decode = _scala_decode_expr(p.type, f"atlasLookup(argsObj, {json.dumps(p.name)})")
                decode_stmts.append(f"  val {var}: {_scala_type(p.type)} = {decode}")
            call_args.append(var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"  {raw_call}"
            result_source = f"arg{mutated_idx}.toList"
        else:
            call_statement = f"  val result = {raw_call}"
            result_source = "result"

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"atlasSerializeTree({result_source})"
        else:
            json_ready_expr = result_source

        tree_prefix = "" if "class TreeNode" in user_code else _SCALA_TREE_CLASS

        driver = f'''
{_SCALA_RUNTIME}

@main def atlasMain(): Unit =
  val inputText = scala.io.Source.stdin.mkString
  val argsObj = atlasParse(inputText)

{chr(10).join(decode_stmts)}
{call_statement}
  println("{RESULT_SENTINEL}" + atlasToJson({json_ready_expr}))
'''
        return f"{tree_prefix}{user_code}\n\n{driver}"


def _scala_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind == "array":
        return "List()"
    if spec.kind == "optional":
        return "None"
    if spec.kind == "tree":
        return "null"
    return "null"


# ── Swift (ninth compiled language) ───────────────────────────────────────────
# Toolchain (Swift 6.3.3 for Windows) installed this session; needed a
# separate Visual Studio Build Tools (C++ workload) install to get a working
# MSVC linker (`link.exe`) -- Swift on Windows targets the MSVC ABI, not a
# GNU one, so there is no MinGW-linker escape hatch of the kind that fixed
# Rust in this same environment. Contradicts nothing about the prior "no
# isolable compile step" style of assumption: `swiftc main.swift -o main.exe`
# was directly confirmed to have a real, isolable compile step (proven by
# fixing the SDKROOT/linker errors one at a time until a standalone .exe was
# produced) -- so, like C#/Scala's fixes this session, Swift gets a real
# `_prepare_swift` PREPARERS entry rather than reusing the existing
# `run_swift`'s `swift main.swift` (JIT-per-invocation script mode).
#
# Calling convention: a plain top-level `func` -- Swift, like Rust/Go/Kotlin/
# Scala, allows top-level functions outside any class/struct.
#
# JSON handling: Foundation's JSONSerialization (Windows Swift ships
# swift-corelibs-foundation) parses stdin generically -- confirmed via direct
# experiment that its `Any` results are NSNumber/__NSCFBoolean-boxed and that
# `as? Int` / `as? Double` / `as? Bool` all bridge correctly regardless, so
# decode helpers use permissive multi-cast fallbacks. JSONSerialization
# CANNOT be reused for the encode side, though: it hard-requires the
# top-level object be an Array or Dictionary (throws for a bare scalar
# return, e.g. contains_nearby_duplicate's Bool) -- confirmed this is a real
# Foundation restriction, not a workaround-able flag. Fixed the same way
# Kotlin/Scala's genuinely-JSON-parser-less standard libraries were fixed:
# a small hand-rolled recursive `atlasToJson` string builder, dispatching on
# native (non-NSNumber-boxed) Swift runtime type -- confirmed via direct
# experiment that native Int/Double/Bool have NO cross-cast ambiguity
# (`(5 as Any) as? Bool` is genuinely nil), unlike the NSNumber-boxed decode
# side, so the dispatch order is safe.
#
# Mutation semantics: Swift's Array is a value type (copy-on-write struct),
# so a plain function parameter can never propagate a mutation back to the
# caller -- unlike Kotlin/Scala/Go where the JVM/slice reference is shared
# for free. Swift's own idiomatic, standard-library-sanctioned answer to
# exactly this (see `swap(_:_:)`) is an `inout` parameter -- so the
# mutates_argument parameter is generated as `inout [Int]` and called as
# `&arg`, a genuinely natural Swift construct, not a forced abstraction.
#
# No tuple support yet: Swift tuples aren't Equatable/Codable/storable in a
# generic `[Any]` in any straightforward way (no protocol conformance is
# possible for tuple types), so -- consistent with the C and Go adapters'
# documented gap -- min-stack-simulation is excluded from Swift's ladder.

def _swift_type(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "Int"
    if spec.kind == "float":
        return "Double"
    if spec.kind == "boolean":
        return "Bool"
    if spec.kind == "string":
        return "String"
    if spec.kind == "optional":
        assert spec.items is not None
        return f"{_swift_type(spec.items)}?"
    if spec.kind == "array":
        assert spec.items is not None
        return f"[{_swift_type(spec.items)}]"
    if spec.kind == "tree":
        return "TreeNode?"
    if spec.kind == "tuple":
        raise ValueError("Swift Function Mode does not support tuple-typed contracts yet (see module docstring)")
    raise ValueError(f"unsupported TypeSpec for Swift: {spec}")


def _swift_decode_expr(spec: TypeSpec, value_expr: str, _depth: int = 0) -> str:
    if spec.kind == "integer":
        return f"atlasAsInt({value_expr})"
    if spec.kind == "float":
        return f"atlasAsDouble({value_expr})"
    if spec.kind == "boolean":
        return f"atlasAsBool({value_expr})"
    if spec.kind == "string":
        return f"atlasAsStr({value_expr})"
    if spec.kind == "tree":
        return f"atlasBuildTree({value_expr})"
    if spec.kind == "optional":
        assert spec.items is not None and spec.items.kind == "integer"
        return f"atlasAsOptInt({value_expr})"
    if spec.kind == "array":
        assert spec.items is not None
        item_var = f"e{_depth}"
        inner = _swift_decode_expr(spec.items, item_var, _depth + 1)
        return f"atlasAsList({value_expr}) {{ {item_var} in {inner} }}"
    raise ValueError(f"unsupported TypeSpec for Swift decode: {spec}")


_SWIFT_TREE_CLASS = (
    "final class TreeNode {\n"
    "    var v: Int\n"
    "    var left: TreeNode?\n"
    "    var right: TreeNode?\n"
    "    init(_ v: Int) { self.v = v; self.left = nil; self.right = nil }\n"
    "}\n\n"
)

# Shared runtime: decode helpers on top of JSONSerialization's `Any` (kept
# permissive -- see module docstring on the NSNumber-boxing experiment),
# tree build/serialize, and a hand-rolled `atlasToJson` encoder (required
# because JSONSerialization itself refuses to serialize a bare top-level
# scalar).
_SWIFT_RUNTIME = r'''
func atlasAsInt(_ v: Any) -> Int {
    if let i = v as? Int { return i }
    if let d = v as? Double { return Int(d) }
    if let n = v as? NSNumber { return n.intValue }
    fatalError("atlasAsInt: not a number")
}
func atlasAsDouble(_ v: Any) -> Double {
    if let d = v as? Double { return d }
    if let i = v as? Int { return Double(i) }
    if let n = v as? NSNumber { return n.doubleValue }
    fatalError("atlasAsDouble: not a number")
}
func atlasAsBool(_ v: Any) -> Bool {
    if let b = v as? Bool { return b }
    if let n = v as? NSNumber { return n.boolValue }
    fatalError("atlasAsBool: not a bool")
}
func atlasAsStr(_ v: Any) -> String {
    if let s = v as? String { return s }
    fatalError("atlasAsStr: not a string")
}
func atlasIsNull(_ v: Any) -> Bool { return v is NSNull }
func atlasAsOptInt(_ v: Any) -> Int? {
    if atlasIsNull(v) { return nil }
    return atlasAsInt(v)
}
func atlasAsList<T>(_ v: Any, _ f: (Any) -> T) -> [T] {
    let arr = v as! [Any]
    return arr.map(f)
}

func atlasBuildTree(_ v: Any) -> TreeNode? {
    let arr = v as! [Any]
    if arr.isEmpty || atlasIsNull(arr[0]) { return nil }
    let root = TreeNode(atlasAsInt(arr[0]))
    var queue: [TreeNode] = [root]
    var i = 1
    while !queue.isEmpty && i < arr.count {
        let node = queue.removeFirst()
        if i < arr.count {
            if !atlasIsNull(arr[i]) {
                node.left = TreeNode(atlasAsInt(arr[i]))
                queue.append(node.left!)
            }
            i += 1
        }
        if i < arr.count {
            if !atlasIsNull(arr[i]) {
                node.right = TreeNode(atlasAsInt(arr[i]))
                queue.append(node.right!)
            }
            i += 1
        }
    }
    return root
}

func atlasSerializeTree(_ root: TreeNode?) -> [Any] {
    var out: [Any] = []
    guard let root = root else { return out }
    out.append(root.v)
    var queue: [TreeNode] = [root]
    while !queue.isEmpty {
        let node = queue.removeFirst()
        for child in [node.left, node.right] {
            if let child = child {
                out.append(child.v)
                queue.append(child)
            } else {
                out.append(NSNull())
            }
        }
    }
    while let last = out.last, last is NSNull { out.removeLast() }
    return out
}

func atlasEscapeStr(_ s: String) -> String {
    var out = "\""
    for c in s {
        switch c {
        case "\"": out += "\\\""
        case "\\": out += "\\\\"
        case "\n": out += "\\n"
        case "\r": out += "\\r"
        case "\t": out += "\\t"
        default: out.append(c)
        }
    }
    out += "\""
    return out
}

func atlasToJson(_ o: Any) -> String {
    if o is NSNull { return "null" }
    if let b = o as? Bool { return b ? "true" : "false" }
    if let i = o as? Int { return String(i) }
    if let d = o as? Double { return String(d) }
    if let s = o as? String { return atlasEscapeStr(s) }
    if let arr = o as? [Any] { return "[" + arr.map(atlasToJson).joined(separator: ",") + "]" }
    fatalError("atlasToJson: unsupported type")
}
'''


class SwiftFunctionAdapter:
    """
    Compile-once Function Mode adapter. Calling convention: a plain
    top-level `func` -- no class/struct wrapper needed (Swift, like
    Rust/Go/Kotlin/Scala, allows top-level functions).

    A missing/renamed function, or wrong parameter types, is a genuine
    Swift COMPILE ERROR (`cannot find ... in scope`/type mismatch),
    surfaced by runner.py as verdict="Compilation Error" via the same
    compile-once path as every other compiled adapter.
    """

    def generate_starter(self, contract: FunctionContract) -> str:
        if contract.mutates_argument is not None:
            params = ", ".join(
                f"{p.name}: inout [Int]" if p.name == contract.mutates_argument else f"{p.name}: {_swift_type(p.type)}"
                for p in contract.parameters
            )
            return_type = ""
            body = ""
        else:
            params = ", ".join(f"{p.name}: {_swift_type(p.type)}" for p in contract.parameters)
            return_type = f" -> {_swift_type(contract.return_type)}"
            body = f"    return {_swift_default_return(contract.return_type)}\n"
        tree_prefix = _SWIFT_TREE_CLASS if _uses_tree(contract) else ""
        return f"{tree_prefix}func {contract.function_name}({params}){return_type} {{\n{body}}}\n"

    def compose_program(self, user_code: str, contract: FunctionContract) -> str:
        decode_stmts = []
        call_args = []
        for idx, p in enumerate(contract.parameters):
            var = f"arg{idx}"
            lookup = f"argsObj[{json.dumps(p.name)}]!"
            if p.name == contract.mutates_argument:
                decode_stmts.append(f"    var {var} = atlasAsList({lookup}) {{ e in atlasAsInt(e) }}")
                call_args.append(f"&{var}")
            else:
                decode = _swift_decode_expr(p.type, lookup)
                decode_stmts.append(f"    let {var}: {_swift_type(p.type)} = {decode}")
                call_args.append(var)

        raw_call = f"{contract.function_name}({', '.join(call_args)})"
        if contract.mutates_argument is not None:
            mutated_idx = contract.parameter_names.index(contract.mutates_argument)
            call_statement = f"    {raw_call}"
            result_source = f"arg{mutated_idx}"
        else:
            call_statement = f"    let result = {raw_call}"
            result_source = "result"

        if contract.mutates_argument is None and contract.return_type.kind == "tree":
            json_ready_expr = f"atlasSerializeTree({result_source})"
        else:
            json_ready_expr = result_source

        tree_prefix = "" if "class TreeNode" in user_code else _SWIFT_TREE_CLASS

        driver = f'''
{_SWIFT_RUNTIME}

let atlasInputData = FileHandle.standardInput.readDataToEndOfFile()
let argsObj = try! JSONSerialization.jsonObject(with: atlasInputData) as! [String: Any]

{chr(10).join(decode_stmts)}
{call_statement}
print("{RESULT_SENTINEL}" + atlasToJson({json_ready_expr}))
'''
        header = "import Foundation\n\n"
        return f"{header}{tree_prefix}{user_code}\n\n{driver}"


def _swift_default_return(spec: TypeSpec) -> str:
    if spec.kind == "integer":
        return "0"
    if spec.kind == "float":
        return "0.0"
    if spec.kind == "boolean":
        return "false"
    if spec.kind == "string":
        return '""'
    if spec.kind == "array":
        return "[]"
    if spec.kind in ("optional", "tree"):
        return "nil"
    return "nil"
