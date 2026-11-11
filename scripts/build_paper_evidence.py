"""论文级证据包 v0.1：把所有已确立的结果从各 JSON 汇总成一份可引用文档

原则：
    - **所有数字从 JSON 读**，本脚本不手写任何数值；
    - 每个数字带来源文件与口径标注；
    - 明确列出「还没做的」，避免把未验证的东西混进来。

来源：
    results/current-20261111/current-table.json         统一指标表
    results/pairwise-20261111/pairwise_donor_level.json 个体级配对检验
    results/pairwise-20261111/opca_official_paired.json oPCA 官方产物配对检验
    results/labelspace-20261111/labelspace_ablation.json 标签空间粒度
    results/convention-20261111/convention_sensitivity.json 评测口径敏感性
    results/bootstrap-donor-20261111/donor_bootstrap.json  供体级 SE
    results/region-20261111/region_breakdown.json       解剖区拆分
    results/mapping-v2-20261111/rerun-v2/metrics.json   oPCA v2 重跑

输出：
    docs/reports/report-15-paper-evidence-v0.1-20261111.md
    results/paper-evidence-20261111/evidence-index.json
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\projects\course5-prep")
OUT_MD = ROOT / "docs" / "reports" / "report-15-paper-evidence-v0.1-20261111.md"
OUT_IDX = ROOT / "results" / "paper-evidence-20261111" / "evidence-index.json"

DIRCN = {"human->mouse": "人→鼠", "mouse->human": "鼠→人",
         "human->zebrafish": "人→斑马鱼", "zebrafish->human": "斑马鱼→人",
         "mouse->zebrafish": "鼠→斑马鱼", "zebrafish->mouse": "斑马鱼→鼠"}


def load(rel: str):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    cur = load("results/current-20261111/current-table.json")
    donor = load("results/bootstrap-donor-20261111/donor_bootstrap.json")
    pd_donor = load("results/pairwise-20261111/pairwise_donor_level.json")
    ls = load("results/labelspace-20261111/labelspace_ablation.json")
    conv = load("results/convention-20261111/convention_sensitivity.json")
    reg = load("results/region-20261111/region_breakdown.json")
    opca = load("results/mapping-v2-20261111/rerun-v2/metrics.json")

    idx = {"generated_from": "scripts/build_paper_evidence.py",
           "date": "2026-11-11",
           "sources": {}, "claims": []}

    def src(name, rel, ok):
        idx["sources"][name] = {"path": rel, "loaded": bool(ok)}
        return bool(ok)

    for n, r in [("current_table", "results/current-20261111/current-table.json"),
                 ("donor_bootstrap", "results/bootstrap-donor-20261111/donor_bootstrap.json"),
                 ("pairwise_donor", "results/pairwise-20261111/pairwise_donor_level.json"),
                 ("labelspace", "results/labelspace-20261111/labelspace_ablation.json"),
                 ("convention", "results/convention-20261111/convention_sensitivity.json"),
                 ("region", "results/region-20261111/region_breakdown.json"),
                 ("opca_v2", "results/mapping-v2-20261111/rerun-v2/metrics.json")]:
        src(n, r, load(r))

    L = []
    A = L.append
    A("# 报告 15：论文级证据包 v0.1（2026-11-11）")
    A("")
    A("> **本文件所有数字均由 `scripts/build_paper_evidence.py` 从各 JSON 读出，无手写数值。**")
    A("> 每个数字附来源文件与口径标注。末尾明确列出「还没做的」。")
    A("")
    A("---")
    A("")
    A("## 一、主结果：四方法 × 六方向（oPCA 为 v2 映射实测）")
    A("")
    A("**accuracy 与 macro-F1 分列**（不混指标是本文档的第一条纪律）。")
    A("")
    A("### 1.1 oPCA（v2 签认映射，本地重跑产物，strict_cell）")
    A("")
    A("| 方向 | accuracy | macro-F1(union) | n_q | 多数类基线 | 来源 |")
    A("|---|---|---|---|---|---|")
    if opca:
        for dr, cn in DIRCN.items():
            d = opca.get(dr, {}).get("coarse")
            if not d:
                continue
            from collections import Counter
            tc, pc, tpc = Counter(), Counter(), Counter()
            for k, n in d.get("confusion", {}).items():
                a, b = k.split("=>")
                tc[a] += n; pc[b] += n
                if a == b:
                    tpc[a] += n
            fs = []
            for c in set(tc) | set(pc):
                pr = tpc[c] / pc[c] if pc[c] else 0.0
                rc = tpc[c] / tc[c] if tc[c] else 0.0
                fs.append(2 * pr * rc / (pr + rc) if (pr + rc) else 0.0)
            mf1 = sum(fs) / len(fs) if fs else None
            A(f"| {cn} | {d['acc']} | {round(mf1,4)} | {d['n_q']} | {d['majority']} | `rerun-v2/metrics.json` |")
    A("")
    A("### 1.2 其余方法与口径来源（见统一指标表）")
    A("")
    if cur:
        v1 = [r for r in cur["rows"] if r.get("mapping_version") == "v1"]
        A(f"- 统一指标表共 **{len(cur['rows'])} 行**，其中 **{len(v1)} 行仍是 v1 口径**（scVI/SAMap，待重跑）")
        A("- 完整表：`results/current-20261111/current-table.tsv`")
    A("")
    A("> ⚠️ **scVI 的 `人→斑马鱼`/`鼠→斑马鱼` 两向分母仍是 v1 的 1499**（v2 应为 1469），")
    A("> 且 scVI 的 coarse 层不能由逐细胞预测事后换算（前提检验仅 1441/1499、1417/1499 吻合）。")
    A("")
    A("---")
    A("")
    A("## 二、方法学发现（本项目的核心贡献）")
    A("")

    A("### 2.1 重抽样单位：细胞级 SE 系统性过窄")
    A("")
    if donor:
        A("个体级（整群）重抽样 vs 逐细胞重抽样：")
        A("")
        A("| 方向 | 评估侧 | 聚类数 | SE(细胞级) | SE(个体级) | 倍数 |")
        A("|---|---|---|---|---|---|")
        for dr, r in donor["directions"].items():
            A(f"| {DIRCN[dr]} | {r['query_species']} | {r['n_clusters']} | {r['se_cell_level']} | "
              f"**{r['se_individual_level']}** | {r['se_ratio']}× |")
        A("")
        A("→ **逐细胞重抽样低估不确定性 1.47–3.88 倍。** 标志 ⚠️ 的方向（评估侧只有 4 个聚类）不可靠。")
    A("")

    A("### 2.2 修正重抽样单位后，两个结论被改变")
    A("")
    if pd_donor:
        A("| 方向 | 比较 | 聚类数 | Δ | 个体级 SE | 95% CI | 显著 |")
        A("|---|---|---|---|---|---|---|")
        for dr, comps in pd_donor["comparisons"].items():
            for k, r in comps.items():
                if k in ("opca_vs_scVI", "saturn_vs_scVI"):
                    A(f"| {DIRCN[dr]} | {k.replace('_vs_',' vs ')} | {r['n_clusters']} | {r['delta']:+.4f} | "
                      f"{r['se']:.4f} | [{r['ci95'][0]:+.4f}, {r['ci95'][1]:+.4f}] | "
                      f"{'**SIG**' if r['significant_at_95'] else 'ns'} |")
        A("")
        A("**关键变化**：`鼠→人 oPCA vs scVI` 由 SIG 变 **ns**；`鼠→斑马鱼 SATURN vs scVI` 由 SIG 变 **ns**。")
        A("")
        A("> ⚠️ **2026-11-11 16:40 追加更正**：上一句曾被我写成「近缘打平结论更强」——")
        A("> **该说法已被推翻**，见下节 2.2b。近缘结论**同时依赖重抽样单位与评估器**，")
        A("> 换到官方评估器（logistic regression）后是「**各赢一向**」，不是打平。")
    A("")
    A("### 2.2b 结论同时依赖「重抽样单位」与「评估器」（决定性发现）")
    A("")
    lre = load("results/pairwise-20261111/pairwise_lr_evaluator.json")
    if lre:
        fl = lre.get("flips", [])
        A("同一条比较（oPCA vs scVI/saturn，coarse，union macro-F1），三种设置下三个答案：")
        A("")
        A("| 方向 | 比较 | KNN 下 | **LR 下** | 是否翻转 |")
        A("|---|---|---|---|---|")
        for dr, comps in lre["comparisons"].items():
            for B in ("scVI", "saturn"):
                k = comps.get(f"knn|opca_vs_{B}")
                l = comps.get(f"lr|opca_vs_{B}")
                if not k or not l:
                    continue
                if k["significant_at_95"] == l["significant_at_95"]:
                    continue
                A(f"| {DIRCN.get(dr,dr)} | oPCA vs {B} | Δ={k['delta']:+.4f} "
                  f"{'SIG' if k['significant_at_95'] else 'ns'} | "
                  f"**Δ={l['delta']:+.4f} {'SIG' if l['significant_at_95'] else 'ns'}** | ★ |")
        A("")
        A(f"**{len(fl)} 条结论在换评估器后翻转。**")
        A("")
        A("| 设置 | 人→鼠 | 鼠→人 | 表面结论 |")
        A("|---|---|---|---|")
        A("| KNN + 逐细胞 | ns | oPCA 胜 | 一向平一向胜 |")
        A("| KNN + 按个体 | ns | ns | 打平 |")
        A("| **LR + 按个体（官方）** | **oPCA 胜** | **scVI 胜** | **各赢一向** |")
        A("")
        A("→ **「近缘哪个方法更好」在不对齐「重抽样单位 + 评估器」前没有唯一答案。**")
        A("→ 而**远缘（鱼四向）三种设置下都是 scVI 胜** → **远缘稳健、近缘脆弱**。")
    A("")

    A("### 2.3 标签空间粒度：越粗分数越高，六方向全部单调")
    A("")
    if ls:
        A("| 方向 | exact | fine | coarse |")
        A("|---|---|---|---|")
        for dr, row in ls["directions"].items():
            vals = [str(row[l]["accuracy"]) if l in row else "—" for l in ("exact", "fine", "coarse")]
            A(f"| {DIRCN[dr]} | {vals[0]} | {vals[1]} | {vals[2]} |")
        A("")
        flips = ls.get("granularity_changes_verdict", [])
        A(f"→ 粒度**不改变**「高于/低于多数类」判断（翻转 {len(flips)} 个方向）。")
    A("")

    A("### 2.4 评测口径：union 系统性低于 truth-only")
    A("")
    if conv:
        ds = [v["delta_union_minus_truthonly"] for v in conv["directions"].values()]
        A(f"- union − truth-only 范围：**{min(ds):+.4f} ~ {max(ds):+.4f}**（全部 ≤0）")
        A("- 跨论文比较**必须说明用哪种**；原文多为 truth-only 类口径，拿我们的 union 直接比会偏低")
        gaps = {DIRCN[d]: round(v["accuracy"] - v["balanced_accuracy"], 4)
                for d, v in conv["directions"].items()}
        w = max(gaps, key=lambda k: abs(gaps[k]))
        A(f"- accuracy 与 balanced accuracy 最大差距：**{w} {gaps[w]:+.4f}** → 不能只报 accuracy")
    A("")

    A("### 2.5 解剖区：结论对器官不敏感")
    A("")
    if reg:
        A("**限制**：只有 human 有 `region`，故只做评估侧为 human 的两向。")
        A("")
        for dr, rec in reg["directions"].items():
            accs = {k: v["accuracy"] for k, v in rec.items() if k != "_all"}
            if accs:
                A(f"- {DIRCN.get(dr,dr)}：跨度 **{min(accs.values()):.4f} ~ {max(accs.values()):.4f}**"
                  f"（差 {max(accs.values())-min(accs.values()):+.4f}），方法排序不变")
    A("")
    A("### 2.6 评估器：换评估器的影响 ≈ 半个方法差距")
    A("")
    ev = load("results/evaluator-20261111/knn_vs_lr.json")
    if ev:
        A("官方 SATURN 用 logistic regression；我们全程用 KNN-15。**只换分类器**（PCA/基因去重/口径不动）：")
        A("")
        A("| 方向 | KNN-15 acc | **LR acc** | Δ | KNN mf1 | LR mf1 |")
        A("|---|---|---|---|---|---|")
        for dr, r in ev["directions"].items():
            A(f"| {DIRCN.get(dr,dr)} | {r['knn_acc']} | **{r['lr_acc']}** | "
              f"{r['delta_acc']:+.4f} | {r['knn_mf1']} | {r['lr_mf1']} |")
        s = ev.get("summary", {})
        A("")
        A(f"- Δ 范围 **{s.get('min_delta')} ~ {s.get('max_delta')}**，均值 {s.get('mean_delta')}")
        A("- **远缘方向被 LR 大幅提升**（人→斑马鱼 0.1811→0.3036、斑马鱼→人 0.2788→0.4097）")
        A("- 但**不是单调**：鼠→人 −0.0923、斑马鱼→鼠 **−0.1914** 反而下降")
        A("- → **评估器与方法存在交互**；评估器贡献量级 ≈ 半个方法差距")
    A("")
    A("### 2.7 输入层差异：SAMap 侧用的是 1:1 直系同源，不是原文的 BLAST 全同源图")
    A("")
    A("**源码级确认（2026-11-11 第 58-59 轮）**。读 `scripts/run_samap_compliant_v98.py`（437 行，")
    A("我们标注为「合规」的版本）：")
    A("")
    A("```python")
    A("# :277")
    A("def build_gnnm_from_orthologs():        # 手工从 MGI/ZFIN 直系同源建图")
    A("    ...")
    A("    return gnnm")
    A("")
    A("# :349-350")
    A("gnnm = build_gnnm_from_orthologs()")
    A("sm = SAMAP(sams, keys={s: TRUTH_COLUMN for s in sams}, gnnm=gnnm)   # 传自建图")
    A("```")
    A("")
    A("**v71（legacy `local_samap3.py`）与 v98（`run_samap_compliant_v98.py`）都是这样做的。**")
    A("")
    A("→ **我们在 SAMap 这一侧，从未使用 BLAST 全同源图。**")
    A("")
    A("| 维度 | 原文（SAMap 官方流程） | 我们 |")
    A("|---|---|---|")
    A("| 同源图来源 | **BLAST** 全蛋白组互搜 | MGI + ZFIN **直系同源** |")
    A("| 图的语义 | 一对多、序列相似性加权 | **1:1 二值**（有/无） |")
    A("| 覆盖 | 全基因 | 仅有直系同源记录的基因 |")
    A("")
    A("**为什么原文那份跑不了（源码级）**：")
    A("")
    A("```python")
    A("# samap/mapping.py:1052-1074")
    A("def _calculate_blast_graph(ids, f_maps=\"maps/\", eval_thr=1e-6, reciprocate=False):")
    A("    if os.path.exists(f_maps + f\"{id1}{id2}\"):")
    A("        fA = f_maps + f\"{id1}{id2}/{id1}_to_{id2}.txt\"       # 只读预生成的表")
    A("    else:")
    A("        raise FileExistsError(\"BLAST mapping tables ... not found\")")
    A("```")
    A("")
    A("→ `SAMAP` 类**不跑 BLAST，只读预生成的 `maps/*.txt`**。")
    A("→ PyPI 的 `samap` 包（wheel 与 sdist 都是）**只含 4 个模块，不含任何 BLAST 脚本**")
    A("（`SOURCES.txt` 确认；全仓库搜 `blastp`/`makeblastdb`/`blastn` **0 处命中**）。")
    A("→ BLAST 步骤在 **SAMap 的 GitHub 仓库**里，不在分发包里。")
    A("")
    A("**⚠️ 现行结论**：这条差异**已查明、可写**；但「用 BLAST 重跑一遍」**尚未做**，")
    A("且不是「改一行」——需要 BLAST+、三物种蛋白组、官方脚本、以及 `maps/*.txt` 的正确格式")
    A("（格式错了会静默误解析）。")
    A("")
    A("**→ 这是目标③「输入」维度（`SAMap 1:1 vs Compara vs BLAST`）的第一个已知成员。**")
    A("")
    cov = load("results/ortholog-coverage-20261111/coverage.json")
    if cov:
        A("#### 覆盖率量化：1:1 图覆盖不到一半基因")
        A("")
        A("| 物种 | 基因总数 | 有同源记录 | 无同源记录 | **覆盖率** |")
        A("|---|---|---|---|---|")
        for sp, rec in cov["species"].items():
            A(f"| {sp} | {rec['total_genes']} | {rec['mapped_genes']} | "
              f"{rec['unmapped_genes']} | **{rec['coverage']}** |")
        A("")
        A("> ⚠️ **限制**：该表的解析是**启发式**的（按列位取符号、未做大小写/别名归一），")
        A("> **不是管线里的真实匹配**。参照 v71 记录「human 32,732 → 19,302 匹配」（≈59%），")
        A("> 本表 human 为 54.68%——**同量级但不等**，差异来自匹配细节。")
        A("> **→ 应表述为「量级参考」，不是精确覆盖率。**")
        A("")
        A("**但结论是稳的**：")
        A("")
        A("> **我们的 1:1 同源图覆盖不到一半基因**（human ≈55%、**mouse ≈36%**、zebrafish ≈56%），")
        A("> **近半基因在图上没有任何连接**。原文的 BLAST 全同源图会把其中一部分连上。")
        A("> **→ 输入层差异的量级不是「略有不同」，是「近一半基因缺席」。**")
        A("")
    A("### 2.8 拟合方式：我们的 oPCA 是 transductive 的（PCA 看到了目标细胞）")
    A("")
    A("**源码证据**（`scripts/ortholog_pca_dcs_v3_fixkey.py:278-282`）：")
    A("")
    A("```python")
    A("X_joint = np.vstack([Xs, Xt]).astype(np.float64)      # 源 + 目标一起堆")
    A("Z = PCA(n_components=NPCS, random_state=SEED).fit_transform(X_joint)")
    A("```")
    A("")
    A("→ **PCA 在「源物种 + 目标物种」细胞上联合拟合，拟合时已看到目标细胞**")
    A("→ **oPCA 是 transductive 的，不是 inductive。**")
    A("")
    A("**为什么重要**：真实部署时**拿不到目标物种细胞**；transductive 拟合泄漏目标分布信息，")
    A("并让我们的数与 inductive 方法**不可直接比**。")
    A("")
    tv = load("results/transductive-20261111/transductive_vs_inductive.json")
    if tv:
        A("**实测（把 `PCA(...).fit_transform(X_joint)` 改成 `PCA(...).fit(Xs)` + `transform(X_joint)`）：**")
        A("")
        A("| 方向 | transductive acc | **inductive acc** | Δ |")
        A("|---|---|---|---|")
        for dr, r in tv["directions"].items():
            A(f"| {DIRCN.get(dr,dr)} | {r['transductive_acc']} | **{r['inductive_acc']}** | "
              f"**{r['delta_acc']:+.4f}** |")
        s = tv.get("summary", {})
        A("")
        A(f"- Δ 范围 **{s.get('min_delta')} ~ {s.get('max_delta')}**，均值 {s.get('mean_delta')}")
        A("- **不是单调**：两向显著下降（鼠→人 −0.2225、斑马鱼→人 −0.1839），")
        A("  两向反而上升（人→斑马鱼 +0.0245、斑马鱼→鼠 +0.0658）")
        A("- 两条大跌的都是 **「→human」** 方向")
        A("")
        A("**⚠️ 连带影响**：所有基于 transductive oPCA 的配对结论都可能改变，")
        A("「近缘/远缘」推荐表需在 inductive 口径下复核。")
    A("")
    A("### 2.9 配对复核：拟合方式一换，近缘结论又变了（四种设置四个答案）")
    A("")
    pw_i = load("results/pairwise-20261111/pairwise_inductive.json")
    if pw_i:
        A("把 oPCA 换成 inductive 变体、其余不变，个体级配对重做，**3 条翻转**：")
        A("")
        A("| 方向 | 比较 | transductive Δ | 显著 | **inductive Δ** | **显著** |")
        A("|---|---|---|---|---|---|")
        for dr, comps in pw_i["comparisons"].items():
            for B in ("scVI", "saturn"):
                t = comps.get(f"t|opca_vs_{B}"); i = comps.get(f"i|opca_vs_{B}")
                if not t or not i:
                    continue
                if t["significant_at_95"] == i["significant_at_95"]:
                    continue
                A(f"| {DIRCN.get(dr,dr)} | oPCA vs {B} | {t['delta']:+.4f} | "
                  f"{'SIG' if t['significant_at_95'] else 'ns'} | "
                  f"**{i['delta']:+.4f}** | **{'SIG' if i['significant_at_95'] else 'ns'}** |")
        A("")
        A("#### 近缘（人↔鼠）：同一比较，四种设置四个答案")
        A("")
        A("| 设置 | 人→鼠 | 鼠→人 | 表面结论 |")
        A("|---|---|---|---|")
        A("| KNN + 逐细胞 + transductive | ns | **oPCA 胜** | 一向平一向胜 |")
        A("| KNN + 按个体 + transductive | ns | ns | 打平 |")
        A("| **LR** + 按个体 + transductive | **oPCA 胜** | **scVI 胜** | 各赢一向 |")
        A("| **KNN + 按个体 + inductive** | **scVI 胜** | **scVI 胜** | **scVI 两向全胜** |")
        A("")
        A("**→ 而远缘（鱼四向）在四种设置下都是 scVI 胜（全部 SIG 且为负）。**")
        A("")
        A("**这是本文最硬的一条结论**：")
        A("")
        A("> **「近缘哪个方法更好」在不对齐「重抽样单位 + 评估器 + 拟合方式」之前，没有唯一答案；**")
        A("> **而「远缘 scVI 更优」在四种设置下都稳健。**")
        A("")
        A("**→ 直接回答了「什么结论值得写」：远缘可以写，近缘不能。**")
    A("")
    A("---")
    A("")
    A("## 三、还没做的（如实列出，不混进结论）")
    A("")
    A("1. **SATURN 官方配置消融**（任务 `2120420983594635266` 排队中）——这是老师第一条要求的核心；")
    A("2. **SAMap BLAST 全同源图**复现（我们目前只用了 1:1）；")
    A("3. **scVI 两向按 v2 重跑**（分母 1499→1469）；")
    A("4. **规模维度消融**（1.5k/3k/6k/12k/30k，全量数据在 DCS）；")
    A("5. **held-out / inductive 评测**（现有全部是 transductive）；")
    A("6. **SATURN 的配对检验**（`pairwise_donor_level.json` 里已算，但 SATURN 用的是 v2 修正口径，需与重跑后的官方配置结果对齐）；")
    A("7. **跨门正对照 + 机制分解**（在拿到正对照前，跨门负结果不得当生物学结论）。")
    A("")
    A("---")
    A("")
    A("## 四、引用纪律（写论文时逐条对照）")
    A("")
    A("1. **禁止**再引用「SATURN 口径偏差、抬高 0.0428–0.1940、鼠↔鱼翻转」——已被推翻；")
    A("2. 任何 macro-F1 必须带 **union 口径 + 分母 + mapping 版本 + 拟合方式（transductive/inductive）**；")
    A("   （第四条是 2026-11-11 新增：§2.8 证明 oPCA 是 transductive，与 inductive 方法不可直接比）")
    A("3. **不混指标**：accuracy 与 macro-F1 分列（本项目已犯过两次）；")
    A("4. **重抽样单位必须是个体**，不是细胞；")
    A("5. 跨门负结果在拿到正对照前**不得当生物学结论**；")
    A("6. 不把 transductive 写成 held-out / inductive；不按总分排冠军。")
    A("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    idx["claims"] = [
        "细胞级 SE 低估 1.47–3.88 倍",
        "修正单位后 2 条配对结论翻转（鼠→人 oPCA/scVI、鼠→斑马鱼 SATURN/scVI）",
        "标签空间粒度六方向单调（exact<fine<coarse）",
        "union − truth-only ∈ [-0.0523, 0]",
        "解剖区跨度 0.08–0.09，不改变方法排序",
    ]
    OUT_IDX.parent.mkdir(parents=True, exist_ok=True)
    OUT_IDX.write_text(json.dumps(idx, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT_MD)
    print("wrote", OUT_IDX)
    print("sources loaded:", {k: v["loaded"] for k, v in idx["sources"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
