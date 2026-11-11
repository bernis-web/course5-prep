#!/bin/bash
# SATURN 官方配置消融 —— 课题5 / XenoTransfer
#
# 目的：检验「我们的 SATURN 分数低，是不是因为没按官方默认配置跑」。
#
# 依据（都已在本地核实）：
#   - 官方默认值： hv_genes=8000, num_macrogenes=2000, pretrain_epochs=200, epochs=50,
#     model_dim=256, batch_size=4096（wheelhouse/saturn-src/train-saturn.py:1010-1018）
#   - 我们 v71 实际： hv_genes=2000, num_macrogenes=1000, 基因宇宙=每物种 HVG top-2500
#     （docs/saturn-smoke-evidence-20260922.md）
#   - v71 入口： saturn/train-saturn.py；参数模板见 saturn/saturn_multiple_seeds.py:62
#
# 本次只动两个数字： hv_genes 2000->8000，num_macrogenes 1000->2000。
# 其余（pretrain_epochs=200 / epochs=50 / model_dim=256 / polling_freq=201）与 v71 相同。
#
# 输入选用 *_saturn_input_s.h5ad（全基因版，416/408/507 MB）
#   推断依据： 19302 基因 x 5120 维 x 4 字节 ≈ 395 MB，与 416 MB 吻合；
#   而 _hvg 版只 54 MB（2500 基因）。→ 只有 _s 版能支撑 hv_genes=8000。
#   （此推断由探针任务 2120390795422437377 正式确认）
#
# 用法（离线任务）：
#   dcs task run --type s -i "bash /work/user50719-8334/saturn/saturn_official_config.sh" \
#     -l "vf=320g,num_proc=88,gpu=L4" \
#     --image "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest" \
#     --output /Files/ResultData/Notebook/saturn-official-20261111

set -uo pipefail

ONLINE=/work/Analysis/user50719-8334/user50719-8334_963bb09e53bb44678e2bb3818cf5992d/online
NOTEBOOK=/Files/ResultData/Notebook
WORK=/work/user50719-8334/saturn/official_$(date +%Y%m%dT%H%M%S)
mkdir -p "$WORK" "$WORK/logs"

echo "=== [1] 环境自检 ==="
python3 -V
python3 -c "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),'n',torch.cuda.device_count())" 2>&1
nvidia-smi 2>&1 | head -12
python3 -c "import scanpy,anndata,h5py;print('scanpy',scanpy.__version__,'anndata',anndata.__version__)" 2>&1

echo "=== [2] 输入自检（确认基因数够 8000） ==="
python3 - "$WORK" <<'PY' 2>&1
import h5py, sys, json
files = {
  'human':     '/Files/ResultData/Notebook/human_saturn_input_s.h5ad',
  'mouse':     '/Files/ResultData/Notebook/mouse_saturn_input_s.h5ad',
  'zebrafish': '/Files/ResultData/Notebook/zebrafish_saturn_input_s.h5ad',
}
ok = True
for sp, f in files.items():
    try:
        d = h5py.File(f, 'r')
        x = d['X'].shape if 'X' in d else None
        ngene = x[1] if x else None
        varm = [(k, d['varm'][k].shape) for k in d['varm']] if 'varm' in d else []
        obs = list(d['obs'].keys())
        lab = [c for c in obs if 'celltype' in c.lower() or c in ('cell_type', 'hcelltype', 'label')]
        print(f'{sp}: X={x} genes={ngene} varm={varm} label_cols={lab}')
        if ngene is None or ngene < 8000:
            print(f'  !! {sp} 基因数 < 8000，hv_genes=8000 不可行')
            ok = False
        d.close()
    except Exception as e:
        print(f'{sp}: ERR {e}')
        ok = False
print('INPUT_OK', ok)
PY

echo "=== [3] 构造 in_data（指向全基因版输入） ==="
cat > "$WORK/in_data_official.csv" <<EOF
species,path,embedding_path
human,$NOTEBOOK/human_saturn_input_s.h5ad,$ONLINE/human_embedding.torch
mouse,$NOTEBOOK/mouse_saturn_input_s.h5ad,$ONLINE/mouse_embedding.torch
zebrafish,$NOTEBOOK/zebrafish_saturn_input_s.h5ad,$ONLINE/zebrafish_embedding.torch
EOF
cat "$WORK/in_data_official.csv"

echo "=== [4] train-saturn.py --help（确认依赖与参数名） ==="
cd "$ONLINE/saturn" || { echo "NO saturn dir"; exit 3; }
python3 train-saturn.py --help > "$WORK/logs/help.txt" 2>&1
echo "help_rc=$?"
head -40 "$WORK/logs/help.txt"

echo "=== [5] 官方配置训练（hv_genes=8000, num_macrogenes=2000） ==="
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
  --device gpu \
  --seed 0 \
  --work_dir "$WORK/out" \
  --log_dir "$WORK/tboard" \
  > "$WORK/logs/train.log" 2>&1
TRAIN_RC=$?
echo "TRAIN_RC=$TRAIN_RC"

echo "=== [6] 产物确认 ==="
find "$WORK/out" -maxdepth 3 -type f 2>/dev/null | head -20
du -sh "$WORK" 2>/dev/null

echo "=== SATURN OFFICIAL RUN DONE rc=$TRAIN_RC ==="
