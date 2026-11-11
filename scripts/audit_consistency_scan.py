# -*- coding: utf-8 -*-
"""仓库一致性扫描：找作废数字残留。
范围: 所有 .md / .docx / .pptx（排除 node_modules/.venv39/wheelhouse/tmp）+ deliverables & docs 下 .json
输出: D:/projects/course5-prep/results/audit-consistency-20261111/hits.json
"""
import json, os, re, sys, zipfile
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
EXCLUDE_DIRS = {"node_modules", ".venv39", "wheelhouse", "tmp", ".git", "__pycache__", ".pytest_cache",
                ".tmp-segs", ".tmp-dcs-chrome-profile", "_asr"}

# (id, label, regex)  —— 精确串 + 容错变体
PATTERNS = [
    ("V01", "0.4147", r"0\.4147"),
    ("V02", "0.4010", r"0\.4010"),
    ("V03", "0.2479", r"0\.2479"),
    ("V04", "0.4021", r"0\.4021"),
    ("V05", "0.6500", r"0\.6500"),
    ("V06", "0.6510", r"0\.6510"),
    ("V07", "0.4560", r"0\.4560"),
    ("V08", "0.4588", r"0\.4588"),
    ("V09", "0.0428", r"0\.0428"),
    ("V10", "0.1882", r"0\.1882"),
    ("V11", "0.1940", r"0\.1940"),
    ("V12", "865 个", r"865\s*个|\b865\b"),
    ("V13", "459–1309", r"459\s*[-–—~至]\s*1309"),
    ("V14", "29–87%", r"29\s*[-–—~至]\s*87\s*%"),
]
COMPILED = [(i, l, re.compile(rx)) for i, l, rx in PATTERNS]


def excluded(p: Path) -> bool:
    parts = set(p.parts)
    if parts & EXCLUDE_DIRS:
        return True
    low = str(p).lower()
    return any(x in low for x in ("\\node_modules\\", "\\.venv39\\", "\\wheelhouse\\", "\\tmp\\"))


def scan_text(text):
    out = []
    for pid, label, rx in COMPILED:
        n = len(rx.findall(text))
        if n:
            out.append({"id": pid, "label": label, "count": n})
    return out


def line_hits(text, base_line=1):
    """返回 [{line, ids:[...]}]"""
    rows = []
    lines = text.splitlines()
    for ln, line in enumerate(lines, start=base_line):
        ids = [pid for pid, label, rx in COMPILED if rx.search(line)]
        if ids:
            rows.append({"line": ln, "ids": ids, "text": line.strip()[:300]})
    return rows


def md_hits(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e)}
    return {"lines": line_hits(text)}


def docx_hits(path: Path):
    from docx import Document
    doc = Document(str(path))
    rows = []
    idx = 0
    for p in doc.paragraphs:
        idx += 1
        ids = [pid for pid, label, rx in COMPILED if rx.search(p.text)]
        if ids:
            rows.append({"loc": f"para#{idx}", "ids": ids, "text": p.text.strip()[:300]})
    for ti, table in enumerate(doc.tables, start=1):
        for ri, row in enumerate(table.rows, start=1):
            for ci, cell in enumerate(row.cells, start=1):
                t = cell.text
                ids = [pid for pid, label, rx in COMPILED if rx.search(t)]
                if ids:
                    rows.append({"loc": f"table{ti}!r{ri}c{ci}", "ids": ids, "text": t.strip()[:300]})
    # 页眉页脚/文本框
    for si, sec in enumerate(doc.sections, start=1):
        for hname, h in (("hdr", sec.header), ("ftr", sec.footer)):
            for p in h.paragraphs:
                ids = [pid for pid, label, rx in COMPILED if rx.search(p.text)]
                if ids:
                    rows.append({"loc": f"sec{si}!{hname}", "ids": ids, "text": p.text.strip()[:300]})
    return {"lines": rows}


def pptx_hits(path: Path):
    from pptx import Presentation
    prs = Presentation(str(path))
    rows = []
    for si, slide in enumerate(prs.slides, start=1):
        def walk(shapes, prefix=""):
            for sh in shapes:
                name = f"{prefix}{sh.shape_type}/{sh.name}"
                if sh.has_text_frame:
                    t = "\n".join(p.text for p in sh.text_frame.paragraphs)
                    ids = [pid for pid, label, rx in COMPILED if rx.search(t)]
                    if ids:
                        rows.append({"loc": f"slide{si}!{name}", "ids": ids, "text": t.strip().replace("\n", " | ")[:300]})
                if getattr(sh, "has_table", False) and sh.has_table:
                    for ri, row in enumerate(sh.table.rows, start=1):
                        for ci, cell in enumerate(row.cells, start=1):
                            t = cell.text_frame.text if cell.text_frame else ""
                            ids = [pid for pid, label, rx in COMPILED if rx.search(t)]
                            if ids:
                                rows.append({"loc": f"slide{si}!table!r{ri}c{ci}", "ids": ids, "text": t.strip()[:300]})
                if getattr(sh, "has_group", False) and sh.has_group:
                    walk(sh.shapes, prefix=name + "/")
        walk(slide.shapes)
        # 备注
        if slide.has_notes_slide:
            nt = slide.notes_slide.notes_text_frame.text
            ids = [pid for pid, label, rx in COMPILED if rx.search(nt)]
            if ids:
                rows.append({"loc": f"slide{si}!notes", "ids": ids, "text": nt.strip()[:300]})
    return {"lines": rows}


def json_hits(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e)}
    return {"lines": line_hits(text)}


def main():
    hits = []
    stats = {"md": 0, "docx": 0, "pptx": 0, "json": 0}
    for p in ROOT.rglob("*"):
        if not p.is_file() or excluded(p):
            continue
        suf = p.suffix.lower()
        rel = str(p.relative_to(ROOT))
        if suf == ".md":
            stats["md"] += 1
            r = md_hits(p)
        elif suf == ".docx":
            stats["docx"] += 1
            r = docx_hits(p)
        elif suf == ".pptx":
            stats["pptx"] += 1
            r = pptx_hits(p)
        elif suf == ".json":
            low = rel.lower()
            if not (low.startswith("deliverables\\") or low.startswith("docs\\")):
                continue
            stats["json"] += 1
            r = json_hits(p)
        else:
            continue
        rows = r.get("lines") or []
        if rows:
            hits.append({"file": rel, "type": suf[1:], "match_count": len(rows), "rows": rows})

    outdir = ROOT / "results" / "audit-consistency-20261111"
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {"stats": stats, "files_with_hits": len(hits), "hits": hits}
    (outdir / "hits.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # 汇总：每文件命中哪些 id
    print(f"scanned md={stats['md']} docx={stats['docx']} pptx={stats['pptx']} json={stats['json']}")
    print(f"files with hits: {len(hits)}")
    for h in sorted(hits, key=lambda x: x["file"]):
        ids = sorted({i for row in h["rows"] for i in row["ids"]})
        print(f"{h['file']}\t{h['type']}\t{h['match_count']}\t{','.join(ids)}")


if __name__ == "__main__":
    main()