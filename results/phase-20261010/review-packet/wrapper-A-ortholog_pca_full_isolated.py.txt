"""阶段 2 隔离 wrapper A：oPCA 全量模式，只写隔离输出目录（不触碰 results/pilot-v1）。

WHY
  scripts/ortholog_pca_local_v1.py 全量模式（:158）无守卫地直写冻结目录
  results/pilot-v1/ortholog-pca-v98（存在性守卫只在 --smoke 分支 :159-160）。
  阶段 2 需要在不触碰冻结目录的前提下做 6 方向 × exact/coarse/fine 全量复算。

HOW（与 Task 1 wrapper 同一模式，经四轮外部审阅验证）
  不重写流程：读取权威源码 -> 施加文本补丁（每个锚点必须恰好匹配一次，否则硬停止）
  -> 补丁后源码落盘到输出目录并执行。除补丁外与冻结协议逐字节一致。

补丁清单
  PA main-header ：去掉 argparse/--smoke，out 固定为 OUT_DIR（不再指向 pilot-v1）
  PB base-scope  ：BASE = Path(__file__).resolve().parents[1] -> BASE = Path(SOURCE_BASE)
                   （补丁源码落在输出目录下，必须把 BASE 钉在仓库根，否则
                     ORTH_DIR / MAPPING_TSV / 三个 h5ad 全部解析到不存在路径）

安全边界（全部在创建输出目录之前生效）
  - 权威脚本 SHA 不等于期望值 -> 退出码 2（防止打在错的脚本上）
  - 补丁锚点匹配 0 次或 >1 次 -> 退出码 2
  - 预检失败（输入缺失 / 常量不符）-> 退出码 2，且未创建任何目录
  - 输出目录已存在或非空 -> 退出码 3，拒绝覆盖
  - 输出路径解析后落在 results/pilot-v1 内，或落在仓库外 -> 退出码 3
  - 正式运行在输出目录内写 _patched_source.py / wrapper-provenance.json /
    environment.txt / sha256.tsv（脚本原生写 manifest.json / metrics.json /
    command.txt / predictions/ / confusion/）

用法
  预检（exec 补丁源码并断言输入与常量；不跑模型、不创建输出目录）：
      .venv39\\Scripts\\python.exe scripts\\ortholog_pca_full_isolated.py --dry-run
  正式运行（需阶段 2 被放行后手动执行；默认输出 A-full-<UTC时间戳>/）：
      .venv39\\Scripts\\python.exe scripts\\ortholog_pca_full_isolated.py
      .venv39\\Scripts\\python.exe scripts\\ortholog_pca_full_isolated.py --out <新目录>
"""
import argparse
import difflib
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "scripts" / "ortholog_pca_local_v1.py"
EXPECTED_SOURCE_SHA = "6582d8736c3570f3de23ed36cb57c9cf58f6190c4730c3d39e29928415fd0c44"
FROZEN_ROOT = (BASE / "results" / "pilot-v1").resolve()
ORTHOLOG_FILES = ("MGI_HOM_MouseHumanSequence.rpt", "human_orthos.txt", "mouse_orthos.txt")
H5AD_FILES = ("local_human_s.h5ad", "local_mouse_s.h5ad", "local_zebrafish_s.h5ad")
EXPECTED_LEVELS = ("exact", "coarse", "fine")
EXPECTED_NPERM_FULL = 200
EXPECTED_DIRECTIONS = 6
WRAPPER_TAG = "ortholog_pca_full_isolated"

PATCHES = [
    (
        "PA main-header",
        'def main():\n'
        '    t0 = time.time()\n'
        '    ap = argparse.ArgumentParser()\n'
        '    ap.add_argument("--smoke", action="store_true")\n'
        '    args = ap.parse_args()\n'
        '    smoke = args.smoke\n'
        '    nperm = NPERM_SMOKE if smoke else NPERM_FULL\n'
        '    out = BASE / "results" / "pilot-v1" / ("ortholog-pca-smoke" if smoke else "ortholog-pca-v98")\n'
        '    if smoke and out.exists():\n'
        '        die("smoke output dir already exists: %s (refusing to overwrite)" % out, 3)\n',
        'def main():\n'
        '    t0 = time.time()\n'
        '    smoke = False\n'
        '    nperm = NPERM_FULL\n'
        '    out = OUT_DIR\n'
        '    if not out.is_dir():\n'
        '        die("isolated output dir was not prepared by the wrapper: %s" % out)\n',
    ),
    (
        "PB base-scope",
        'BASE = Path(__file__).resolve().parents[1]',
        'BASE = Path(SOURCE_BASE)',
    ),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def die(msg, code=2):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(code)


def apply_patches(text):
    applied = []
    for name, anchor, replacement in PATCHES:
        n = text.count(anchor)
        if n != 1:
            die("patch %s anchor matched %d times (must be exactly 1)" % (name, n))
        text = text.replace(anchor, replacement)
        applied.append(name)
    return text, applied


def unified_diff(before, after, label):
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="%s (authoritative)" % label, tofile="%s (patched)" % label))


def build_namespace(patched, out_dir, patched_path):
    ns = {
        "__name__": "isolated_source",   # 不触发 main()
        "__file__": str(patched_path),
        "SOURCE_BASE": str(BASE),
        "OUT_DIR": Path(out_dir),
    }
    exec(compile(patched, str(patched_path), "exec"), ns)
    return ns


def guard_output(out_dir):
    out = Path(out_dir)
    if out.exists():
        die("output dir already exists: %s (refusing to overwrite)" % out, 3)
    resolved = out.resolve() if out.is_absolute() else (BASE / out).resolve()
    if FROZEN_ROOT in resolved.parents or resolved == FROZEN_ROOT:
        die("output resolves inside results/pilot-v1: %s (refusing)" % resolved, 3)
    if BASE.resolve() not in resolved.parents:
        die("output resolves outside repo root: %s (refusing)" % resolved, 3)
    return resolved


def preflight(out_dir):
    checks = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    src_sha = sha256_file(SOURCE)
    add("source_sha256_matches", src_sha == EXPECTED_SOURCE_SHA,
        "source=%s expected=%s" % (src_sha[:16], EXPECTED_SOURCE_SHA[:16]))

    text = SOURCE.read_text(encoding="utf-8")
    patched, applied = apply_patches(text)
    add("patches_applied", len(applied) == len(PATCHES), ",".join(applied))

    patched_path = Path(out_dir) / "_patched_source.py"
    try:
        ns = build_namespace(patched, out_dir, patched_path)
        add("patched_source_exec", True, "module-level exec OK")
    except Exception as exc:  # noqa: BLE001
        add("patched_source_exec", False, repr(exc))
        ns = None

    if ns is not None:
        add("base_is_repo_root", Path(ns["BASE"]).resolve() == BASE.resolve(), str(ns["BASE"]))
        orth = Path(ns["ORTH_DIR"])
        add("ortholog_dir_exists", orth.is_dir(), str(orth))
        for f in ORTHOLOG_FILES:
            add("ortholog_file:%s" % f, (orth / f).is_file())
        add("mapping_tsv_exists", Path(ns["MAPPING_TSV"]).is_file(), str(ns["MAPPING_TSV"]))
        for f in H5AD_FILES:
            add("h5ad:%s" % f, (BASE / f).is_file())
        add("levels_expected", tuple(ns["LEVELS"]) == EXPECTED_LEVELS, str(ns["LEVELS"]))
        add("nperm_full_expected", ns["NPERM_FULL"] == EXPECTED_NPERM_FULL, str(ns["NPERM_FULL"]))
        maps_block = (
            '    MAPS = {("human", "mouse"): hm, ("mouse", "human"): {v: k for k, v in hm.items()},\n'
            '            ("human", "zebrafish"): fh, ("zebrafish", "human"): {v: k for k, v in fh.items()},\n'
            '            ("mouse", "zebrafish"): fmm, ("zebrafish", "mouse"): {v: k for k, v in fmm.items()}}\n')
        add("directions_block_intact", patched.count(maps_block) == 1,
            "six-direction MAPS block appears exactly once")

    resolved = guard_output(out_dir)
    add("output_dir_absent", not Path(out_dir).exists(), str(out_dir))
    add("output_not_in_frozen_root", FROZEN_ROOT not in resolved.parents, str(resolved))
    add("output_inside_repo", BASE.resolve() in resolved.parents, str(resolved))

    return checks, patched


def write_sha256_tsv(out_dir):
    rows = []
    for p in sorted(Path(out_dir).rglob("*")):
        if p.is_file() and p.name != "sha256.tsv":
            rows.append((str(p.relative_to(out_dir)).replace("\\", "/"), sha256_file(p)))
    (Path(out_dir) / "sha256.tsv").write_bytes(
        ("".join("%s\t%s\n" % r for r in rows)).encode("utf-8"))
    return len(rows)


def run(out_dir):
    out_dir = Path(out_dir)
    text = SOURCE.read_text(encoding="utf-8")
    patched, applied = apply_patches(text)
    diff = unified_diff(text, patched, "ortholog_pca_local_v1.py")
    out_dir.mkdir(parents=True, exist_ok=False)  # guard_output 已保证不存在

    patched_path = out_dir / "_patched_source.py"
    patched_path.write_bytes(patched.encode("utf-8"))
    on_disk = sha256_file(patched_path)
    assert on_disk == sha256_text(patched), "patched source hash split (LF vs disk)"

    (out_dir / "command.txt").write_bytes(
        (" ".join([sys.executable.replace("\\", "/")] + sys.argv) + "\n").encode("utf-8"))
    env = {
        "wrapper": WRAPPER_TAG,
        "wrapper_sha256": sha256_file(__file__),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source": str(SOURCE),
        "source_sha256": sha256_file(SOURCE),
        "patched_source_sha256": on_disk,
        "patches": applied,
        "out_dir": str(out_dir),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "environment.txt").write_bytes(
        (json.dumps(env, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (out_dir / "wrapper-provenance.json").write_bytes(
        (json.dumps({"environment": env, "patch_diff": diff}, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))

    ns = build_namespace(patched, out_dir, patched_path)
    t0 = time.time()
    ns["main"]()
    elapsed = time.time() - t0

    n = write_sha256_tsv(out_dir)
    print("DONE|status=PASS|files_hashed=%d|elapsed=%.1fs|out=%s" % (n, elapsed, out_dir))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # 冻结守卫必须与"实际落盘路径"同源，否则可从非仓库根 cwd 绕过
    # （外部审阅第 1 轮实质缺口）。处理方式：强制 cwd == 仓库根，
    # 并把 --out 一律 resolve 到绝对路径后再校验与建目录。
    if Path.cwd().resolve() != BASE.resolve():
        die("must be invoked from the repo root: cwd=%s expected=%s" % (Path.cwd(), BASE), 2)
    raw_out = Path(args.out) if args.out else (
        BASE / "results" / "phase-20261010" / ("A-full-%s" % stamp))
    out_dir = raw_out.resolve()

    checks, patched = preflight(out_dir)
    npass = sum(1 for c in checks if c["ok"])
    for c in checks:
        print("%s %s %s" % ("PASS" if c["ok"] else "FAIL", c["check"], c["detail"]))
    print("PREFLIGHT|%d/%d|out=%s" % (npass, len(checks), out_dir))
    if npass != len(checks):
        die("preflight failed (%d/%d)" % (npass, len(checks)), 2)

    if args.dry_run:
        print("DRY-RUN|no model executed, no output dir created")
        return
    guard_output(out_dir)
    run(out_dir)


if __name__ == "__main__":
    main()
