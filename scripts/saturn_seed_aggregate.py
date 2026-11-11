"""汇总多 seed 的 SATURN vs scVI 结果，判断六向全胜是否稳定

为什么要多 seed
--------------
seed=0 跑出六向全显著正 Δ（+0.23~+0.34）。这个结论与历史完全相反，
最需要排除的就是「只是一个幸运种子」。

判据（写死在脚本里，避免事后找理由）
--------------------------------
对每个方向，跨 seed 看 Δ 的符号与显著率：
  - 3/3 seed 都 SIG 且同号  → `robust`
  - 2/3 seed SIG 且同号     → `likely`
  - 其余                   → `unstable`
只有 `robust` 的方向才允许在论文里写成无条件主张。

用法
----
    python scripts/saturn_seed_aggregate.py
    python scripts/saturn_seed_aggregate.py --seeds 0 1 2 --out results/saturn-seeds-20261111
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv39" / "Scripts" / "python.exe"
EVAL = ROOT / "scripts" / "saturn_new_vs_scvi_same_protocol.py"
MAP = ROOT / "config" / "heart-celltype-map-v1.tsv"
DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]
CN = {"human": "人", "mouse": "鼠", "zebrafish": "斑马鱼"}


def dir_label(d: str) -> str:
    a, b = d.split("->")
    return f"{CN[a]}→{CN[b]}"


def find_final(run_dir: Path) -> Path | None:
    rd = run_dir / "saturn_results"
    if not rd.exists():
        return None
    cands = [p for p in rd.glob("*.h5ad")
             if "pretrain" not in p.name and "_ep_" not in p.name]
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--out", default=str(ROOT / "results" / "saturn-seeds-20261111"))
    args = ap.parse_args()

    od = Path(args.out)
    od.mkdir(parents=True, exist_ok=True)

    per_seed = {}
    for s in args.seeds:
        run_dir = ROOT / ("local_run_full" if s == 0 else f"local_run_seed{s}")
        h5 = find_final(run_dir)
        if h5 is None:
            print(f"seed={s}: 没找到最终 h5ad（{run_dir}）——跳过", flush=True)
            continue
        out_json = od / f"seed{s}.json"
        if out_json.exists():
            print(f"seed={s}: 已有结果，复用 {out_json.name}", flush=True)
        else:
            print(f"seed={s}: 评测 {h5.name}", flush=True)
            r = subprocess.run(
                [str(PY), str(EVAL), "--saturn-h5ad", str(h5),
                 "--map", str(MAP), "--out", str(od / f"run_seed{s}")],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0:
                print(f"  FAILED rc={r.returncode}\n{r.stdout[-800:]}\n{r.stderr[-800:]}", flush=True)
                continue
            src = od / f"run_seed{s}" / "saturn_new_vs_scvi.json"
            if src.exists():
                out_json.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        d = json.loads(out_json.read_text(encoding="utf-8"))
        per_seed[s] = d["directions"]

    if not per_seed:
        print("没有任何 seed 可用", flush=True)
        return 1

    print()
    hdr = f"{'方向':10s}" + "".join(f"{'seed'+str(s):>22s}" for s in per_seed)
    print(hdr)
    print("-" * len(hdr))

    agg = {}
    for d in DIRS:
        if not all(d in per_seed[s] for s in per_seed):
            continue
        cells, deltas, sigs = [], [], []
        for s in per_seed:
            p = per_seed[s][d]["vs_scvi"]
            dl = p.get("delta")
            sg = p.get("significant_at_95", False)
            deltas.append(dl)
            sigs.append(sg)
            cells.append(f"{dl:+.4f}{'*' if sg else ' '}")
        same_sign = all((x > 0) == (deltas[0] > 0) for x in deltas if x is not None)
        n_sig = sum(1 for x in sigs if x)
        if n_sig == len(per_seed) and same_sign:
            verdict = "robust"
        elif n_sig >= max(2, len(per_seed) - 1) and same_sign:
            verdict = "likely"
        else:
            verdict = "unstable"
        print(f"{dir_label(d):10s}" + "".join(f"{c:>22s}" for c in cells) + f"   {verdict}")
        agg[d] = {"deltas": deltas, "sig": sigs, "verdict": verdict,
                  "same_sign": same_sign, "n_sig": n_sig}

    out = {"seeds": list(per_seed), "directions": agg,
           "note": "robust = 所有 seed 都显著且同号；likely = 至少 n-1 个显著且同号；"
                   "只有 robust 允许写成无条件主张"}
    (od / "seed_summary.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    md = ["# SATURN vs scVI 多 seed 稳定性", "",
          f"> seed: {', '.join(str(s) for s in per_seed)}；`*` = 该 seed 下 95% CI 不含 0", "",
          "| 方向 | " + " | ".join(f"seed{s} Δ" for s in per_seed) + " | 判定 |",
          "|---|" + "---|" * len(per_seed) + "---|"]
    for d, a in agg.items():
        md.append(f"| {dir_label(d)} | " +
                  " | ".join(f"{x:+.4f}" if x is not None else "-" for x in a["deltas"]) +
                  f" | **{a['verdict']}** |")
    (od / "seed_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    n_robust = sum(1 for a in agg.values() if a["verdict"] == "robust")
    print(f"\nrobust 方向数: {n_robust}/{len(agg)}")
    print(f"wrote {od / 'seed_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())