# 课题5 跨物种整合基线：可复现容器
#
# 只需要 numpy / scipy / anndata / scanpy / scikit-learn，无 GPU、无编译。
# 已验证的运行环境（DCS 2c8g，2026-10-15 任务 W202610150090794）：
#   python 3.9 / numpy 1.23.5 / anndata 0.10.8 / scanpy 1.9.3 / scikit-learn 1.6.1
#
# 构建（注意 context 必须是仓库根目录，脚本在 scripts/ 下）：
#   docker build -f container/Dockerfile -t course5-opca:1.0.0 .
#
# 运行：
#   docker run --rm \
#     -v /path/to/data:/data:ro \
#     -v /path/to/out:/out \
#     course5-opca:1.0.0 \
#     --data /data --out /out/run-$(date -u +%Y%m%dT%H%M%SZ)

FROM python:3.9-slim

LABEL org.opencontainers.image.title="course5 ortholog-PCA baseline"
LABEL org.opencontainers.image.description="Cross-species single-cell label transfer baseline (deterministic, CPU only)"
LABEL org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1

WORKDIR /app

COPY container/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY scripts/ortholog_pca_dcs_v3_fixkey.py /app/ortholog_pca.py
COPY container/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 数据与产物都走挂载点，镜像内不落任何数据
VOLUME ["/data", "/out"]

ENTRYPOINT ["/app/entrypoint.sh"]
