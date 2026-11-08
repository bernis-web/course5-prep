## 复核结果（逐条）

### 1. wrapper sha256 vs 文档声明 — 一致

```
694e0bb0cf5a9b67595a108661620cea6de604a2c88ce607ddd86e353ed970aa *scripts/ortholog_pca_task1_isolated.py
```
与 `docs/execution/20261010-task1-preflight.md:33` 声明的 `694e0bb0…` 逐字符相同。文件当前是 untracked（`git status` 显示 `??`），无未提交改动混入。

### 2. P6 仍在，补丁后哈希未变 — 一致

- `scripts/ortholog_pca_task1_isolated.py:119-123`：P6 `base-scope` 锚点/替换对完整在位。
- 实测 `--dry-run`（只读，未建任何目录）输出：

```
DRYRUN|source_sha256=6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44
DRYRUN|patched_sha256=c56d3ee7607cf4a5b20af446ba279390f1cef3ba361e7b76d55ec3871367ba55
DRYRUN|patches_applied=6
DRYRUN|patch=P6 base-scope anchor_sha256=73cc4823288a866836505a808e766b7bd4e9eff88371480ce6d0e5af162d4d35
```

补丁集仍是 P1–P6，patched sha256 与 `20261010-task1-preflight.md:35` 声明一致。额外交叉验证：`results/pilot-v1/ortholog-pca-v98/manifest.json` 的 `script_sha256` 实测 = `6582d873…`，与仓库内 `scripts/ortholog_pca_local_v1.py` 文件哈希相同 —— 证实"wrapper 补丁的就是产出冻结数字的那个脚本"（`scripts/ortholog_pca_local_v1.py:344`）。

### 3. 两项冻结 metrics 断言确实存在，且在创建输出目录之前 — 一致

- 代码：`scripts/ortholog_pca_task1_isolated.py:222-238`（`frozen_metrics:exists` / `:parse` / `has_human->mouse/coarse` / `fields`），必需字段元组 `:235-236` 的十个字段与 `verify()` 在 `:272-273`、`:281` 比较的字段**完全一致**。
- 时序：`preflight()` 调用在 `:367`，`out.mkdir` 在 `:397`。`--dry-run` 走 `:370-389` 提前 return，两条路径都在 mkdir 之前。
- 实测 `preflight_checks=15 failed=0`，其中最后两项即新增断言，均 `OK  missing=none`。
- 冻结侧实测字段集 = `['acc','confusion','coverage_q','majority','n_perm','n_q','n_q_total','n_ref','shared_genes','shuffle_p']`，与必需集恰好相等。
- exec 安全性：权威脚本模块级只有常量与函数定义（`:33-46`），唯一的顶层语句是 `:356` 的 `if __name__ == "__main__"`，namespace 传 `__name__="_ortholog_pca_task1_patched"`（`:175`），不会触发 `main()`，无 I/O 副作用。

### 4. 只读复核 — 三项全部一致

| 项 | 结果 |
|---|---|
| `results/phase-20261010/A-smoke/` | 不存在（dry-run 前后各查一次，均 `No such file or directory`） |
| `scripts/ortholog_pca_local_v1.py` sha256 | `6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44` ✅ |
| `results/pilot-v1` mtime | `find results/pilot-v1 -newermt "2026-10-10 11:04:48"`（本机 TZ=+0800）**空**；全树最新 mtime 为 `2026-10-05T01:12:04`，比截止点早 5 天 |

我的操作未产生任何文件：`find scripts -newermt "2026-10-10 16:24:00"` 为空；`scripts/__pycache__` 是 16:03 之前的旧物。全程未写、未删、未移动、未 git 操作。

### 5. 文档两项声明 vs 实测 — 一致

- "15/15 checks pass"：实测 `preflight_checks=15 failed=0`。计数可解析：BASE(1) + ORTH_DIR(1) + 3 个 ortholog 文件 + MAPPING_TSV(1) + `SPECIES_FILES` 3 项（`:45` 确为 3 个物种）+ LEVELS(1) + NPERM(1) + smoke_branch(1) + out_injected(1) + 冻结两项(2) = 15。注意这是**条件计数**：若 BASE 断言失败会追加 `root_cause`（16），若冻结文件缺失则少一项（14）—— 文档只记了通过态的数字，可接受。
- wrapper sha256 声明：与实测一致（见第 1 条）。
- `--dry-run` 的 BASE/输入路径断言实测全部解析到仓库根：`ORTH_DIR=D:\projects\course5-prep\ortholog`、三个 h5ad、`MAPPING_TSV` 均在位。

---

## 关于 N2 加固是否引入新风险

**没有引入会危及安全边界或数字正确性的新风险**，但有两条残留，值得记录：

1. **窄口子仍在**：`:231` 的 `frozen.get(DIRECTION, {}).get(LEVEL)` 只对 `frozen` 本身做了 `isinstance(frozen, dict)` 保护，对中间值没有。若冻结文件里 `human->mouse` 的值不是 dict（例如字符串），`.get` 会抛 `AttributeError`，落在 `:225-229` 的 `try` 之外 → 未捕获 → 退出码 1，正是 N2 想消除的那类表现。现实概率极低（该文件由同一脚本生成），且发生在 mkdir 之前、不留残骸，属残留而非回归。
2. **`verify()` 侧未对称加固**：`:264` 对 A-smoke 自己的 `metrics.json` 仍是裸索引 `[DIRECTION][LEVEL]`，形状异常同样退出码 1。外部输入（冻结文件）已护住，这条是自产文件，风险更低。

另外顺带记录（非新引入）：`preflight` 会要求 `local_zebrafish_s.h5ad` 存在（`:206-208` 遍历 `SPECIES_FILES`），而该输入在补丁后永不被读 —— 这是 N3 的同一根因，文档只记了 manifest 登记，没记 preflight 对它的依赖。目前该文件存在，无影响。

---

## 独立发现 F1（我自己的，不在你给的清单里）：补丁源码哈希将出现"同名两值"

这条我认为够格挡住 Phase 0 门。

**事实链：**

1. `scripts/ortholog_pca_local_v1.py:344` 用 `sha256_file(__file__)` 写 manifest 的 `script_sha256` —— 哈希的是**磁盘字节**。
2. wrapper 在 `:399-400` 用 `patched_path.write_text(patched, encoding="utf-8")` 落盘补丁源码。`newline` 默认 `None`，Windows 下会把 `\n` 翻译成 `os.linesep`，即 **CRLF**。
3. 权威脚本本身是纯 LF（实测 `crlf=0, lone_lf=357`）；补丁串也全是 `\n`。所以补丁文本 = LF，落盘文件 = CRLF，**两个字节流不同 → sha256 必然不同**。
4. 本机同代码路径产出的冻结产物实测证实了该翻译行为（全部 100% CRLF、0 个裸 LF）：`metrics.json crlf=1033`、`manifest.json crlf=81`、`environment.json crlf=8`、`command.txt crlf=1`。
5. 而 wrapper 在 `:430`（environment.txt）和 `:444`（wrapper-provenance.json）记录的 `patched_source_sha256` 是 `sha256_text(patched)` = `c56d3ee7…`，即 **LF 文本哈希**。

**后果：** 首次真跑后，同一份 A-smoke 产物里会出现两个都自称"补丁源码哈希"的不同值 —— `manifest.json:script_sha256` 与 `sha256.tsv` 里 `_patched_source.py` 那行是 CRLF 文件哈希（既不是 `6582d873…` 也不是 `c56d3ee7…`），而 `wrapper-provenance.json` / `environment.txt` 是 `c56d3ee7…`。更糟的是 provenance 里 `"patched_source": <path>` 与 `"patched_source_sha256": c56d3ee7…` 同处一个 JSON 对象却对不上：**路径指向的文件，字节哈希不等于记录值**。

**为什么这不是纯注释问题：** 你这次新加的 N1 条（`20261010-task1-preflight.md:41`）恰恰是在教读者"manifest 的 `script_sha256` 就是补丁源码哈希，别当成协议漂移"。读者按此预期会去比对 provenance 的 `c56d3ee7…`，然后**发现对不上** —— N1 想预防的困惑，反而被 N1 引到了一个新的错配点上。

**为什么现在改比跑完再改便宜：** wrapper 按设计拒绝覆盖非空输出目录（`:395-396`，退出码 3）。一旦首跑把这组自相矛盾的 provenance 写进 `A-smoke/`，修正它就必须先删 `A-smoke/` —— 而删除动作在本项目的边界里需要用户当次明确批准。这与 C1 属同一族（都由 `__file__` 推导语义引起，且都是外部审阅才捞出来的）。

**修法（任选其一，都很小）：** ① `:400` 改 `write_text(patched, encoding="utf-8", newline="\n")`，让落盘字节与 `sha256_text` 一致；② 或在 provenance/environment 里同时记 `patched_source_file_sha256`（落盘字节）与 `patched_source_text_sha256`，并在 N1 条里写明两者差异。我倾向 ①，因为它让"补丁源码"只有一个哈希。

**严重度界定（我不想夸大）：** 不碰冻结目录、不改任何数字、不违反任何只读/安全边界，也**不是**本轮改动引入的（P6/provenance 设计早已如此，N2 加固与它无关）。它是写一次就固化的审计一致性问题。

另附一条操作性观察（同样非本轮引入）：`:397` 先 mkdir 再跑模型，若模型阶段硬停（如 `<1000 shared ortholog`），残留的半成品目录会让重跑被 `:395-396` 拒绝，操作者被迫走删除流程。preflight 前移已挡住最可能的一类失败，但这一类没挡住。

---

## 结论

你给的 5 项声明**全部与实测一致**，N2 加固本身**没有引入安全或正确性风险**（只有第 1 条那个窄口子）。但 F1 是一个可独立验证、会在首跑固化成写一次产物的 provenance 自相矛盾，且恰好落在本轮新加 N1 说明的射程内。按本门自己的标准（C1 就是这么被抓出来的），建议在首次真跑前用一行修掉。

verdict: REVISE
