# -*- coding: utf-8 -*-
"""全仓作废数字：细分类扫描 + 二进制历史件插声明。

角色（按证据判，不按文件名猜）：
  DATA     results/**            数值记录本体，不动
  RECORD   审计/复盘/更正索引    引用作废值是本职工作，不动
  QUOTE    命中窗口里有「旧值/原（错）/对照/作废/更正/推翻」→ 合法引用
  HISTORY  2026-11-08 前的交付件 加声明（md 已批量；docx/pptx 本轮插）
  CURRENT  其它活文件            命中必须为 0，否则改数
"""
import re
import zipfile
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
STALE = ["0.6500", "0.6510", "0.4560", "0.4588", "0.4147", "0.4010", "0.2479", "0.4021",
         "0.1269", "0.1640", "0.3658", "0.3563", "0.1654", "0.1512", "0.2177", "0.4405",
         "0.0428", "0.1882", "0.1940"]
CTX = ["旧值", "原（错）", "原口径", "（错）", "旧口径", "对照", "作废", "更正", "推翻", "错口径", "冻结值", "已废", "附录"]
SHORT = [(re.compile(r"分母[^\n]{0,20}459"), "旧分母"),
         (re.compile(r"459[^\n]{0,6}1309"), "旧分母区间"),
         (re.compile(r"865\s*个|Orthers\D{0,20}865|865\D{0,20}Orthers"), "Orthers 865"),
         (re.compile(r"300\s*倍"), "300 倍")]
SKIP = (".git", "node_modules", "wheelhouse", "__pycache__", ".venv39", ".tmp-", "tmp/",
        "repro-20261111-215553", "tr_render", "mh_render", "fr_render", "td_render", "docx_render")
BANNER = ("⚠️ 本文件数字已作废（2026-11-11 标注）：现行值见 docs/reports/number-index-20261111.md "
          "与 docs/execution/20261108-更正索引.md；本文件按当时口径保留，不回改。")


def hits_text(txt):
    out = set()
    for s in STALE:
        for m in re.finditer(re.escape(s), txt):
            w = txt[max(0, m.start() - 30): m.start() + 30]
            if any(k in w for k in CTX):
                continue
            out.add(s)
            break
    for rx, label in SHORT:
        if rx.search(txt):
            out.add(label)
    return sorted(out)


def hits_pptx(p):
    """只认 a:t 文本与 c:v 缓存值，避开 offset 与颜色码（004592 曾被误判）。"""
    z = zipfile.ZipFile(p)
    out = set()
    for n in z.namelist():
        if not (n.endswith(".xml") and ("slides/slide" in n or "charts/chart" in n or "notesSlides" in n)):
            continue
        x = z.read(n).decode("utf-8", errors="ignore")
        # 逐页判：只有整页文本都带引用标记才豁免
        texts = re.findall(r"<a:t>([^<]{1,160})</a:t>", x)
        vals = re.findall(r"<c:v>(-?[0-9.]+)</c:v>", x)
        blob = " | ".join(texts + vals)
        ctx_ok = any(k in " ".join(texts) for k in CTX)
        for s in STALE:
            if s in blob and not ctx_ok:
                out.add(s)
        for rx, label in SHORT:
            if rx.search(" ".join(texts)):
                out.add(label)
    return sorted(out)


def role(rel, name):
    if rel.startswith("results/"):
        return "DATA"
    if (name.startswith(("audit-", "report-", "final-state", "number-index", "20261108-更正索引",
                         "20261111-obsolete", "20261111-mainline", "20261104-1215", "20261111-1300"))
            or rel.startswith("_claude/")):
        return "RECORD"
    if name.startswith(("场景化选型指南-v1", "场景化选型指南-v2", "场景化选型指南-v3",
                        "场景化选型指南-v4", "场景化选型指南-v5", "场景化选型指南-v6",
                        "场景化选型指南-v7", "course5-final-report", "course5-final-presentation",
                        "course5-monday-presentation", "course5-progress-presentation",
                        "课题5第0", "课题5-项目说明文档-组员版", "课题5-汇报讲稿",
                        "课题5-汇报-讲故事版", "课题5-汇报-v3", "课题5-汇报-v4",
                        "20261015", "20261017", "20261018", "20261019", "20261023",
                        "report-0", "report-1", "unified-coarse", "scvi-cross")):
        return "HISTORY"
    return "CURRENT"


def stamp_binary_file(p: Path) -> bool:
    """docx 顶部插声明段；pptx 末尾加声明页。已有声明则跳过（幂等）。"""
    try:
        if p.suffix.lower() == ".docx":
            from docx import Document
            from docx.shared import Pt, RGBColor
            d = Document(str(p))
            if any("本文件数字已作废" in x.text for x in d.paragraphs[:8]):
                return True
            par = d.paragraphs[0]
            new = d.add_paragraph()
            run = new.add_run(BANNER)
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x92, 0x68, 0x12)
            par._p.addprevious(new._p)
            d.save(str(p))
            return True
        if p.suffix.lower() == ".pptx":
            from pptx import Presentation
            from pptx.util import Inches, Pt
            prs = Presentation(str(p))
            for s in prs.slides:
                for sh in s.shapes:
                    if sh.has_text_frame and "本文件数字已作废" in sh.text_frame.text:
                        return True
            s = prs.slides.add_slide(prs.slide_layouts[6])
            tb = s.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(1.6))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.text = BANNER
            tf.paragraphs[0].runs[0].font.size = Pt(16)
            prs.save(str(p))
            return True
    except Exception as e:
        print("  stamp fail:", p.name, e)
    return False


def main(stamp: bool):
    rows = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(rel.startswith(s) or f"/{s}" in rel for s in SKIP):
            continue
        if p.name.startswith("~$") or ".bak" in p.name:
            continue
        suf = p.suffix.lower()
        try:
            if suf in (".md", ".json"):
                hits = hits_text(p.read_text(encoding="utf-8", errors="ignore"))
            elif suf == ".docx":
                from docx import Document
                d = Document(str(p))
                # 逐段/逐格判：引用标记只对**同一段**生效，避免一处「旧值」豁免全篇
                blocks = [x.text for x in d.paragraphs]
                blocks += [c.text for tb in d.tables for r in tb.rows for c in r.cells]
                hits = sorted({h for b in blocks for h in hits_text(b)})
            elif suf == ".pptx":
                hits = hits_pptx(p)
            else:
                continue
        except Exception as e:
            rows.append((rel, "ERR", [str(e)[:40]], "待查"))
            continue
        if not hits:
            continue
        r = role(rel, p.name)
        act = {"DATA": "保留（数据本体）", "RECORD": "保留（引用/记录）"}.get(r, "")
        if r == "CURRENT":
            act = "需改数"
        elif r == "HISTORY":
            act = "已加声明" if (stamp and stamp_binary_file(p)) else ("加声明" if not stamp else "声明失败")
        rows.append((rel, r, hits, act))

    out = ROOT / "docs" / "reports" / "scan-all-stale-20261111.md"
    lines = ["# 全仓作废数字扫描与处置（2026-11-11）", "",
             "四类文件（.md / .docx / .pptx / .json）全仓扫，按证据分角色，逐文件给处置。",
             "判 `CURRENT` 的条件：既不是数据本体（results/）、也不是引用作废值的记录（审计/复盘/索引），",
             "且命中窗口 30 字内没有「旧值 / 原（错） / 对照 / 作废 / 更正 / 推翻」这些引用标记。",
             "", "| 文件 | 角色 | 命中 | 处置 |", "|---|---|---|---|"]
    cnt, bad = {}, []
    for rel, r, hits, act in rows:
        cnt[r] = cnt.get(r, 0) + 1
        if r == "CURRENT":
            bad.append(rel)
        lines.append(f"| `{rel}` | {r} | {len(hits)} | {act} |")
    lines += ["", "## 统计", ""] + [f"- {k}: {v} 个文件" for k, v in sorted(cnt.items())]
    lines += ["", f"## 仍属 CURRENT 的文件（{len(bad)} 个）", ""] + ([f"- `{b}`" for b in bad] or ["- 无"])
    lines += ["", "## 处置口径", "",
              "- DATA / RECORD：作废值是数据本体或引用对象，改它等于伪造记录 → 保留。",
              "- HISTORY：加声明（.md 顶部一行；.docx 首段；.pptx 末页声明页），数字不回改。",
              "- CURRENT：命中即为「活文件还在引用作废值」→ 改数。", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-14:]))
    print(f"\n写出 {out}")


if __name__ == "__main__":
    import sys
    main(stamp="--stamp" in sys.argv)