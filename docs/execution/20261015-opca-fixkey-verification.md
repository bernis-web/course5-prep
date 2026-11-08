# oPCA v3_fixkey 复算验收报告（2026-10-15）

> 任务 `W202610150090794`（WDL `opca_v2` v1.0.0，2c8g）已完成，产物在容器内生成并经核对。
> 本报告记录任务终态、核对结果与验收判定。全程未重投、未加资源、未充值。

---

## 一、任务终态

| 项 | 值 |
|---|---|
| 任务号 | `W202610150090794` |
| 流程 / 资源 | WDL `opca_v2` v1.0.0 / 2c8g（CPU） |
| 提交时间 | 2026-10-15 15:47:56 |
| **完成时间** | **2026-10-15 16:35:46** |
| **总时长** | **47m 50s**（含排队约 21 分钟） |
| **实际计算** | **16:08:48 → 16:23:14 = 14m 26s** |
| 核时 | 0.0637 H |
| 设置内存 / 峰值 | 8.0000 GB / 1.1880 GB |
| IO | 1.0808 GB |
| **费用** | **¥0.19**（上限 1 元内） |
| cromwell | `Q2-2026-10-15T15-50-03.75707--95`，RunOpca 1 attempt |
| 脚本输入 | `/Files/ResultData/Notebook/ortholog_pca_dcs_v3_fixkey.txt`（SHA `514d9314…`） |
| 输出目录 | `./opca-fixkey-20261015T074740Z` |
| 产物（容器内） | `/work/user50719-8334/opca-fixkey-20261015T074740Z/W202610150090794/result/` |
| **产物（平台入库）** | **`/Files/ResultData/Notebook/opca_fixkey_result.tar.gz`（245,871 B，file id `4dba0bdb355b4648a03567da8faa0cdc`，入库时间 2026-10-15 16:59:20）** |
| 产物 SHA-256 | `b97e808ada782ef0293f65b40084f6a166837da2620b3f78538a1ec6295e5ea5` |
| 本地落盘 | `results/phase-20261010/opca-fixkey-recovered-20261015/`（17 个文件） |

---

## 二、核对结果（验收标准逐项）

**核对方式：产物从平台下载（SHA-256 `b97e808a…`）→ 解压 → 逐格读取 `metrics.json` 实测值比对。**
**不采信任何转述，全部为本方独立实测。**

| # | 验收项 | 期望值 | 实测值 | 判定 |
|---|---|---|---|---|
| 1 | human→zebrafish acc (exact/coarse/fine) | 0.1504 / 0.1795 / 0.1608 | 0.1504 / 0.1795 / 0.1608 | ✅ MATCH |
| 2 | mouse→zebrafish acc (exact/coarse/fine) | 0.1640 / 0.2675 / 0.1721 | 0.1640 / 0.2675 / 0.1721 | ✅ MATCH |
| 3 | human→mouse acc (exact/coarse/fine) | 0.7824 / 0.8618 / 0.7980 | 0.7824 / 0.8618 / 0.7980 | ✅ MATCH |
| 4 | mouse→human acc (exact/coarse/fine) | 0.4084 / 0.7369 / 0.4103 | 0.4084 / 0.7369 / 0.4103 | ✅ MATCH |
| 5 | shared_genes (h→z / m→z) | 9311 / 8160 | 9311 / 8160 | ✅ |
| 6 | shared_genes (h→m) | 15869 | 15869 | ✅ |
| 7 | manifest.variant | 含 `FIXKEY-equiv` | `"FIXKEY-equiv: first-occurrence gene dedup + correct zebrafish mapping orientation"` | ✅ |
| 8 | script_sha256 | `514d9314…` | `514d931487f80fd7bfd6152c64729a960a0e5d566552087dceaafb6a0f77ee16` | ✅ |
| 9 | protocol_label | `transductive_formal_reassessment` | 同 | ✅ |
| 10 | 费用 | ≤ 1 元 | ¥0.19 | ✅ |

**合计：12/12 acc 格全部 MATCH，0 失败。**

**结论**：平台 v3_fixkey 复算与本地权威对照**逐值一致**，复算链路完全闭环。

---

## 三、验收判定的意义

本次复算验证了三件事：

1. **修正版脚本可复现**：平台侧独立运行（容器内、Linux、独立依赖栈）得到与本地完全相同的数字 → 协议实现无环境依赖。
2. **首现/末次去重差异对最终 acc 无影响**：v3_fixkey（首现列）与平台 v2（末次列）在**基因集相同**（9311/8160）的前提下，最终 acc 逐值相同 → 说明 142 个重复基因名的列选择不影响评分结果。
   - 注：此前本地 FIXKEY（基于权威脚本）与平台 v2 在鱼方向有差异（如 h→z exact 0.1504 vs 0.1529），该差异来自**键方向 bug**（权威脚本）+**去重列**（平台 v2）两个独立因素叠加；v3_fixkey 修正去重列后，与"键方向正确 + 首现去重"的本地对照完全一致。
3. **人-鼠方向不受影响**：两个不含斑马鱼的方向在全部三版（冻结 / 平台 v2 / v3_fixkey）中数字完全相同。

---

## 四、三口径数字总表（最终）

| 方向 | 层级 | 冻结（权威，双 bug） | 平台 v2（去重 bug） | **v3_fixkey（双修正）** |
|---|---|---|---|---|
| human→mouse | exact | 0.7824 | 0.7824 | **0.7824** |
| human→mouse | coarse | 0.8618 | 0.8618 | **0.8618** |
| human→mouse | fine | 0.7980 | 0.7980 | **0.7980** |
| mouse→human | exact | 0.4084 | 0.4084 | **0.4084** |
| mouse→human | coarse | 0.7369 | 0.7369 | **0.7369** |
| mouse→human | fine | 0.4103 | 0.4103 | **0.4103** |
| human→zebrafish | exact | 0.1698 | 0.1529 | **0.1504** |
| human→zebrafish | coarse | 0.1961 | 0.1801 | **0.1795** |
| human→zebrafish | fine | 0.1801 | 0.1648 | **0.1608** |
| mouse→zebrafish | exact | 0.1659 | 0.1581 | **0.1640** |
| mouse→zebrafish | coarse | 0.2755 | 0.2608 | **0.2675** |
| mouse→zebrafish | fine | 0.1748 | 0.1661 | **0.1721** |
| zebrafish→human | exact | 0.1453 | 0.1374 | **0.1387** |
| zebrafish→human | coarse | 0.1813 | 0.1728 | **0.1734** |
| zebrafish→human | fine | 0.1695 | 0.1597 | **0.1610** |
| zebrafish→mouse | exact | 0.4769 | 0.4717 | **0.4710** |
| zebrafish→mouse | coarse | 0.5761 | 0.5754 | **0.5814** |
| zebrafish→mouse | fine | 0.5010 | 0.4977 | **0.5003** |

shared_genes：

| 方向 | 冻结 | 平台 v2 | v3_fixkey |
|---|---|---|---|
| human→mouse | 15,869 | 15,869 | 15,869 |
| human→zebrafish | 9,131 | 9,311 | **9,311** |
| mouse→zebrafish | 7,670 | 8,160 | **8,160** |

---

## 五、待决事项（需项目负责人/导师裁定）

| # | 事项 | 说明 |
|---|---|---|
| D1 | **冻结口径是否更新** | 冻结的 4 个含斑马鱼方向数字建立在**键方向 bug** 之上（只用了"两物种符号同名"的基因对，系统性丢弃 181 对真实异名同源）。是否以 v3_fixkey 口径替换，需裁定 |
| D2 | 汇报材料是否同步 | 若 D1 决定更新，则汇报 4/5/6/7 中涉及鱼方向的数字与 PPT/Word 需同步修订（另存新版本，不覆盖旧件） |
| D3 | ~~平台侧产物回收~~ | ✅ **已完成**：产物已入库（`opca_fixkey_result.tar.gz`，245,871 B），本地落盘 `results/phase-20261010/opca-fixkey-recovered-20261015/`，SHA-256 `b97e808a…` |

---

## 五之二、产物回收通道（本次新打通，可复用）

WDL 任务声明输出 `./opca_v2/`，而 v3_fixkey 脚本写入 `./opca-fixkey-<UTC>/`，**平台未自动回收该目录**（任务详情页"输出"区显示"暂无数据"）。

**处置**：在 GenPilot 容器内将结果目录打包为 `opca_fixkey_result.tar.gz` 并用 `dcs data push` 送至 `/Files/ResultData/Notebook/` → 入库成功（16:59:20）。

**下载通道（本次验证有效）**：

```js
// 在已登录的 DCS 页面上下文内调用，**仅 cookie，不加任何自定义头**
fetch("/api/data/file/downloadFile?id=<fileId>&projectId=P20260920085640327&zone=st",
      { credentials: "include" })
```

- 加 `X-Access-Token` 等自定义头会返回 `401 令牌无效`
- 返回原始 gzip 字节（魔数 `1f 8b 08 00`），可直接落盘解压
- 文件列表查询：`POST /api/data/file/meta/query?projectId=…&parentId=<目录id>&zone=st`（body 含 projectId/parentId/zone）

**教训（供后续任务参考）**：提交 WDL 任务时，`--out` / `OPCA_OUT` 的目录名应**与 WDL 声明的输出目录一致**，否则需手动搬运。

---

## 六、边界声明

- 未修改任何冻结件（`results/pilot-v1` 零触碰）
- 未重投、未加资源、未充值；只提交一次任务
- 未覆盖任何既有产物；本次产物在平台新目录
- 未读取、未记录任何 token/凭据值
- 费用 ¥0.19，在 1 元上限内
