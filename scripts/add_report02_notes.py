"""Add speaker notes to a COPY of report-02 PPTX (original is never modified).

Reads the walkthrough JSON, pulls the 9 per-page speech blocks, and writes them
into the notes pages of a new file. Output name carries a -备注版 suffix.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"E:/xwechat_files/wxid_2gvkgptwgs8b22_6b72/msg/file/2026-10/课题5第02次汇报_数字来源链_校模板(1).pptx")
FALLBACK_SRC = ROOT / "results" / "stage-reports-20261019" / "课题5第02次汇报_数字来源链_校模板.pptx"
CONTENT = ROOT / "docs" / "reports" / "report02-walkthrough-content.json"
OUT = ROOT / "results" / "stage-reports-20261019" / "课题5第02次汇报_数字来源链_校模板-备注版.pptx"

# Page-by-page extra cues that do NOT belong in the spoken script but help the
# presenter: timing, what to point at, and the one sentence to land.
CUES = {
    1: ("约 10 秒", "不要念副标题，说完口径声明就翻页。"),
    2: ("约 45 秒", "手指进度条从左到右划一下；不要逐行念表，只念「3 完成、2 进行中、2 未开始」。"),
    3: ("约 55 秒", "语速加快，重点是「改了什么」，不是「错在哪」。不要自我检讨超过 30 秒。"),
    4: ("约 60 秒", "顺着 8 个方框用手比一遍；落点句是「换任何一环的定义，百分比就会变」。"),
    5: ("约 80 秒", "这是全场最核心的一页，慢讲。先指 1,528/1,535，再指 15,869，最后指 1,297÷1,505。"),
    6: ("约 60 秒", "重点解释「为什么分母不是 1,535」；majority 那两个数（0.4817 / 0.0813）一定要念出来。"),
    7: ("约 55 秒", "拿「考纲」打比方：truth-only 只算考纲内的题，union 把超纲题也算进平均分。"),
    8: ("约 50 秒", "不要逐个念数字，只念每组最高的是谁，最后落到「没有全面赢家」。"),
    9: ("约 60 秒", "收尾页。三条限定语必须念完，然后说「跨门待跑，下次讲公平比较边界」结束。"),
}


def load_speeches() -> list[str]:
    spec = json.loads(CONTENT.read_text(encoding="utf-8"))
    out: list[str] = []
    for block in spec["blocks"]:
        if block["type"] == "speech":
            out.append(block["text"])
    return out


def main() -> int:
    src = SRC if SRC.exists() else FALLBACK_SRC
    if not src.exists():
        raise SystemExit(f"source pptx not found: {SRC} / {FALLBACK_SRC}")
    speeches = load_speeches()
    prs = Presentation(str(src))
    if len(speeches) != len(prs.slides):
        raise SystemExit(f"speech count {len(speeches)} != slide count {len(prs.slides)}")

    for idx, (slide, speech) in enumerate(zip(prs.slides, speeches), 1):
        timing, cue = CUES.get(idx, ("", ""))
        notes = slide.notes_slide.notes_text_frame
        notes.clear()
        p1 = notes.paragraphs[0]
        p1.text = f"【第 {idx} 页 · {timing}】{cue}"
        p2 = notes.add_paragraph()
        p2.text = ""
        p3 = notes.add_paragraph()
        p3.text = "口播（可直接念）："
        p4 = notes.add_paragraph()
        p4.text = speech

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"saved {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
