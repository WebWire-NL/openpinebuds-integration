#!/usr/bin/env python3
"""Reconstruct C prototypes for functions the blobs define, from their DWARF.

Turns the debug info the vendor left in place back into a header: return type,
parameter names and types, declaration line, and the source file it came from.
Writes docs/anc-prototypes.md. Only metadata is read; no code is decompiled.

Usage: dwarf_protos.py [lib.a] [object-regex] [out.md]
"""
import re, subprocess, sys, pathlib, tempfile

DIE = re.compile(r"^\s*<(\d+)><([0-9a-f]+)>:\s+Abbrev Number:\s+\d+\s+\((DW_TAG_\w+)\)")
ATTR = re.compile(r"^\s*<([0-9a-f]+)>\s+(DW_AT_\w+)\s*:\s*(.*?)\s*$")

def clean(v):
    v = re.sub(r"^\((?:indirect )?(?:line )?string, offset: [^)]*\):\s*", "", v.strip())
    return re.sub(r"\s*\((?:ANSI C99|ISO C\+\+[^)]*)\)\s*$", "", v).strip()

def ref(v):
    m = re.search(r"<0x([0-9a-f]+)>", v or "")
    return int(m.group(1), 16) if m else None

def parse(obj):
    """Read one object's .debug_info into a flat list of DIEs with parent links."""
    out = subprocess.run(["readelf", "--debug-dump=info", str(obj)],
                         capture_output=True, text=True, errors="replace").stdout
    dies, stack, cur = [], [], None
    for ln in out.splitlines():
        m = DIE.match(ln)
        if m:
            depth, off, tag = int(m.group(1)), int(m.group(2), 16), m.group(3)
            while stack and stack[-1][0] >= depth:
                stack.pop()
            dies.append({"depth": depth, "off": off, "tag": tag, "attrs": {},
                         "parent": stack[-1][2] if stack else None})
            stack.append((depth, off, len(dies) - 1))
            cur = len(dies) - 1
            continue
        if cur is not None:
            a = ATTR.match(ln)
            if a:
                dies[cur]["attrs"][a.group(2)] = a.group(3)
    return dies, {d["off"]: d for d in dies}

def typename(by_off, off, depth=0, seen=()):
    if off is None or depth > 8 or off in seen:
        return "void" if off is None else "..."
    d = by_off.get(off)
    if d is None:
        return "?"
    t, a = d["tag"], d["attrs"]
    nm = clean(a.get("DW_AT_name", ""))
    inner = lambda: typename(by_off, ref(a.get("DW_AT_type", "")), depth + 1, seen + (off,))
    if t in ("DW_TAG_base_type", "DW_TAG_typedef"):
        return nm or "?"
    if t == "DW_TAG_pointer_type":
        return inner() + " *"
    if t == "DW_TAG_const_type":
        return "const " + inner()
    if t == "DW_TAG_volatile_type":
        return "volatile " + inner()
    if t == "DW_TAG_structure_type":
        return "struct " + (nm or "?")
    if t == "DW_TAG_union_type":
        return "union " + (nm or "?")
    if t == "DW_TAG_enumeration_type":
        return "enum " + (nm or "?")
    if t == "DW_TAG_array_type":
        return typename(by_off, ref(a.get("DW_AT_type", "")), depth + 1, seen + (off,)) + "[]"
    if t == "DW_TAG_subroutine_type":
        return typename(by_off, ref(a.get("DW_AT_type", "")), depth + 1, seen + (off,)) + " (*)()"
    return nm or ("void" if t == "DW_TAG_unspecified_type" else "?")

def prototypes(obj):
    """Return (source_file, [prototype dicts], unresolved_count) for one object file."""
    dies, by_off = parse(obj)
    cu = next((d for d in dies if d["tag"] == "DW_TAG_compile_unit"), None)
    source = clean(cu["attrs"].get("DW_AT_name", "")) if cu else ""
    out, unresolved = [], 0
    for i, d in enumerate(dies):
        if d["tag"] != "DW_TAG_subprogram" or "DW_AT_name" not in d["attrs"]:
            continue
        if "DW_AT_declaration" in d["attrs"]:      # external decl, not code this blob defines
            continue
        a = d["attrs"]
        ret = typename(by_off, ref(a["DW_AT_type"]) if "DW_AT_type" in a else None)
        if ret == "?":
            unresolved += 1
        args = []
        for c in dies:
            if c["parent"] != i:
                continue
            if c["tag"] == "DW_TAG_unspecified_parameters":
                args.append({"type": "...", "name": ""})
            elif c["tag"] == "DW_TAG_formal_parameter":
                args.append({"type": typename(by_off, ref(c["attrs"]["DW_AT_type"])
                                              if "DW_AT_type" in c["attrs"] else None),
                             "name": clean(c["attrs"].get("DW_AT_name", ""))})
        out.append({"name": clean(a["DW_AT_name"]), "return": ret, "args": args,
                    "static": "DW_AT_external" not in a,
                    "line": int(a["DW_AT_decl_line"]) if a.get("DW_AT_decl_line", "").isdigit() else None})
    return source, out, unresolved

def fmt(p):
    args = ", ".join((x["type"] + " " + x["name"]).strip() if x["name"] else x["type"] for x in p["args"])
    return (f"{'static ' if p['static'] else ''}{p['return']} {p['name']}"
            f"({args or 'void'})")

def main():
    lib = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                       "/tmp/opb/services/multimedia/lib/best2300p_libmultimedia_cp_anc.a")
    filt = re.compile(sys.argv[2] if len(sys.argv) > 2 else
                      r"(anc|adj_mc|iir|fft|eq|drc|wind|denoise|speech|vqe|dsp)")
    out_path = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else \
        pathlib.Path(__file__).resolve().parent.parent / "docs" / "anc-prototypes.md"
    members = subprocess.run(["ar", "t", str(lib)], capture_output=True, text=True).stdout.split()
    objs = [m for m in members if filt.search(m)]
    tmp = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(["ar", "x", str(lib)], cwd=tmp, check=True)
    total, nres, sources, body = 0, 0, set(), []
    for o in objs:
        if not (tmp / o).exists():
            continue
        src, protos, un = prototypes(tmp / o)
        if not protos:
            continue
        total += len(protos); nres += un; sources.add(src)
        body.append((o, src, [fmt(p) + f";  // line {p['line']}" for p in protos]))
    body.sort()
    L = [f"# Prototypes reconstructed from the blobs' DWARF ({__import__('datetime').date.today().isoformat()})",
         "", f"Source: `{lib.relative_to(lib.parents[3]) if len(lib.parents) > 3 else lib}` "
         f"({len(objs)} matching objects of {len(members)}), {total} function definitions, "
         f"{nres} with an unresolvable return type.",
         "Generated by `scripts/dwarf_protos.py`. This is what the vendor's `-g` build leaves behind:",
         "enough to write a compatible header, not enough to recover the code body.", "",
         "Source files the objects came from:", ""]
    L += [f"- `{s}`" for s in sorted(sources)]
    for o, src, protos in body:
        L += ["", f"## `{o}`", "", f"compiled from `{src}`", "", "```c"] + protos + ["```"]
    out_path.write_text("\n".join(L) + "\n")
    print(f"{len(objs)} objects, {total} prototypes, {nres} unresolved returns, {len(sources)} source files")

if __name__ == "__main__":
    main()
