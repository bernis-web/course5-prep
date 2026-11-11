#!/bin/bash
# 探针 v2 —— 修正 v1 的两个 bug，并落地 SATURN 源码
#
# v1 的两个 bug（2026-11-11 由 CPU 探针暴露）：
#   bug1  离线容器里 /work/Analysis/<user>/<ws>/online 不存在（那是在线容器专属只读挂载）
#         → SATURN 源码要自己从 /Files/wheelhouse/saturn-src.tar.gz.txt 解出来
#   bug2  h5ad 的 X 是稀疏矩阵存在 Group 里，d['X'].shape 会报
#         'Group' object has no attribute 'shape' → 改读 d['X'].attrs['shape']
#
# 本脚本要回答三件事：
#   A. SATURN 源码能否在离线容器里解开并跑通 --help（依赖是否满足）
#   B. 三份 *_saturn_input_s.h5ad 的真实基因数（决定 hv_genes=8000 是否可行）
#   C. varm 里有没有 X_protein_embedding、obs 里的标签列名是什么
set -uo pipefail

SRC=/Files/wheelhouse/saturn-src.tar.gz.txt
BASE=/work/user50719-8334/saturn
WORK=$BASE/probe2_$(date +%Y%m%dT%H%M%S)
mkdir -p "$WORK"
echo "WORK=$WORK"

echo "=== [0] 环境 ==="
nproc; free -g | head -2
python3 -V
python3 -c "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available())" 2>&1
python3 -c "import scanpy,anndata,h5py;print('scanpy',scanpy.__version__,'anndata',anndata.__version__,'h5py',h5py.__version__)" 2>&1

echo "=== [1] 取 SATURN 源码 ==="
ls -la "$SRC" 2>&1
mkdir -p "$BASE/src"
cd "$BASE/src" || exit 3
if [ -f saturn/train-saturn.py ]; then
  echo "已存在，跳过解包"
else
  cp "$SRC" ./saturn-src.tar.gz
  tar xzf saturn-src.tar.gz 2>&1 | head -5
  echo "解包后顶层："; ls | head -20
fi

echo "=== [2] 找 train-saturn.py ==="
find "$BASE/src" -maxdepth 4 -name "train-saturn.py" 2>/dev/null
TRAINER=$(find "$BASE/src" -maxdepth 4 -name "train-saturn.py" 2>/dev/null | head -1)
echo "TRAINER=$TRAINER"

echo "=== [3] train-saturn.py --help（依赖自检） ==="
if [ -n "$TRAINER" ]; then
  cd "$(dirname "$TRAINER")" && python3 train-saturn.py --help > "$WORK/help.txt" 2>&1
  echo "help_rc=$?"
  head -60 "$WORK/help.txt"
else
  echo "没找到 train-saturn.py"
fi

echo "=== [4] h5ad 真实结构（修正读法） ==="
python3 - "$WORK" <<'PY' 2>&1
import h5py, sys, json
files = {
  'human':     '/Files/ResultData/Notebook/human_saturn_input_s.h5ad',
  'mouse':     '/Files/ResultData/Notebook/mouse_saturn_input_s.h5ad',
  'zebrafish': '/Files/ResultData/Notebook/zebrafish_saturn_input_s.h5ad',
}
report = {}
for sp, f in files.items():
    try:
        d = h5py.File(f, 'r')
        # X 可能是 dense Dataset 或 sparse Group
        x = d['X']
        if hasattr(x, 'shape'):
            xshape = x.shape
        elif 'attrs' in dir(x) and 'shape' in x.attrs:
            xshape = tuple(x.attrs['shape'])
        else:
            xshape = ('?', getattr(x, 'keys', lambda: [])())
        n_cells = len(d['obs'][d['obs'].attrs['_index']]) if '_index' in d['obs'].attrs else None
        obs_cols = list(d['obs'].keys())
        varm = {}
        if 'varm' in d:
            for k in d['varm']:
                g = d['varm'][k]
                sh = g.shape if hasattr(g, 'shape') else tuple(g.attrs.get('shape', []))
                varm[k] = (str(sh), str(getattr(g, 'dtype', getattr(g, 'attrs', {}).get('dtype', '?'))))
        var_cols = list(d['var'].keys()) if 'var' in d else []
        report[sp] = {'X_shape': list(xshape) if xshape != '?' else '?',
                      'n_obs_hint': n_cells, 'obs_cols': obs_cols,
                      'varm': varm, 'var_cols': var_cols[:8]}
        genes = xshape[1] if isinstance(xshape, tuple) and len(xshape) > 1 else None
        print(f"{sp}: X={xshape} genes={genes} obs_cols={obs_cols[:14]}")
        print(f"   varm={varm}")
        print(f"   hv8000_feasible={bool(genes and genes >= 8000)}")
        d.close()
    except Exception as e:
        print(f"{sp}: ERR {type(e).__name__}: {e}")
        report[sp] = {'error': f'{type(e).__name__}: {e}'}
open(sys.argv[1] + '/h5ad_report.json', 'w').write(json.dumps(report, ensure_ascii=False, indent=1))
print('wrote h5ad_report.json')
PY

echo "=== [5] 结果目录 ==="
ls -la "$WORK"
echo "=== PROBE2 DONE ==="
