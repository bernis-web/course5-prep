"""一键复现：在隔离沙箱里跑完仓库所有「本地可复现」的分析步骤。

设计要点（为什么这么做）
------------------------
1) 隔离：脚本会往仓库里的 results/ 写产物。为了证明「产物可由输入重算」而
   又不动到真实仓库，本脚本用**硬链接**把 config/ results/ ortholog/ 和三个
   .h5ad 灌进一个临时沙箱，再在沙箱里跑；写出来的新文件落在沙箱，读的是同一
   inode（不额外占盘）。跑完删沙箱，原始文件不受影响（delete 只删链接）。
   例外：被任何一步声明为产物的文件**不灌**，否则写穿硬链接会改到原文件。

2) 路径重定向：仓库里有 38 个脚本把根目录硬编码成 ``D:\\projects\\course5-prep``，
   直接搬到别处就跑不了。沙箱里用一份运行期 shim 把该前缀重写到沙箱根
   （Path / open / os.makedirs 等），**脚本源码一字不改**。等价于换挂载点。

3) 证据：每步落 cmd / stdout / stderr / rc / 耗时 / 产物 sha256，并把产物与
   仓库里已有的同名文件对比（sha 相同=逐字节复现；不同则再做一次「去易变键」
   的 JSON 值比对）。最后出 manifest.json + summary.md。

用法
----
    .venv39\\Scripts\\python.exe scripts\\reproduce_all.py
    ... --fast                # 跳过 >20s 的重步骤（bootstrap / pairwise）
    ... --steps 03,07-12      # 只跑指定步
    ... --keep-sandbox        # 留着沙箱便于排查
    ... --out results/repro-manual

退出码：0 = 所有步骤退出码 0；1 = 有步骤失败（明细见 manifest.json）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = Path(sys.executable)
HARD_ROOT = "D:\\projects\\course5-prep"
STAMP = time.strftime("%Y%m%d-%H%M%S")

# ── 步骤表（全部经 tmp 沙箱实测跑通，见 docs/reports/audit-repro-20261111.md） ──
# mode=sandbox: 在沙箱里跑（脚本自行决定输出位置）
# mode=direct : 在仓库根跑，输出用显式 --out 指到本步目录（只读仓库输入）
STEPS = [
    dict(id="01", name="env-check", script="environment_check.py", mode="sandbox",
         outputs=["environment-report.json"], heavy=False,
         note="运行期自检，产出 environment-report.json"),
    dict(id="02", name="plan-contract", script="plan_contract.py", mode="sandbox",
         outputs=[], heavy=False, note="校验 config/benchmark-plan.json 的计划契约"),
    dict(id="03", name="startup-preflight", script="startup_preflight.py", mode="sandbox",
         outputs=[], heavy=False, note="校验 config/startup-preflight.json 的启动前置信息"),
    dict(id="04", name="unified-coarse-macro-f1", script="unified_coarse_macro_f1.py", mode="sandbox",
         outputs=["results/phase-20261017/unified-coarse-macro-f1/unified-coarse-macro-f1.json",
                  "results/phase-20261017/unified-coarse-macro-f1/run.log"], heavy=False,
         note="18 份逐细胞预测 → 权威 coarse macro-F1 表（后续 bootstrap 的冻结校验源）"),
    dict(id="05", name="bootstrap-ci", script="bootstrap_ci.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/bootstrap.json"], heavy=True,
         note="四方法 × 6 方向 ±SE/95%CI，跑前与冻结表逐格对齐，不等就 abort"),
    dict(id="06", name="bootstrap-crossphylum", script="bootstrap_crossphylum.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/crossphylum.json"], heavy=True,
         note="跨门（七鳃鳗↔小鼠）臂的 bootstrap"),
    dict(id="07", name="saturn-convention-audit-v1", script="saturn_convention_audit.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/saturn_convention.json"], heavy=False,
         note="v1 口径审计（物种方向颠倒的原始版本，保留作对照）"),
    dict(id="08", name="saturn-convention-audit-v2", script="saturn_convention_audit_v2.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/saturn_convention_v2.json"], heavy=False,
         note="修正物种方向后重算三口径；SATURN 更正列的出处"),
    dict(id="09", name="convention-variants", script="convention_variants.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/convention_variants.json"], heavy=False,
         note="四种词表归属约定 A/B/C/D，判定哪种能复现 6 个冻结值"),
    dict(id="10", name="convention-flip-check", script="convention_flip_check.py", mode="sandbox",
         outputs=[], heavy=False, note="结论翻转敏感性（只打印，不落盘）"),
    dict(id="11", name="mapping-v2-sensitivity", script="mapping_v2_sensitivity.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/mapping_v2_sensitivity.json"], heavy=False,
         note="三行候选改法（R36/R21/R30）逐行敏感性"),
    dict(id="12", name="orthers-variant-impact", script="orhters_variant_impact.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/orthers_variant_impact.json"], heavy=False,
         note="zebrafish|Orthers 改 unmapped 的后果（真值侧退出 + 预测侧记错）"),
    dict(id="13", name="convention-sensitivity", script="convention_sensitivity.py", mode="sandbox",
         outputs=["results/convention-20261111/convention_sensitivity.json",
                  "results/convention-20261111/convention_sensitivity.md"], heavy=False,
         note="同一批预测换口径，结论会不会翻"),
    dict(id="14", name="drop-unmapped-audit", script="drop_unmapped_audit.py", mode="sandbox",
         outputs=["results/convention-20261111/drop_unmapped_audit.json",
                  "results/convention-20261111/drop_unmapped_audit.md"], heavy=False,
         note="strict/drop 口径下，丢弃不可映射预测会影响谁"),
    dict(id="15", name="bootstrap-saturn-fixed-v1", script="bootstrap_saturn_fixed.py", mode="sandbox",
         outputs=["results/bootstrap-20261030/saturn_bootstrap_fixed.json"], heavy=False,
         note="修正方向 + v1 映射，1000 次 query 细胞重抽样"),
    dict(id="16", name="bootstrap-saturn-fixed-mapv2", script="bootstrap_saturn_fixed.py", mode="sandbox",
         env={"MAP_TSV": "config/heart-celltype-map-v2.tsv",
              "OUT_NAME": "saturn_bootstrap_fixed_mapv2.json"},
         outputs=["results/bootstrap-20261030/saturn_bootstrap_fixed_mapv2.json"], heavy=False,
         note="同上，切到 v2 签认映射（脚本原生支持 MAP_TSV / OUT_NAME）"),
    dict(id="17", name="donor-bootstrap", script="donor_bootstrap.py", mode="sandbox",
         outputs=["results/bootstrap-donor-20261111/donor_bootstrap.json",
                  "results/bootstrap-donor-20261111/donor_bootstrap.md"], heavy=True,
         note="按供体/簇重抽样的 cluster bootstrap"),
    dict(id="18", name="opca-mapping-convention-audit", script="opca_mapping_convention_audit.py",
         mode="sandbox",
         outputs=["results/mapping-v2-20261111/opca_mapping_convention_audit.json"], heavy=False,
         note="oPCA 六值的口径注记审计"),
    dict(id="19", name="opca-mapping-v1-v2", script="opca_mapping_v1_v2_audit.py", mode="sandbox",
         outputs=["results/mapping-v2-20261111/opca_v1_vs_v2.json"], heavy=False,
         note="oPCA 在 v1/v2 映射下的逐格差异"),
    dict(id="20", name="scvi-mapping-v1-v2", script="scvi_mapping_v1_v2_audit.py", mode="sandbox",
         outputs=["results/mapping-v2-20261111/scvi_v1_vs_v2.json"], heavy=False,
         note="scVI 在 v1/v2 映射下的逐格差异"),
    dict(id="21", name="labelspace-ablation", script="labelspace_ablation.py", mode="sandbox",
         outputs=["results/labelspace-20261111/labelspace_ablation.json",
                  "results/labelspace-20261111/labelspace_ablation.md"], heavy=False,
         note="exact/fine/coarse 三种标签空间下的分数"),
    dict(id="22", name="region-breakdown", script="region_breakdown.py", mode="sandbox",
         outputs=["results/region-20261111/region_breakdown.json",
                  "results/region-20261111/region_breakdown.md"], heavy=False,
         note="区域维度的对照表（读 local_human_s.h5ad）"),
    dict(id="23", name="ortholog-coverage", script="ortholog_coverage.py", mode="sandbox",
         outputs=["results/ortholog-coverage-20261111/coverage.json",
                  "results/ortholog-coverage-20261111/coverage.md"], heavy=False,
         note="1:1 直系同源图覆盖率"),
    dict(id="24", name="pairwise-corrected", script="pairwise_corrected.py", mode="sandbox",
         outputs=["results/pairwise-20261111/pairwise_corrected.json",
                  "results/pairwise-20261111/pairwise_corrected.md"], heavy=True,
         note="13 组同批细胞配对 bootstrap（v2 映射）"),
    dict(id="25", name="pairwise-donor-level", script="pairwise_donor_level.py", mode="sandbox",
         outputs=["results/pairwise-20261111/pairwise_donor_level.json",
                  "results/pairwise-20261111/pairwise_donor_level.md"], heavy=True,
         note="供体级配对：检验是不是单个供体在撑分数"),
    dict(id="26", name="pairwise-inductive", script="pairwise_inductive.py", mode="sandbox",
         outputs=["results/pairwise-20261111/pairwise_inductive.json",
                  "results/pairwise-20261111/pairwise_inductive.md"], heavy=True,
         note="inductive 口径下重做配对检验"),
    dict(id="27", name="pairwise-lr-evaluator", script="pairwise_lr_evaluator.py", mode="sandbox",
         outputs=["results/pairwise-20261111/pairwise_lr_evaluator.json",
                  "results/pairwise-20261111/pairwise_lr_evaluator.md"], heavy=True,
         note="LR 评测器口径下重做配对检验"),
    dict(id="28", name="pairwise-opca-official", script="pairwise_opca_official.py", mode="sandbox",
         outputs=["results/pairwise-20261111/opca_official_paired.json",
                  "results/pairwise-20261111/opca_official_paired.md"], heavy=True,
         note="oPCA 正式配对检验（类空间 KNN 口径）"),
    dict(id="29", name="batch-metrics-samap", script="compute_batch_metrics.py", mode="direct",
         args=["--embedding", "results/phase-20261026/samap-batch/samap_joint_embedding.npy",
               "--obs", "results/phase-20261026/samap-batch/samap_joint_obs.json",
               "--mapping", "config/heart-celltype-map-v1.tsv"],
         out_flag="--out", out_name="batch_metrics.json", outputs=[], heavy=False,
         note="silhouette/iLISI/kBET（SAMap 关节嵌入臂，有 obs 才可复算）"),
    dict(id="30", name="h5ad-inspect", script="heart_h5ad_inspect.py", mode="direct",
         args=["local_human_s.h5ad", "local_mouse_s.h5ad", "local_zebrafish_s.h5ad"],
         out_flag="--output", out_name="h5ad-inspect.json", outputs=[], heavy=False,
         note="三个源文件的 obs/var 证据（细胞数、基因数、sha256）"),
]

SKIP_HYDRATE = {"wheelhouse", "node_modules", "__pycache__", ".venv39", "tmp", ".tmp-segs"}
MAX_LINK_MB = 24


# ───────────────────────── 沙箱与重定向 ─────────────────────────
def hydrate(dst: Path, excluded: set[str]) -> dict[str, int]:
    """把输入文件硬链接进沙箱；失败则退化为复制。返回统计。"""
    stat = {"link": 0, "copy": 0, "skip_big": 0, "skip_excluded": 0}
    roots = ["config", "results", "ortholog", "templates", "deliverables", "scripts"]
    files: list[Path] = []
    for r in roots:
        base = REPO / r
        if base.is_dir():
            files.extend(p for p in base.rglob("*") if p.is_file())
    for name in ("local_human_s.h5ad", "local_mouse_s.h5ad", "local_zebrafish_s.h5ad",
                 "local_samap3_emb.h5ad"):
        p = REPO / name
        if p.is_file():
            files.append(p)
    for src in files:
        rel = src.relative_to(REPO).as_posix()
        if any(rel.startswith(s) for s in SKIP_HYDRATE):
            continue
        if rel.startswith("results/repro-"):
            continue          # 上一次的复现目录不进沙箱
        if rel in excluded:
            stat["skip_excluded"] += 1
            continue
        try:
            size = src.stat().st_size
        except OSError:
            continue
        if size > MAX_LINK_MB * 1024 * 1024 and not rel.endswith(".h5ad"):
            stat["skip_big"] += 1
            continue
        t = dst / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(src, t)
            stat["link"] += 1
        except OSError:
            shutil.copy2(src, t)
            stat["copy"] += 1
    return stat


def install_redirect(sandbox: str) -> None:
    """运行期把硬编码的仓库根重写到沙箱根（源码不改）。"""
    import builtins
    import pathlib

    variants = (HARD_ROOT, HARD_ROOT.lower(), HARD_ROOT.replace("\\", "/"),
                HARD_ROOT.lower().replace("\\", "/"))

    def fix_str(s: str) -> str:
        if sandbox in s or sandbox.replace("\\", "/") in s:
            return s          # 已经是沙箱路径，别再拼一遍
        for v in variants:
            if v in s:
                s = s.replace(v, sandbox)
        return s

    for cls in (pathlib.PurePath, pathlib.Path, pathlib.PureWindowsPath, pathlib.WindowsPath):
        old = cls.__dict__.get("__new__")
        if old is None:
            continue
        if isinstance(old, staticmethod):
            old = old.__func__

        def make(old=old):
            def __new__(kls, *args, **kwargs):
                return old(kls, *[fix_str(str(a)) if isinstance(a, (str, os.PathLike)) else a
                                  for a in args], **kwargs)
            return staticmethod(__new__)

        cls.__new__ = make()

    old_open = builtins.open

    def open_(file, *a, **kw):
        if isinstance(file, str):
            file = fix_str(file)
        return old_open(file, *a, **kw)

    builtins.open = open_

    for fname in ("makedirs", "mkdir", "remove", "rename", "replace", "rmdir"):
        fn = getattr(os, fname, None)
        if fn is None:
            continue

        def wrap(fn=fn):
            def inner(path, *a, **kw):
                if isinstance(path, str):
                    path = fix_str(path)
                return fn(path, *a, **kw)
            return inner

        setattr(os, fname, wrap())


def _child_exec(script: str, sandbox: str) -> int:
    import runpy
    install_redirect(sandbox)
    sys.argv = [script]
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else (code if isinstance(code, int) else 1)
    return 0


# ───────────────────────── 单步执行 ─────────────────────────
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def volatile_strip(obj):
    VOLATILE = {"generated_at", "timestamp", "time", "elapsed", "elapsed_s", "sec", "seconds",
                "duration", "duration_s", "date", "datetime", "started", "finished",
                "machine", "hostname", "host", "python_version", "platform_version"}
    if isinstance(obj, dict):
        return {k: volatile_strip(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, list):
        return [volatile_strip(v) for v in obj]
    return obj


def decode(blob: bytes) -> str:
    for enc in ("utf-8", "cp936", "latin-1"):
        try:
            return blob.decode(enc)
        except UnicodeDecodeError:
            continue
    return blob.decode("utf-8", "replace")


def run_step(step: dict, root: Path, step_dir: Path) -> dict:
    script = REPO / "scripts" / step["script"]
    env = dict(os.environ)
    env.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONHASHSEED": "0"})
    env.update(step.get("env") or {})

    if step["mode"] == "sandbox":
        # 沙箱子进程 cwd 是 root，脚本里若做 Path(env).relative_to(REPO) 会炸；
        # 这里把「看起来是相对路径且文件确实存在」的 env 值提升为绝对路径。
        for k, v in list(env.items()):
            if (isinstance(v, str) and v and not os.path.isabs(v)
                    and (os.sep in v or "/" in v) and (root / v).exists()):
                env[k] = str(root / v)
        cmd = [str(PY), str(Path(__file__).resolve()), "--_exec", str(script), str(root)]
        cwd = root
        # 该步自己的产物先从沙箱删掉，强制它真算一遍（硬链接只删链接，仓库原文件不动）
        for rel in step.get("outputs") or []:
            p = root / rel
            try:
                if p.is_file() or p.is_symlink():
                    p.unlink()
            except OSError:
                pass
    else:
        out = step_dir / step["out_name"]
        cmd = [str(PY), str(script), *step.get("args", []), step["out_flag"], str(out)]
        cwd = REPO
        step["_direct_out"] = out

    (step_dir / "cmd.txt").write_text(
        "cwd: " + str(cwd) + "\n" + " ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n",
        encoding="utf-8")

    t0 = time.time()
    # 子进程直接把回显写进日志文件（不经管道解码），避免 Windows 控制台编码把 UTF-8 回显打坏
    out_path = step_dir / "stdout.log"
    err_path = step_dir / "stderr.log"
    with open(out_path, "wb") as fo, open(err_path, "wb") as fe:
        try:
            cp = subprocess.run(cmd, cwd=str(cwd), stdout=fo, stderr=fe,
                                timeout=step.get("timeout", 1800), env=env)
            rc = cp.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    secs = round(time.time() - t0, 2)
    (step_dir / "rc.txt").write_text(f"{rc}\n", encoding="utf-8")

    arts = []
    targets = list(step.get("outputs") or [])
    if step.get("_direct_out"):
        targets = [str(step["_direct_out"])]
    for rel in targets:
        p = Path(rel)
        src = p if p.is_absolute() else (root / rel if step["mode"] == "sandbox" else REPO / rel)
        rec = {"path": rel, "exists": src.is_file()}
        if src.is_file():
            rec["size"] = src.stat().st_size
            rec["sha256"] = sha256(src)
            cp_dst = step_dir / "artifacts" / Path(rel).name
            cp_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, cp_dst)
            rec["copy"] = str(cp_dst.relative_to(step_dir).as_posix())
            repo_file = REPO / rel
            if repo_file.is_file() and repo_file.resolve() != src.resolve():
                rec["repo_sha256"] = sha256(repo_file)
                rec["byte_identical"] = rec["repo_sha256"] == rec["sha256"]
                if not rec["byte_identical"] and src.suffix == ".json":
                    try:
                        a = volatile_strip(json.loads(src.read_text(encoding="utf-8")))
                        b = volatile_strip(json.loads(repo_file.read_text(encoding="utf-8")))
                        rec["value_identical"] = a == b
                    except Exception:
                        rec["value_identical"] = False
            elif repo_file.is_file():
                # direct 模式写进本步目录：同一条路径，没有仓库基线可比
                rec["byte_identical"] = None
        arts.append(rec)

    tail_out = [l for l in decode(out_path.read_bytes()).strip().splitlines() if l.strip()][-4:]
    tail_err = [l for l in decode(err_path.read_bytes()).strip().splitlines() if l.strip()][-4:]
    return {"id": step["id"], "name": step["name"], "script": step["script"], "mode": step["mode"],
            "note": step.get("note", ""), "rc": rc, "seconds": secs, "heavy": step.get("heavy", False),
            "artifacts": arts, "stdout_tail": tail_out, "stderr_tail": tail_err,
            "dir": step_dir.name}


def env_snapshot() -> dict:
    import importlib
    pkgs = {}
    for name in ("numpy", "scipy", "pandas", "sklearn", "anndata", "scanpy", "h5py",
                 "pptx", "docx", "openpyxl", "matplotlib"):
        try:
            m = importlib.import_module(name)
            pkgs[name] = getattr(m, "__version__", "?")
        except Exception as exc:                      # noqa: BLE001
            pkgs[name] = f"MISSING ({exc.__class__.__name__})"
    git = {"commit": None, "branch": None, "dirty": None}
    try:
        gk = dict(encoding="utf-8", errors="replace")
        git["commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                                       capture_output=True, text=True, **gk).stdout.strip() or None
        git["branch"] = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(REPO),
                                       capture_output=True, text=True, **gk).stdout.strip() or None
        git["dirty"] = bool(subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                                          capture_output=True, text=True, **gk).stdout.strip())
    except Exception:
        pass
    return {"python": sys.version.split()[0], "python_executable": str(PY),
            "platform": platform.platform(), "os": platform.system(),
            "machine": platform.machine(), "packages": pkgs, "git": git,
            "cwd": os.getcwd(), "hard_root_redirect": HARD_ROOT}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="一键复现（隔离沙箱）")
    ap.add_argument("--fast", action="store_true", help="跳过 heavy 步骤")
    ap.add_argument("--steps", default="", help="如 01,07-12")
    ap.add_argument("--keep-sandbox", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--_exec", nargs=2, metavar=("SCRIPT", "SANDBOX"), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if args._exec:
        return _child_exec(args._exec[0], args._exec[1])

    outdir = Path(args.out) if args.out else REPO / "results" / f"repro-{STAMP}"
    if not outdir.is_absolute():
        outdir = REPO / outdir
    outdir.mkdir(parents=True, exist_ok=True)
    sandbox = outdir / "_sandbox"

    selected = STEPS
    if args.steps:
        wanted = set()
        for part in args.steps.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-")
                wanted.update(f"{i:02d}" for i in range(int(a), int(b) + 1))
            elif part:
                wanted.add(f"{int(part):02d}")
        selected = [s for s in STEPS if s["id"] in wanted]
    if args.fast:
        selected = [s for s in selected if not s["heavy"]]

    # 产物不再从沙箱里剔除：否则「某步产物是另一步输入」（如 convention_flip_check 读
    # pairwise 的 opca_official_paired.json）会缺文件。改为每步开跑前删掉自己的产物，
    # 强制重算，见 run_step()。
    excluded: set[str] = set()

    t_start = time.time()
    env = env_snapshot()
    print(f"[repro] 输出目录 {outdir}")
    print(f"[repro] python {env['python']}  git {env['git']['branch']}@{str(env['git']['commit'])[:10]}")
    print(f"[repro] 步骤 {len(selected)} / {len(STEPS)}"
          + ("  (--fast)" if args.fast else ""))

    if any(s["mode"] == "sandbox" for s in selected):
        print("[repro] 建沙箱（硬链接灌入输入）...", flush=True)
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)
        sandbox.mkdir(parents=True, exist_ok=True)
        stat = hydrate(sandbox, excluded)
        print(f"[repro] 沙箱: link={stat['link']} copy={stat['copy']} "
              f"skip_big={stat['skip_big']} skip_excluded={stat['skip_excluded']}", flush=True)

    rows = []
    for s in selected:
        step_dir = outdir / f"{s['id']}-{s['name']}"
        step_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{s['id']}] {s['name']:<32}", end="", flush=True)
        rec = run_step(s, sandbox, step_dir)
        rows.append(rec)
        mark = "OK  " if rec["rc"] == 0 else f"FAIL{rec['rc']}"
        hashes = " ".join(f"{Path(a['path']).name}:{(a.get('sha256') or '-')[:8]}"
                          f"{'=' if a.get('byte_identical') else ('~' if a.get('value_identical') else ' ')}"
                          for a in rec["artifacts"])
        print(f" {mark} {rec['seconds']:>6.1f}s  {hashes}", flush=True)
        if rec["rc"] != 0 and rec["stderr_tail"]:
            for line in rec["stderr_tail"][-3:]:
                print("      ! " + line[:160])

    duration = round(time.time() - t_start, 1)
    ok = [r for r in rows if r["rc"] == 0]
    bad = [r for r in rows if r["rc"] != 0]
    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "repro_dir": str(outdir),
        "duration_s": duration,
        "environment": env,
        "steps_total": len(STEPS),
        "steps_run": len(rows),
        "steps_ok": len(ok),
        "steps_failed": len(bad),
        "failed": [{"id": r["id"], "script": r["script"], "rc": r["rc"]} for r in bad],
        "steps": rows,
        "exit_code": 0 if not bad else 1,
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False),
                                          encoding="utf-8")

    lines = [f"# 复现运行 {STAMP}", "",
             f"- python `{env['python']}` @ `{env['python_executable']}`",
             f"- git `{env['git']['branch']}` @ `{str(env['git']['commit'])[:12]}`"
             f"（dirty={env['git']['dirty']}）",
             f"- 耗时 {duration} s，步骤 {len(ok)}/{len(rows)} 通过", "",
             "| 步 | 脚本 | rc | 秒 | 产物 (sha8) | 与仓库同名文件 |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        art = "<br>".join(
            f"`{Path(a['path']).name}` `{(a.get('sha256') or '-')[:8]}`"
            + (" =逐字节" if a.get("byte_identical") else (" ~值相同" if a.get("value_identical")
                                                          else "" if not a.get("exists") else " ≠"))
            for a in r["artifacts"]) or "—"
        lines.append(f"| {r['id']} | `{r['script']}` | {r['rc']} | {r['seconds']} | {art} | |")
    lines += ["", "判据：rc=0 且产物 sha256 与仓库内同名文件一致（`=` 逐字节，`~` 去易变键后值相同）。"]
    (outdir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if not args.keep_sandbox and sandbox.exists():
        shutil.rmtree(sandbox, ignore_errors=True)

    print()
    print(f"[repro] 完成 {len(ok)}/{len(rows)}，耗时 {duration}s")
    print(f"[repro] manifest: {outdir / 'manifest.json'}")
    if bad:
        print("[repro] 失败步骤: " + ", ".join(f"{r['id']}:{r['script']}(rc={r['rc']})" for r in bad))
        return 1
    print("[repro] 全部步骤退出码 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())