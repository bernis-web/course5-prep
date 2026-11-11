# -*- coding: utf-8 -*-
"""给每个 CURRENT 文件的每个命中打出上下文，判定「现值」还是「引用」。

这是最终一致性回执：不是"扫到了"，而是"每个命中都看过上下文并定过性"。
"""
import re
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
STALE = ["0.6500", "0.6510", "0.4560", "0.4588", "0.4147", "0.4010", "0.2479", "0.4021",
         "0.1269", "0.1640", "0.3658", "0.3563", "0.1654", "0.1512", "0.2177", "0.4405",
         "0.0428", "0.1882", "0.1940"]
CTX = ["旧值", "原（错）", "原口径", "旧口径", "（错）", "对照", "作废", "更正", "推翻", "错口径", "冻结值", "已废", "附录"]

FILES = [
    "deliverables/课题5-PPT制作交接包-20261110.docx",
    "deliverables/课题5-总交接文档-20261028.docx",
    "deliverables/课题5-汇报-v5-20261111.pptx",
    "deliverables/课题5-组员交接总纲-20261104.docx",
    "deliverables/课题5-组员入门手册-20261104.docx",
    "deliverables/课题5-组员汇报说明-小白版-20261110.docx",
    "deliverables/课题5-老师七条意见回应-20261030.docx",
    "docs/execution/20261028-master-handoff.md",
    "docs/execution/20261104-队友交接总纲.md",
    "docs/execution/20261111-repro-manifest.md",
    "docs/team-handbook/part1-问题与方法.md",
    "docs/team-handbook/part2-口径陷阱与三场景.md",
    "docs/team-handbook/part3-可复现与FAQ.md",
    "docs/team-handbook/part4-汇报说明小白版.md",
]


def blocks_of(p: Path):
    suf = p.suffix.lower()
    if suf == ".md":
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        # markdown 表格：数据行继承表头上下文（表头|方向|约定A（冻结）|… 才让数据行算引用）
        out, hdr = [], ""
        for ln in lines:
            t = ln.strip()
            if t.startswith("|"):
                if not hdr:
                    hdr = t
                out.append(f"[表 {hdr[:70]}] {ln}")
            else:
                if t and not t.startswith("|"):
                    hdr = ""
                out.append(ln)
        return out
    if suf == ".docx":
        from docx import Document
        d = Document(str(p))
        out = [x.text for x in d.paragraphs]
        # 表格：把表头拼进每个单元格的上下文，否则「旧值」列的数据格会被当成现值
        for tb in d.tables:
            hdr = " ".join(c.text for c in tb.rows[0].cells) if len(tb.rows) else ""
            for r in list(tb.rows)[1:]:
                for c in r.cells:
                    out.append(f"[表 {hdr[:60]}] {c.text}")
        return out
    if suf == ".pptx":
        from pptx import Presentation
        prs = Presentation(str(p))
        out = []
        for i, s in enumerate(prs.slides):
            for sh in s.shapes:
                if sh.has_text_frame:
                    out.append(f"[页{i+1}] {sh.text_frame.text}")
                if sh.has_chart:
                    for ser in sh.chart.plots[0].series:
                        try:
                            vals = ",".join(str(round(v, 4)) for v in ser.values if v is not None)
                            out.append(f"[页{i+1} 图] {ser.name}: {vals}")
                        except Exception:
                            pass
        return out
    return []


lines = ["# CURRENT 文件逐命中定性（2026-11-11）", "",
         "扫描器只能报「命中」，这份回执逐个命中看上下文，定性成「现值」还是「引用」。", "",
         "| 文件 | 命中 | 定性 | 上下文 |", "|---|---|---|---|"]
need_fix = []
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        lines.append(f"| `{rel}` | - | 文件不存在 | - |")
        continue
    rows = []
    for b in blocks_of(p):
        for s in STALE:
            if s in b:
                kind = "引用" if any(k in b for k in CTX) else "**现值**"
                if kind == "**现值**":
                    need_fix.append((rel, s, b.strip()[:60]))
                rows.append((s, kind, b.strip().replace("|", "/")[:56]))
    if not rows:
        lines.append(f"| `{rel}` | 0 | 已清零 | - |")
        continue
    seen = set()
    for s, kind, ctx in rows:
        key = (s, kind)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"| `{rel}` | {s} | {kind} | {ctx} |")

lines += ["", f"## 判为「现值」的命中（{len(need_fix)} 处，必须改）", ""]
for rel, s, ctx in need_fix[:400]:
    lines.append(f"- `{rel}` · **{s}** · {ctx}")
out = ROOT / "docs" / "reports" / "scan-current-context-20261111.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:10]))
print(f"\n判为现值: {len(need_fix)} 处；写出 {out}")
for rel, s, ctx in need_fix[:15]:
    print(f"  {rel} | {s} | {ctx[:50]}")