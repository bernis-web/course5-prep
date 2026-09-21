# G2 离线通道探针证据（2026-09-21）

## 执行环境（平台记录实证）

- 任务：g2-probe-v6-printf（2026-09-21 10:56:04 提交，1c 4g CPU，镜像 SATURN--22 = st-harbor.dcs.cloud/public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest，uuid 57362367597d49499e5bc388096a17f1，cluster-st）
- 执行方式：离线任务 shell（printf 写 probe_v6.py → /usr/local/bin/python3 执行 → 输出落工作区 probe_v6_out.txt，经 /stereonote/api/normal/content 公网读取）
- 通道完整性：www.dcs.cloud 公网 API（X-Zone: st）全程可达，无需 VPN——离线任务通道是公网可用的执行环境

## 实测输出（probe_v6_out.txt 原文）

```
PY 3.9.12 /usr/local/bin/python3
PKG saturn MISSING
PKG samap MISSING
PKG scvi-tools 1.1.6.post2
PKG anndata 0.10.8
PKG scanpy 1.10.3
PKG torch 2.6.0
PKG esm MISSING
PKG fair-esm 2.0.0
PKG faiss-gpu 1.7.2
IMP saturn FAIL No module named 'saturn'
IMP samap FAIL No module named 'samap'
IMP scvi 1.1.6.post2
IMP anndata 0.10.8
IMP scanpy 1.10.3
IMP torch 2.6.0+cu124
```

## 结论（G2 证据项）

| 项 | 实测 | 与页面声明对照 |
|---|---|---|
| Python | 3.9.12（/usr/local/bin/python3） | 页面未声明 |
| scvi-tools | **1.1.6.post2**（import scvi 成功） | 页面 1.1.6.post2 ✓ 一致 |
| scanpy | **1.10.3**（import 成功） | 页面 1.10.3 ✓ 一致 |
| torch | **2.6.0+cu124**（import 成功，CUDA 12.4 构建） | 页面 2.6.0 + CUDA 12.4 ✓ 一致 |
| anndata | 0.10.8 | 页面未单独声明 |
| fair-esm | 2.0.0 | — |
| faiss-gpu | 1.7.2 | — |
| **saturn** | **不存在**（pip 无发行版 + ImportError） | 页面确实未列出 SATURN 包——**SATURN--22 镜像不含 SATURN 工具本体** |
| samap | 不存在（本镜像预期不含） | — |
| GPU 型号 | 离线节点 1c4g 无 GPU（nvidia-smi → NO_GPU）；GPU 型号证据维持 K8s 事件+购买页 3080Ti+官方 FAQ L4（待 GPU 实例内核验定夺） | — |

**重大发现**：SATURN--22 镜像 **不含 SATURN 包**——若 benchmark 要跑 SATURN 需在实例内 pip 安装（或换镜像）。页面版本声明（scvi-tools/scanpy/torch/CUDA）与实例实测**全部一致**，镜像清单可信度上调。

## 附：通道技术要点（复用手册）

1. 表单路由 `https://www.dcs.cloud/stereonote/#/notebookListNewTask?workspaceId=<ws>&projectId=P...&zone=st`（需 sessionStorage cld:projectId/cld:project:detail）
2. 脚本**必须单行化**（runner 会把多行压成一行加 tee）→ printf 写 .py 再执行
3. 提交成功后页面跳 dashboard；任务列表 API 轮询状态；输出经 /ipynb/dir/info + /normal/content 读
4. 镜像经 /images/select/list?search_key= 查 uuid；AES("stereonote") 加密仅直接 API 时需要（表单自动处理）
