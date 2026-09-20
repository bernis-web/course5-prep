# G2 镜像探针：离线任务通道与当前阻塞（2026-09-20 晚）

## 已验证可用的通路（任何组员 2 分钟可复现）

交互式 JupyterLab 在部分网络环境下无法打开（见下文阻塞 1），但平台"个性分析 → 离线任务 → 运行脚本"通道**不依赖 inner 域名解析**，可以在 www 页面直接提交 shell 脚本，在 SATURN--22 镜像沙箱内执行，文件会同步回分析工作区（同步有明显延迟，约数分钟到停机时）。

操作路径：项目 → 个性分析 → `saturn22-g2-probe-20260920` → 离线任务 → 任务类型选 **运行脚本** → 把下述脚本粘贴进代码框 → 确定。

脚本（核心逻辑：定位镜像内 python → 跑仓库标准探针 `scripts/dcs_readonly_probe.py` 的 base64 载荷 → 结果落 output/ 并复制为工作区可见文件）：

```bash
mkdir -p output
# p.b64 = scripts/dcs_readonly_probe.py 的 base64（4 行，见仓库 docs/probe-payload-20260920.b64.txt）
echo <LINE1> > p.b64
echo <LINE2> >> p.b64
echo <LINE3> >> p.b64
echo <LINE4> >> p.b64
base64 -d p.b64 > probe.py
python3 probe.py --output output/dcs-readonly-probe.json > py_out.txt 2>&1 || python probe.py --output output/dcs-readonly-probe.json > py_out.txt 2>&1 || echo PY_FAILED > py_out.txt
# 关键：裸 shell 的 PATH 可能没有 python（v3 实测 PY_FAILED），按路径探测：
PYT=$(find / -maxdepth 4 \( -path "*/bin/python" -o -path "*/bin/python3" \) -type f 2>/dev/null | head -1)
echo "PYT=$PYT" >> diag.py 2>&1
[ -n "$PYT" ] && "$PYT" probe.py --output output/dcs-readonly-probe.json > pyrun.py 2>&1
cp output/dcs-readonly-probe.json result_data.py 2>/dev/null || cp pyrun.py result_data.py
```

（完整可粘贴版本含 base64 载荷：`docs/probe-payload-20260920.b64.txt` 拼接说明见文件头注释。）

## 已拿到的证据（2026-09-20，任务 NB2026092015045990505383）

- K8s 事件日志（运行历史 → 日志）：Pod `jupyter/task-p20260920085640327-eqwnedcz-7b5f6958f4-5hqbq`；调度等待 23 分钟（15:05 FailedScheduling → 15:28 Scheduled to `ms-k8s-worker12`）；镜像 `st-harbor.dcs.cloud/public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest` 拉取成功（5m54s）；15:34 容器 Started。**这些是 SATURN--22 镜像真实可运行 + GPU 节点存在的平台侧证据**。
- 离线沙箱执行证明：工作区出现 `probe.py`（base64 解码产物）与 `output/`、`offline-task-logs/` 目录——脚本通道真实在 SATURN--22 环境执行。
- 费用实测：3080Ti×1 捆绑（88c 320G）计费 ¥30.78/h，从**提交时刻**计费（含排队 23 分钟）；本次 1h06s 自动停，**¥32.42**。后续预算核算按此口径。

## 阻塞 1（环境侧，需老师/IT）：inner.dcs.cloud 不可解析

- 交互式 JupyterLab 的 iframe 指向 `https://inner.dcs.cloud/notebook/st/task-.../lab/...`。该域名在本机所有 DNS（校园 DNS 10.143.85.191、AliDNS、114DNS、DNSPod）均 NXDOMAIN，curl/NODE 亦无法解析 → 界面白屏。
- 影响：无法交互打开终端/notebook（本机）。**需要老师/IT 确认：校园网访问 个性分析 是否需要 VPN、hosts 配置或专用 DNS**。其他组员若网络不同，可先试打开——若能打开，直接用上文离线脚本或手动跑探针。

## 阻塞 2（脚本侧，已有对策）：离线沙箱裸 shell 无 python PATH

- v3 实测 `python3`/`python` 均失败（PY_FAILED）。镜像的 python 大概率在 conda 环境（如 /opt/conda/bin/python）且未激活。
- 对策已写入脚本：`find / -maxdepth 4 -name python` 按路径探测后以绝对路径执行。v4 已提交，结果文件同步延迟尚未可读（工作区同步时机不透明：v1-v3 文件在容器停止后批量出现）。

### 追加诊断（2026-09-20 深夜，v4 diag.py 同步后）

- 离线沙箱事实：`/usr/bin/python3` **存在**（which 命中）；`/opt` 下只有 requirements.txt；`/opt/conda` 不存在——**离线沙箱很可能不是完整的 SATURN--22 环境**（33.6GB 镜像不应没有 conda），或镜像环境未挂载进离线任务。
- 含义：即便 v4 的 python 路径探测成功，从离线沙箱读到的包版本**可能不构成 G2 有效证据**（必须来自 SATURN--22 真实环境）。G2 包版本证据的**唯一可靠来源是交互式实例内探针**，即必须先解决阻塞 1 的网络访问。
- v4 的 result_data.py 同步批次仍未返回 pyrun 内容（同步批次不透明，diag.py 已到、result_data 未更新）；不再继续等待，避免为同步机制空耗。
- 用户已切换校园网并关闭代理复测：inner.dcs.cloud 仍不可解析（新 DNS 10.170.10.252 对该记录查询超时；dcs.cloud 权威 NS=hichina.com，直询亦超时/公网递归 NXDOMAIN）——**确认 split-horizon 内网域名，公网无记录**。

## 结论与行动项

1. **关键路径 = 问老师/IT**："DCS 个性分析的 inner.dcs.cloud 校园网解析不了需要什么配置（VPN/hosts/专用 DNS）？"——拿到访问方式后，交互终端 2 分钟跑完探针，G2 即可关账。
2. 组员侧并行验证：不同网络的组员打开 个性分析 看是否白屏（若可打开，直接跑 `python scripts/dcs_readonly_probe.py --output output/dcs-readonly-probe.json`，或用上文离线脚本）。
3. 预算口径已实测（提交即计费、含排队），下次启动按 1h 封顶 ¥30.78 预算并确保探针脚本先准备好再点运行。

## 下一步

1. 任一组员打开 个性分析 确认 inner.dcs.cloud 是否可访问（网络差异验证）；
2. 或向老师/IT 提单询问访问方式（ITSM0403 为平台已知提单口）；
3. 通道打通后：粘贴离线脚本（或交互终端手动跑 `python scripts/dcs_readonly_probe.py --output output/dcs-readonly-probe.json`）→ 结果回填 `config/startup-preflight.json` 的 image_versions/kbet/readonly_sample_command 字段 → G2 关账。
