# -*- coding: utf-8 -*-
"""给「历史留档」类 .md 文件头插一行作废声明。

判据（来自 audit-consistency 1.2）：2026-11-08 之前定稿、已对外讲过/交过的版本 → 改数字等于篡改历史，
只加声明。现行件（v8 选型指南 / part1-3 / 已修 handoff / 索引 / 审计报告本身）不动。
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
STAMP = ("> ⚠️ **本节数字已作废（2026-11-11 标注）**：见 `docs/reports/number-index-20261111.md` "
         "与 `docs/execution/20261108-更正索引.md`。本文件按当时口径保留，不回改。")

STALE = ["0.6500", "0.6510", "0.4560", "0.4588", "0.4147", "0.4010", "0.2479", "0.4021",
         "0.1269", "0.1640", "0.3658", "0.3563", "0.1654", "0.1512", "0.2177", "0.4405",
         "0.0428", "0.1882", "0.1940", "459–1309", "459-1309"]

# 现行件 / 索引 / 审计 / 更正语境 —— 一律不回插
SKIP_DIRS = ["tmp", "node_modules", ".git", "wheelhouse", "_claude",
             "results/repro-20261111", "results/pairwise-20261111"]
SKIP_NAMES = {
    "number-index-20261111.md",
    "20261108-更正索引.md",
    "20261111-repro-manifest.md",
    "audit-round1-summary-20261111.md",
}
SKIP_PREFIX = ("audit-", "report-12-", "report-13-", "report-14-", "report-15-", "20261111-")
SKIP_PATH_PARTS = ("docs/team-handbook/part1", "docs/team-handbook/part2",
                   "docs/team-handbook/part3", "场景化选型指南-v8",
                   "docs/execution/20261028-master-handoff",
                   "docs/execution/20261104-队友交接总纲")


def is_hist(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(rel.startswith(d) for d in SKIP_DIRS):
        return False
    if any(s in rel for s in SKIP_PATH_PARTS):
        return False
    if path.name in SKIP_NAMES or path.name.startswith(SKIP_PREFIX):
        return False
    return True


def iter_md():
    """os.walk 而不是 rglob：仓库里有 junction/权限异常目录，rglob 会在 select_from 里直接抛。"""
    import os
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "node_modules", "wheelhouse", "__pycache__"}]
        for fn in filenames:
            if fn.endswith(".md"):
                yield Path(dirpath) / fn


def main(apply: bool) -> int:
    done, skipped = [], []
    for md in sorted(iter_md()):
        if not is_hist(md):
            continue
        try:
            txt = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits = sorted({s for s in STALE if s in txt})
        if not hits:
            continue
        head = "\n".join(txt.splitlines()[:6])
        if "已作废" in head or STAMP.split("\n")[0] in txt:
            skipped.append((md, "已有声明"))
            continue
        lines = txt.splitlines(keepends=True)
        ins = 0
        for i, ln in enumerate(lines):
            if ln.startswith("# "):
                ins = i + 1
                break
        lines.insert(ins, "\n" + STAMP + "\n")
        if apply:
            md.write_text("".join(lines), encoding="utf-8")
        done.append((md.relative_to(ROOT).as_posix(), len(hits), hits[:3]))

    print(f"=== {'已插入' if apply else '待插入（dry-run）'}: {len(done)} 个文件 ===")
    for rel, n, sample in done:
        print(f"  {rel}  ({n} 个作废值: {sample})")
    print(f"=== 跳过（已有声明）: {len(skipped)} ===")
    for rel, why in skipped:
        print(f"  {rel}  ← {why}")
    return 0


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)