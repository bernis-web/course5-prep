#!/usr/bin/env bash
# SATURN 消融运行器 —— 参数化，投递用
#
# 用途：目标③的 SATURN 侧消融。每次只改 env 变量，不改代码。
#
# 关键设计：
#   1. **KMeans n_jobs 补丁**：make_centroids 里的 KMeans 没设 n_jobs → 单线程。
#      本脚本在运行时用 sed 打上 n_jobs=-1（安全：random_state 固定时并行不改变结果）。
#   2. **centroids 复用**：传 --centroids_init_path 可跳过 KMeans。
#      注意 hv_genes 不同 → 基因集合不同 → centroids 不能混用，故路径名带 hv 标记。
#   3. **不传 --score_adatas**（它只算一对且需 ct_map）；分数用
#      scripts/saturn_output_scores.py 从输出 adata 自己算六方向。
#
# 用法：
#   HV=8000 MG=2000 SPAN=0.3 TAG=hv8000 bash saturn_ablation_runner.sh
#
# 投递（在在线容器）：
#   dcs task run --type s -i "HV=8000 MG=2000 TAG=hv8000 bash <此脚本>" \
#     -l "vf=128g,num_proc=32" \
#     --image "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest" \
#     --output /Files/ResultData/Notebook/saturn-ablation-HV8000
set -uo pipefail

# ---- 可调参数（env 覆盖） ----
HV=${HV:-8000}                  # --hv_genes
MG=${MG:-2000}                  # --num_macrogenes
SPAN=${SPAN:-0.3}               # --hv_span（注意：不传 batch 列时它无效）
EPOCHS=${EPOCHS:-50}
PRE_EPOCHS=${PRE_EPOCHS:-200}
TAG=${TAG:-hv${HV}_mg${MG}}
PATCH_KMEANS=${PATCH_KMEANS:-1}
REUSE_CENTROIDS=${REUSE_CENTROIDS:-1}

BASE=/work/user50719-8334/saturn
EMB=$BASE/emb
NB=/Files/ResultData/Notebook
SRC=$BASE/src/saturn-src
W=$BASE/run_${TAG}_$(date +%Y%m%dT%H%M%S)
CENT=$BASE/centroids_hv${HV}_mg${MG}.pkl
mkdir -p "$W"

echo "======== TAG=$TAG HV=$HV MG=$MG SPAN=$SPAN W=$W ========"

echo "=== [1] 环境 ==="
nproc; free -g | head -2
python3 -c "import torch,scanpy;print('torch',torch.__version__,'scanpy',scanpy.__version__,'cuda',torch.cuda.is_available())" 2>&1

echo "=== [2] 输入与嵌入 ==="
for e in human mouse zebrafish; do
  printf '  %s h5ad=%s emb=%s\n' "$e" \
    "$(stat -c%s "$NB/${e}_saturn_input_s.h5ad" 2>/dev/null || echo MISS)" \
    "$(stat -c%s "$EMB/${e}_embedding.torch" 2>/dev/null || echo MISS)"
done

echo "=== [3] KMeans n_jobs 补丁 ==="
if [ "$PATCH_KMEANS" = "1" ]; then
  F=$SRC/model/saturn_model.py
  if grep -q 'KMeans(n_clusters=num_centroids, random_state=seed)' "$F"; then
    sed -i 's/KMeans(n_clusters=num_centroids, random_state=seed)/KMeans(n_clusters=num_centroids, random_state=seed, n_jobs=-1)/' "$F"
    echo "  已打补丁：$(grep -n 'KMeans(n_clusters=num_centroids' "$F" | head -1)"
  else
    echo "  已是补丁状态或未找到目标行："; grep -n 'KMeans(' "$F" | head -3
  fi
else
  echo "  跳过（PATCH_KMEANS=0）"
fi

echo "=== [4] 构造 in_data ==="
cat > "$W/in_data.csv" <<CSV
species,path,embedding_path
human,$NB/human_saturn_input_s.h5ad,$EMB/human_embedding.torch
mouse,$NB/mouse_saturn_input_s.h5ad,$EMB/mouse_embedding.torch
zebrafish,$NB/zebrafish_saturn_input_s.h5ad,$EMB/zebrafish_embedding.torch
CSV
cat "$W/in_data.csv"

CENT_ARG=""
if [ "$REUSE_CENTROIDS" = "1" ]; then
  CENT_ARG="--centroids_init_path $CENT"
  if [ -f "$CENT" ]; then echo "=== [5] 复用已有 centroids: $CENT ==="
  else echo "=== [5] centroids 不存在，将计算并保存到 $CENT ==="; fi
else
  echo "=== [5] 不复用 centroids ==="
fi

echo "=== [6] 训练 ==="
cd "$SRC" || exit 3
python3 -u train-saturn.py \
  --in_data "$W/in_data.csv" \
  --in_label_col cell_type --ref_label_col cell_type \
  --num_macrogenes "$MG" --hv_genes "$HV" --hv_span "$SPAN" \
  --pretrain --pretrain_epochs "$PRE_EPOCHS" --epochs "$EPOCHS" \
  --model_dim 256 --polling_freq 201 \
  --device cpu --seed 0 \
  $CENT_ARG \
  --work_dir "$W/out" --log_dir tboard \
  > "$W/train.log" 2>&1
RC=$?
echo "TRAIN_RC=$RC"
tail -30 "$W/train.log"

echo "=== [7] 产物 ==="
find "$W/out" -name "*.h5ad" 2>/dev/null | head -10
du -sh "$W" 2>/dev/null

echo "=== [8] 下一步（在在线容器对输出 adata 打分） ==="
echo "  python scripts/saturn_output_scores.py --adata <run_name>.h5ad"
echo "======== DONE TAG=$TAG rc=$RC ========"
