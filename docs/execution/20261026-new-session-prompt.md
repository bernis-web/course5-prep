# 新会话接手提示词（复制粘贴用）

> 用法：在 ZCode 里新建一个会话（点左上角「新建任务」/ 「+」），把下面整段粘进去。

---

```
接手一个进行中的项目：课题5 跨物种单细胞整合方法评估。
仓库：D:\projects\course5-prep

请先按顺序读这三个文件，不要问我任何背景问题：
1. AGENTS.md
2. docs/execution/20261019-handoff-full.md
3. docs/execution/20261023-resume-point.md

读完你应该知道：项目做到 12 项课程要求里的 10 项完成、2 项部分；四方法数据齐全；
基准报告 v2、选型指南 v5、七份汇报内容稿 + 六份 PPT 都已交付。

【当前唯一待办：SAMap 批次指标】
详见 docs/reports/batch-mixing-and-crossphylum-feasibility-20261019.md 的 §8。

背景：
- `samap_v98_emb.txt`（已打补丁、会保存联合嵌入的 SAMap 脚本）已经在
  /Files/ResultData/Notebook/ 里，上传问题已解决。
- 我新建的流程 `samap_emb` 跑过一次，任务 W202610260087701 完成但失败在
  `cp ${script_txt} ./samap_script.py` 没生效，日志只有一句
  "can't open file '..././samap_script.py'"。

要做的事：
1. 编辑流程 `samap_emb`，把命令段简化成（去掉 heredoc、去掉 sed、加一行诊断）：
     mkdir -p ./result
     tar xzf ${pylibs_tar}
     export PYTHONPATH=$PWD/pylibs_full:$PYTHONPATH
     export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
     cp ${script_txt} ./samap_script.py
     ls -la ./samap_script.py
     python3 ./samap_script.py > ./result/run.log 2>&1
     find . -name 'samap_joint_embedding.npy' -exec cp {} ./result/ \;
     find . -name 'samap_joint_obs.json' -exec cp {} ./result/ \;
     ls -la ./result
2. 用流程 `samap_emb` 提交：script_txt=/Files/ResultData/Notebook/samap_v98_emb.txt，
   pylibs_tar=/Files/ResultData/Notebook/pylibs_full.tar.gz，实体自定（如 samap-emb-r2）。
3. 完成后把 samap_joint_embedding.npy 与 obs 拿到，算 silhouette / iLISI / kBET，
   与 oPCA（0.0937 / 1.0124 / 0.0004）、scVI（0.181 / 1.125 / 0.0039）并表。
4. 更新 batch-mixing 报告与选型指南。

【硬约束，务必遵守】
- 不修改 scripts/run_samap_compliant_v98.py（原件）；改脚本一律复制副本。
- 不重投已失败的任务；每次提交前先确认命令段正确。
- 不覆盖旧 PPT/报告，新版本另存。
- 不把 transductive 写成 inductive / held-out；不按总分给方法排冠军。
- 不读取、打印、复制任何 token / cookie / 密码。
- 本地不做模型运算，运算走 DCS。

【环境提示】
- WDL 的 command 必须用 `command <<< ... >>>`，不要用 `command { }`——
  后者遇到 Python 字典里的 `}` 会提前闭合（这个坑踩过）。
- 平台内置浏览器会掉登录态，需要用户在面板里重新登录。
- GenPilot 有用：它能在自己的容器里直接跑 numpy/sklearn，适合算指标。
```

---

## 怎么新开会话

在 ZCode 里：

1. 左上角点 **`+ 新建任务`**（或侧边栏顶部的加号）
2. 新会话里直接粘上面那段提示词
3. 如果它需要登录 DCS，会告诉你，你在内置浏览器面板里登一次

新会话不继承本会话的上下文，但它会读那三个文件，等于把项目记忆接过去。
