"""统一 coarse 标签空间重算 macro-F1（零算力，只用现有 confusion / per_cell）。

背景（Claude 2026-10-17 咨询结论）：
  三方法原本在不同标签空间与不同分母上报告 accuracy，主表把不可比的数字并列，
  然后以"不可直接排名"作为结论。基准测试的职责是把不可比变成可比。
  本脚本把三方法的预测统一映射到 config/heart-celltype-map-v1.tsv 的 coarse_level，
  在同一空间内重算 macro-F1 / accuracy / per-class F1 / majority 基线。

只读冻结件，输出写入新目录。
"""
import csv
import json
import pathlib
import sys
from collections import Counter, defaultdict

BASE = pathlib.Path("D:/projects/course5-prep")
FROZEN = BASE / "results" / "pilot-v1"
MAPPING = BASE / "config" / "heart-celltype-map-v1.tsv"
OUT = BASE / "results" / "phase-20261017" / "unified-coarse-macro-f1"

DIRS = ["human->mouse", "mouse->human", "human->zebrafish",
        "zebrafish->human", "mouse->zebrafish", "zebrafish->mouse"]

SP_PREFIX = {"human": "hu", "mouse": "mo", "zebrafish": "zf"}
PREFIX_SP = {v: k for k, v in SP_PREFIX.items()}


def load_mapping():
    """(species, source_label) -> (coarse_level, status)"""
    m = {}
    for row in csv.DictReader(open(MAPPING, encoding="utf-8-sig", newline=""), delimiter="\t"):
        key = (row["source_species"].strip(), row["source_label"].strip())
        m[key] = (row["coarse_level"].strip(), row["mapping_status"].strip())
    return m


def to_coarse(species, label, mapping):
    """把原始标签映射到 coarse；无映射或非 active 返回 None（排除）。"""
    if label is None:
        return None
    hit = mapping.get((species, str(label).strip()))
    if hit is None:
        return None
    coarse, status = hit
    if status != "active":
        return None
    return coarse if coarse else None


def macro_f1(pairs):
    """pairs: [(truth, pred)] -> (macro_f1, accuracy, per_class, n)"""
    n = len(pairs)
    if n == 0:
        return 0.0, 0.0, {}, 0
    correct = sum(1 for t, p in pairs if t == p)
    labels = sorted({t for t, _ in pairs} | {p for _, p in pairs})
    per = {}
    f1s = []
    for lab in labels:
        tp = sum(1 for t, p in pairs if t == lab and p == lab)
        fp = sum(1 for t, p in pairs if t != lab and p == lab)
        fn = sum(1 for t, p in pairs if t == lab and p != lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per[lab] = {"precision": round(prec, 4), "recall": round(rec, 4),
                    "f1": round(f1, 4), "support": tp + fn}
        f1s.append(f1)
    return round(sum(f1s) / len(f1s), 4), round(correct / n, 4), per, n


def majority_baseline(pairs):
    """多数类分类器：全预测最高频 truth 类；返回其 macro-F1 / accuracy。"""
    if not pairs:
        return 0.0, 0.0, None
    cnt = Counter(t for t, _ in pairs)
    maj = cnt.most_common(1)[0][0]
    fake = [(t, maj) for t, _ in pairs]
    mf1, acc, _, _ = macro_f1(fake)
    return mf1, acc, maj


# ---------------------------------------------------------------- loaders
def load_opca(direction, level="coarse"):
    """oPCA: confusion 已经是 coarse 空间（键形如 'adipocyte=>immune'）。"""
    src, tgt = direction.split("->")
    p = FROZEN / "ortholog-pca-v98" / "confusion" / f"{level}_{src}_to_{tgt}.json"
    if not p.exists():
        return None, "missing"
    conf = json.loads(p.read_text(encoding="utf-8"))
    pairs = []
    for k, v in conf.items():
        t, pr = k.split("=>")
        pairs.extend([(t, pr)] * v)
    return pairs, "confusion(coarse-native)"


def load_saturn(direction, mapping, level="coarse"):
    """SATURN v99: per_cell 有原始标签；confusion 也是原始标签空间。
    优先用 per_cell（可映射），否则用 confusion 的原始标签映射。"""
    src, tgt = direction.split("->")
    base = FROZEN / "saturn-v99" / "raw" / "recovered-20261001"

    # 1) 尝试 per_cell payload
    for cand in [base / "predictions" / f"{level}_{src}_to_{tgt}.json",
                 base / f"{level}_{src}_to_{tgt}.json"]:
        if cand.exists():
            data = json.loads(cand.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                pairs = []
                for r in data:
                    if not r.get("included", True):
                        continue
                    t = to_coarse(src, r.get("truth"), mapping)
                    p = to_coarse(tgt, r.get("prediction"), mapping)
                    if t and p:
                        pairs.append((t, p))
                return pairs, "per_cell"

    # 2) 退回 confusion（原始标签 -> coarse）
    cp = base / "confusion" / f"{level}_{src}_to_{tgt}.json"
    if not cp.exists():
        return None, "missing"
    conf = json.loads(cp.read_text(encoding="utf-8"))
    pairs = []
    for k, v in conf.items():
        t_raw, p_raw = k.split("=>")
        t = to_coarse(src, t_raw, mapping)
        p = to_coarse(tgt, p_raw, mapping)
        if t and p:
            pairs.extend([(t, p)] * v)
    return pairs, "confusion(remapped)"


def load_samap(direction, mapping, level="coarse"):
    """SAMap: per_cell 有原始标签（truth/prediction），direction 形如 'hu->mo'。"""
    src, tgt = direction.split("->")
    tag = f"{SP_PREFIX[src]}--{SP_PREFIX[tgt]}"
    p = FROZEN / "samap-v98" / "wdl-run" / "extracted" / f"{level}_{tag}.json"
    if not p.exists():
        return None, "missing"
    data = json.loads(p.read_text(encoding="utf-8"))
    pc = data.get("per_cell", [])
    if not pc:
        return None, "empty per_cell"
    pairs = []
    for r in pc:
        if not r.get("included", True):
            continue
        t = to_coarse(src, r.get("truth"), mapping)
        pr = to_coarse(tgt, r.get("prediction"), mapping)
        if t and pr:
            pairs.append((t, pr))
    return pairs, "per_cell"


def main():
    mapping = load_mapping()
    OUT.mkdir(parents=True, exist_ok=True)

    results = {}
    log = []
    for d in DIRS:
        results[d] = {}
        for method, loader in [("ortholog_pca", lambda x, m: load_opca(x)),
                               ("saturn_v99", load_saturn),
                               ("samap", load_samap)]:
            try:
                pairs, src = loader(d, mapping)
            except Exception as e:
                pairs, src = None, f"error:{e}"
            if pairs is None:
                results[d][method] = {"status": "unavailable", "reason": src}
                log.append(f"{d:22} {method:14} UNAVAILABLE ({src})")
                continue
            mf1, acc, per, n = macro_f1(pairs)
            mf1_maj, acc_maj, maj_label = majority_baseline(pairs)
            results[d][method] = {
                "status": "ok", "source": src, "n": n,
                "macro_f1": mf1, "accuracy": acc,
                "majority_macro_f1": mf1_maj, "majority_accuracy": acc_maj,
                "majority_label": maj_label,
                "beats_majority_macro_f1": mf1 > mf1_maj,
                "beats_majority_accuracy": acc > acc_maj,
                "per_class": per,
            }
            log.append(
                f"{d:22} {method:14} n={n:5d} macroF1={mf1:.4f} (maj {mf1_maj:.4f}) "
                f"acc={acc:.4f} (maj {acc_maj:.4f})  "
                f"{'ABOVE' if mf1 > mf1_maj else 'below'} majority[macroF1]"
            )

    (OUT / "unified-coarse-macro-f1.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "run.log").write_text("\n".join(log) + "\n", encoding="utf-8")

    print("\n".join(log))
    print(f"\nwrote {OUT / 'unified-coarse-macro-f1.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
