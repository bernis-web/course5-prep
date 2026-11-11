#!/bin/bash
# SATURN 官方配置消融（合并版：依赖自检 + 训练 + 评估）
#
# 设计意图：把「依赖验证」和「正式训练」合并成一个离线任务，
#   因为平台排队时间长，分两次投递等于排两次队。
#
# 依据（均已核实）：
#   官方默认（wheelhouse/saturn-src/train-saturn.py:1010-1018）：
#     hv_genes=8000, num_macrogenes=2000, pretrain_epochs=200, epochs=50,
#     model_dim=256, batch_size=4096
#   v71 实际：hv_genes=2000, num_macrogenes=1000, 基因宇宙=每物种 HVG top-2500
#   v71 入口：saturn/train-saturn.py（参数模板见 saturn/saturn_multiple_seeds.py:62）
#
# 输入（已实测基因数，2026-11-11）：
#   human_saturn_input_s.h5ad      1528 × 19302  varm=['X_protein_embedding']
#   mouse_saturn_input_s.h5ad      1535 × 18703  varm=['X_protein_embedding']
#   zebrafish_saturn_input_s.h5ad  1543 × 24007  varm=['X_protein_embedding']
#   三份都在 /Files/ResultData/Notebook/；≥8000 基因，官方 hv_genes=8000 可行。
#
# 坑（已踩过，写在这里免得再踩）：
#   1. 离线容器看不到在线容器的 /work/Analysis/<user>/<ws>/online（专属只读挂载）
#      → SATURN 源码必须自己从 /Files/wheelhouse/saturn-src.tar.gz.txt 解出来
#   2. h5ad 的 X 是稀疏 Group，要用 d['X'].attrs['shape']，不能 .shape
#   3. 投递必须显式带 --image，否则会用 workspace 默认镜像（无 scanpy/torch）
#   4. GPU 机型是固定档；2c8g 通常最快，大档排队久
#
# 用法：
#   dcs task run --type s -i "bash /work/user50719-8334/saturn/run_official.sh" \
#     -l "vf=32g,num_proc=8" \
#     --image "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest" \
#     --output /Files/ResultData/Notebook/saturn-official-20261111
set -uo pipefail

SRC_TAR=/Files/wheelhouse/saturn-src.tar.gz.txt
BASE=/work/user50719-8334/saturn
NOTEBOOK=/Files/ResultData/Notebook
WORK=$BASE/official_$(date +%Y%m%dT%H%M%S)
mkdir -p "$WORK/logs"
echo "WORK=$WORK"

echo "=== [0] 环境 ==="
nproc; free -g | head -2; python3 -V
python3 -c "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),'n',torch.cuda.device_count())" 2>&1
nvidia-smi 2>&1 | head -8
python3 -c "import scanpy,anndata,h5py,sklearn,scipy;print('scanpy',scanpy.__version__,'anndata',anndata.__version__,'h5py',h5py.__version__)" 2>&1

echo "=== [1] 解 SATURN 源码 ==="
mkdir -p "$BASE/src"; cd "$BASE/src" || exit 3
if [ -f saturn/train-saturn.py ]; then
  echo "已解包"
else
  cp "$SRC_TAR" ./saturn-src.tar.gz && tar xzf saturn-src.tar.gz 2>&1 | head -3
  ls | head -20
fi
TRAINER=$(find "$BASE/src" -maxdepth 5 -name "train-saturn.py" 2>/dev/null | head -1)
echo "TRAINER=$TRAINER"

echo "=== [2] 依赖自检（关键：record_keeper / scvi-tools） ==="
for mod in torch scanpy anndata h5py sklearn scipy numpy tqdm record_keeper louvain faiss; do
  python3 -c "import $mod; print('  OK   $mod', getattr($mod,'__version__',''))" 2>&1 | tail -1
done
echo "--- record_keeper 若缺，尝试装 ---"
python3 -c "import record_keeper" 2>/dev/null || {
  echo "record_keeper 缺失，尝试 pip install（无网则失败，不致命于本步骤记录）"
  pip install record_keeper 2>&1 | tail -3
}
python3 -c "import record_keeper;print('record_keeper NOW OK')" 2>&1 | tail -1

echo "=== [3] 输入自检 ==="
python3 - "$WORK" <<'PY' 2>&1
import h5py, sys, json
files={'human':'/Files/ResultData/Notebook/human_saturn_input_s.h5ad',
       'mouse':'/Files/ResultData/Notebook/mouse_saturn_input_s.h5ad',
       'zebrafish':'/Files/ResultData/Notebook/zebrafish_saturn_input_s.h5ad'}
rep={}
for sp,f in files.items():
    try:
        d=h5py.File(f,'r'); x=d['X']
        sh=tuple(x.attrs['shape']) if (not hasattr(x,'shape') and 'shape' in x.attrs) else (x.shape if hasattr(x,'shape') else None)
        varm={k:(str(d['varm'][k].shape if hasattr(d['varm'][k],'shape') else d['varm'][k].attrs.get('shape','?')),
                str(getattr(d['varm'][k],'dtype','?'))) for k in d['varm']}
        rep[sp]={'X':str(sh),'varm':varm,'obs':list(d['obs'].keys())}
        print(f"{sp}: X={sh} varm={varm}")
        d.close()
    except Exception as e:
        print(f"{sp}: ERR {type(e).__name__}: {e}"); rep[sp]={'error':str(e)}
open(sys.argv[1]+'/logs/input_report.json','w').write(json.dumps(rep,ensure_ascii=False,indent=1))
PY

echo "=== [4] 构造 in_data ==="
# 注意：embedding_path 必须指向**离线容器可达**的位置。
# 三个 .torch 原本在 /work/Analysis/<user>/<ws>/online/（只有在线容器能看）。
# 正确搬运目标 = /work/user50719-8334/ —— 它是在线与离线容器**共享**的
#   （证据：离线容器成功读到了在线容器写的 /work/user50719-8334/probe/probe_saturn.sh）
# 不要用 /Files/wheelhouse/：实测只读（cp 报 Read-only file system）
EMB_DIR=/work/user50719-8334/saturn/emb
ok=1
for e in human mouse zebrafish; do
  if [ -f "$EMB_DIR/${e}_embedding.torch" ]; then
    echo "  OK   $EMB_DIR/${e}_embedding.torch  $(stat -c%s "$EMB_DIR/${e}_embedding.torch" 2>/dev/null) bytes"
  else
    echo "  MISS $EMB_DIR/${e}_embedding.torch"; ok=0
  fi
done
if [ "$ok" -ne 1 ]; then
  echo "!! 嵌入文件缺失。请先在**在线容器**里执行："
  echo "   mkdir -p /work/user50719-8334/saturn/emb"
  echo "   cp /work/Analysis/user50719-8334/*/online/*_embedding.torch /work/user50719-8334/saturn/emb/"
  echo "   （/work/user50719-8334 是在线与离线容器共享的；/Files/wheelhouse 只读，不要用）"
  exit 9
fi

cat > "$WORK/in_data_official.csv" <<EOF
species,path,embedding_path
human,$NOTEBOOK/human_saturn_input_s.h5ad,$EMB_DIR/human_embedding.torch
mouse,$NOTEBOOK/mouse_saturn_input_s.h5ad,$EMB_DIR/mouse_embedding.torch
zebrafish,$NOTEBOOK/zebrafish_saturn_input_s.h5ad,$EMB_DIR/zebrafish_embedding.torch
EOF
cat "$WORK/in_data_official.csv"

echo "=== [5] train-saturn.py --help ==="
if [ -n "$TRAINER" ]; then
  cd "$(dirname "$TRAINER")"
  python3 train-saturn.py --help > "$WORK/logs/help.txt" 2>&1
  echo "help_rc=$?"; head -50 "$WORK/logs/help.txt"
fi

echo "=== [6] 官方配置训练（hv_genes=8000, num_macrogenes=2000） ==="
if [ -n "$TRAINER" ] && python3 -c "import record_keeper" 2>/dev/null; then
  cd "$(dirname "$TRAINER")"
  python3 train-saturn.py \
    --in_data "$WORK/in_data_official.csv" \
    --org human \
    --num_macrogenes 2000 \
    --hv_genes 8000 \
    --hv_span 1.0 \
    --embedding_model ESM2 \
    --pretrain --pretrain_epochs 200 --epochs 50 \
    --model_dim 256 --polling_freq 201 \
    --in_label_col celltype --ref_label_col celltype \
    --device cpu \
    --seed 0 \
    --work_dir "$WORK/out" --log_dir "$WORK/tboard" \
    > "$WORK/logs/train.log" 2>&1
  echo "TRAIN_RC=$?"
  tail -20 "$WORK/logs/train.log"
else
  echo "跳过训练：TRAINER 为空 或 record_keeper 缺失"
fi

echo "=== [7] 产物 ==="
find "$WORK" -maxdepth 3 -type f 2>/dev/null | head -20
du -sh "$WORK" 2>/dev/null
echo "=== SATURN OFFICIAL DONE ==="
