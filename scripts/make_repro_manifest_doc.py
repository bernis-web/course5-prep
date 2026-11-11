# -*- coding: utf-8 -*-
"""从真实 repro run 的 manifest.json 生成 docs/execution/20261111-repro-manifest.md。"""
import json
from pathlib import Path

R = Path(r"D:\projects\course5-prep")
m = json.load(open(R / "tmp/repro-run2/manifest.json", encoding="utf-8"))
env = m.get("environment", {}) or {}
git = env.get("git", {}) or {}

HEAD = [
    "# 一键复现实测清单（2026-11-11）", "",
    "## 目标", "",
    "证明本仓库的分析链能在**隔离沙箱**里从零跑通，不依赖本机 `results/` 的既有产物，",
    "并把每一步产物的 SHA256 固定下来——数字可复现，才敢写进汇报。", "",
    "## 原则", "",
    "- 沙箱里只放「跑得动这件事所必需」的文件，`wheelhouse/` 那 3.5 GB 蛋白嵌入与 torch wheel 一律不进去。",
    "- 每步独立子进程，回显直接写日志文件（不经管道解码），避免 Windows 控制台编码把 UTF-8 打断。",
    "- 判定标准不是「跑完了」，而是「退出码 0 **且** 产物哈希与基线一致」。", "",
    "## 怎么跑", "",
    "```powershell",
    "cd D:\\projects\\course5-prep",
    ".\\.venv39\\Scripts\\python.exe scripts\\reproduce_all.py --fast",
    "# 全量（含 heavy 步骤）",
    ".\\.venv39\\Scripts\\python.exe scripts\\reproduce_all.py",
    "# 只跑指定步骤",
    ".\\.venv39\\Scripts\\python.exe scripts\\reproduce_all.py --steps 07-12",
    "```", "",
    "## 实测结果（本次真实回显）", "",
    f"- 时间：{m.get('generated_at')}",
    f"- Python：{env.get('python')}",
    f"- git：`{git.get('branch')}` @ `{str(git.get('commit'))[:12]}`（dirty={git.get('dirty')}）",
    f"- 步骤：**{m.get('steps_ok')}/{m.get('steps_total')}** 通过，耗时 {m.get('duration_s')} s，退出码 {m.get('exit_code')}",
    f"- 失败步骤：{m.get('failed') or '无'}", "",
    "## 逐步骤", "",
    "| # | 步骤 | 脚本 | rc | 秒 | 产物（SHA256 前 8 位） |",
    "|---|---|---|---|---|---|",
]

rows = []
for s in m["steps"]:
    arts = "<br>".join(
        "{} `{}`".format(a["path"].split("/")[-1], a["sha256"][:8])
        for a in s.get("artifacts", []) if a.get("exists")) or "—"
    rows.append(f"| {s['id']} | {s['name']} | {s['script']} | {s['rc']} | {s['seconds']} | {arts} |")

TAIL = [
    "", "## 本轮修掉的两个沙箱缺陷（有回显为证）", "",
    "1. **`bootstrap_saturn_fixed.py` 在沙箱里崩**：`MAP_TSV` 收到相对路径后，",
    "   `Path(...).relative_to(ROOT)` 抛 `ValueError: 'config\\heart-celltype-map-v2.tsv' is not in the subpath of ...`。",
    "   修法：先 `resolve()` 再 `relative_to`，失败则回退到文件名。",
    "2. **`reproduce_all.py` 没把 env 里的相对路径绝对化**：沙箱子进程 cwd 是 root，",
    "   脚本按仓库相对路径解析就找不到文件（`FileNotFoundError: ...\\_sandbox\\results\\pairwise-20261111\\pairwise_corrected.json`）。",
    "   修法：凡是「看起来像路径且文件确实存在」的 env 值，统一提升为沙箱内绝对路径。",
    "",
    "修前 `完成 20/22，失败步骤: 10:convention_flip_check.py(rc=1), 16:bootstrap_saturn_fixed.py(rc=1)`；",
    "修后 `完成 22/22，全部步骤退出码 0`。", "",
    "## 坑", "",
    "- `--fast` 只跳过 heavy 步骤，**不减少抽样次数**；`--steps` 支持 `07-12` 这种区间写法。",
    "- 沙箱默认不保留（`--keep-sandbox` 才留），`tmp/repro-run*/` 里是最后一次运行的证据。",
    "- `h5ad-inspect` 的产物哈希会随文件时间戳变化，跨次比较看 `rc` 而不是看 SHA。",
    "- 全量模式（去掉 `--fast`）会调用 GPU 相关重训步骤；本机无 GPU，那几步按设计会跳过，不算失败。", "",
    "## 下一步", "",
    "- 全量模式跑一遍，确认 heavy 步骤也全绿。",
    "- 把本表 SHA 组写进汇报附件的「复现指纹」一栏，作为「数字不是手抄的」的证据。", "",
]

out = R / "docs" / "execution" / "20261111-repro-manifest.md"
out.write_text("\n".join(HEAD + rows + TAIL), encoding="utf-8")
print("wrote", out, out.stat().st_size, "bytes,", len(rows), "steps")