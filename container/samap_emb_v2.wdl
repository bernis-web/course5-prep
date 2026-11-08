# SUPERSEDED 2026-10-26: this workflow declares only script+pylibs and never stages the
# three h5ad inputs, so it cannot run the SAMap script even if `cp` succeeds.
# Kept for audit only. The working route is the existing `runsamap` workflow
# (5 inputs: 3 h5ad + script + pylibs). See docs/execution/20261026-resume-point.md.
version 1.0

workflow samap_emb_v2 {
  input {
    File script_txt
    File pylibs_tar
  }
  call RunSamap {
    input:
      script_txt = script_txt,
      pylibs_tar = pylibs_tar
  }
  output {
    File output_result = RunSamap.result
  }
}

task RunSamap {
  input {
    File script_txt
    File pylibs_tar
  }
  command <<<
    set -x
    mkdir -p ./result
    echo "PWD=$(pwd)"
    echo "SRC=${script_txt}"
    ls -la "${script_txt}" || echo "SCRIPT_SRC_MISSING"
    tar xzf "${pylibs_tar}" || echo "TAR_FAILED"
    export PYTHONPATH="$PWD/pylibs_full:$PYTHONPATH"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    cp -v "${script_txt}" ./samap_script.py || echo "CP_FAILED"
    ls -la ./samap_script.py || echo "SCRIPT_DST_MISSING"
    python3 ./samap_script.py > ./result/run.log 2>&1 || echo "PY_FAILED"
    tail -n 40 ./result/run.log || true
    find . -name 'samap_joint_embedding.npy' -exec cp -v {} ./result/ \;
    find . -name 'samap_joint_obs.json' -exec cp -v {} ./result/ \;
    ls -la ./result
  >>>
  runtime {
    req_cpu: 2
    req_memory: "8Gi"
    docker_url: "public-library/zhongliyuan_57362367597d49499e5bc388096a17f1_public:latest"
  }
  output {
    File result = "./result"
  }
}
