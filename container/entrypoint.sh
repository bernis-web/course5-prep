#!/usr/bin/env bash
# 统一入口：把 --data / --out 翻译成脚本需要的环境变量，并做前置检查。
set -euo pipefail

DATA_DIR="${OPCA_DATA_DIR:-/data}"
OUT_DIR=""

usage() {
  echo "usage: $0 --data <dir> --out <dir>" >&2
  echo "  --data  目录需包含 local_{human,mouse,zebrafish}_s.h5ad 与 wheelhouse/" >&2
  echo "  --out   结果目录，必须不存在（脚本拒绝覆盖）" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --data) DATA_DIR="$2"; shift 2 ;;
    --out)  OUT_DIR="$2";  shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown arg: $1" >&2; usage ;;
  esac
done

[[ -n "$OUT_DIR" ]] || usage

# 前置检查：缺文件直接退出 2，与脚本内部的 PREFLIGHT_FAIL 语义一致
for f in local_human_s.h5ad local_mouse_s.h5ad local_zebrafish_s.h5ad; do
  [[ -f "$DATA_DIR/$f" ]] || { echo "PREFLIGHT_FAIL missing $DATA_DIR/$f" >&2; exit 2; }
done
for f in orth-MGI-HOM.rpt orth-human-orthos.txt orth-mouse-orthos.txt; do
  [[ -f "$DATA_DIR/wheelhouse/$f" ]] || { echo "PREFLIGHT_FAIL missing $DATA_DIR/wheelhouse/$f" >&2; exit 2; }
done

[[ -e "$OUT_DIR" ]] && { echo "OUT_EXISTS $OUT_DIR (refusing to overwrite)" >&2; exit 3; }

export OPCA_H5AD_DIR="$DATA_DIR"
export OPCA_ORTH_DIR="$DATA_DIR/wheelhouse"
# 脚本按文件名分别读这三个变量（默认指向 /Files/wheelhouse，容器内不存在），
# 只导出 OPCA_ORTH_DIR 不会被使用，必须逐个指定。
export OPCA_ORTH_MGI="${OPCA_ORTH_MGI:-$DATA_DIR/wheelhouse/orth-MGI-HOM.rpt}"
export OPCA_ORTH_HF="${OPCA_ORTH_HF:-$DATA_DIR/wheelhouse/orth-human-orthos.txt}"
export OPCA_ORTH_MF="${OPCA_ORTH_MF:-$DATA_DIR/wheelhouse/orth-mouse-orthos.txt}"
export OPCA_MAPPING="${OPCA_MAPPING:-$DATA_DIR/wheelhouse/heart-celltype-map-v1.tsv}"
export OPCA_OUT="$OUT_DIR"

echo "== course5 oPCA baseline =="
echo "data: $DATA_DIR"
echo "out : $OUT_DIR"
python3 -V

exec python3 /app/ortholog_pca.py
