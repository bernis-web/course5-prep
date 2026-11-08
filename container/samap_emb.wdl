version 1.0

workflow samap_emb {
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
    mkdir -p ./result
    tar xzf ${pylibs_tar}
    export PYTHONPATH=$PWD/pylibs_full:$PYTHONPATH
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
    cp ${script_txt} ./samap_script.py
    sed -i 's|/data/work|.|g' ./samap_script.py
    sed -i 's/"hu": "human", "mo": "mouse", "zf": "zebrafish"/"hu": "human", "ms": "mouse", "zf": "zebrafish"/g' ./samap_script.py
    python3 - <<'PATCH'
from pathlib import Path
p = Path('./samap_script.py')
s = p.read_text(encoding='utf-8')
marker = '    metrics = {}'
assert s.count(marker) >= 1, 'marker missing'
ins = (
    '    np.save(str(output_dir / "samap_joint_embedding.npy"), np.asarray(emb))\n'
    '    (output_dir / "samap_joint_obs.json").write_text(\n'
    '        json.dumps({"obs_names": [str(x) for x in bc.tolist()],\n'
    '                    "species": [str(x) for x in sp.tolist()],\n'
    '                    "labels": [str(x) for x in labels.tolist()]}, ensure_ascii=False),\n'
    '        encoding="utf-8")\n'
    '    print("EMB_SAVED", np.asarray(emb).shape, flush=True)\n'
)
s = s.replace(marker, ins + marker, 1)
p.write_text(s, encoding='utf-8')
print('PATCH_OK')
PATCH
    echo STEP_RUN
    python3 ./samap_script.py > ./result/run.log 2>&1
    echo STEP_COLLECT
    find . -name 'samap_joint_embedding.npy' -exec cp {} ./result/ \;
    find . -name 'samap_joint_obs.json' -exec cp {} ./result/ \;
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
