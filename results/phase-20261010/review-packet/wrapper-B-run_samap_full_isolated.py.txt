"""阶段 2 隔离 wrapper B：SAMap 本地全量模式，只写隔离输出目录（不触碰 results/pilot-v1）。

WHY
  scripts/run_samap_compliant_v98.py:249-250 把 output_dir 硬编码为
  results/pilot-v1/samap-v98 且 mkdir(parents=True, exist_ok=True)，无守卫；
  阶段 2 需要在不触碰冻结目录的前提下具备可隔离的 SAMap 全量运行能力。

HOW（与 Task 1 / wrapper A 同一模式）
  读取权威源码 -> 文本补丁（锚点必须恰好匹配一次）-> 补丁源码落盘到输出目录并执行。

补丁清单（共 2 个；root 与 output_dir 合并为同一处锚点）
  PB base-scope  ：BASE = Path(__file__).resolve().parents[1] -> BASE = Path(SOURCE_BASE)
  PC main-root   ：main() 内 root + output_dir + mkdir(exist_ok=True) 三行
                   -> root = Path(SOURCE_BASE)、output_dir = Path(OUT_DIR)、
                      并把 mkdir 换成"须由 wrapper 预建"断言

版本口径（重要，来自 GenPilot 平台侧实查，2026-10-11）
  本地脚本 = 437 行变体（sha256 8da8c8e7…）。**冻结 SAMap 数字的权威版本不是它**：
  线上 WDL 部署脚本 samap_script.py（c0f05b89…）= 410 行权威版（56bb6035…，可从
  /Files/ResultData/Notebook/run_samap_compliant_v98_dcs.txt 回捞）+ 两处 sed
  （/data/work→.、mo→ms）。本 wrapper 隔离的是本地变体；若阶段 5 要"同协议复算"，
  应以 410 行权威版为源，本文件仅记录该差异、不改变冻结口径。

安全边界（与 wrapper A 相同，全部在创建输出目录之前生效）
  - 权威脚本 SHA 不等于期望值 -> 退出码 2
  - 补丁锚点匹配 0 次或 >1 次 -> 退出码 2
  - 预检失败 -> 退出码 2，且未创建任何目录
  - 输出目录已存在或非空 -> 退出码 3；输出落在 results/pilot-v1 或仓库外 -> 退出码 3

用法
  预检：.venv39\\Scripts\\python.exe scripts\\run_samap_full_isolated.py --dry-run
  正式：.venv39\\Scripts\\python.exe scripts\\run_samap_full_isolated.py
        .venv39\\Scripts\\python.exe scripts\\run_samap_full_isolated.py --out <新目录>
  （正式运行需 samap/samalg 依赖栈，属阶段 5 范畴；本阶段只做 dry-run。）
"""
import argparse
import difflib
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "scripts" / "run_samap_compliant_v98.py"
# 完整 64 位十六进制（外部审阅第 1 轮要求：禁止前缀比较，前缀不足以锁定被审阅的字节）
EXPECTED_SOURCE_SHA = "8da8c8e7221aeac5e3915cc233931aced86f83ba60fd4bb0ac289d5ccbe8e4a7"
FROZEN_ROOT = (BASE / "results" / "pilot-v1").resolve()
EXPECTED_SPECIES = ("human", "mouse", "zebrafish")
ORTHOLOG_FILES = ("MGI_HOM_MouseHumanSequence.rpt", "human_orthos.txt", "mouse_orthos.txt")
EXPECTED_LEVELS = ("exact", "coarse", "fine")
EXPECTED_NPERM = 200
EXPECTED_DIRECTIONS = 6
WRAPPER_TAG = "run_samap_full_isolated"

PATCHES = [
    (
        "PB base-scope",
        'BASE = Path(__file__).resolve().parents[1]',
        'BASE = Path(SOURCE_BASE)',
    ),
    (
        "PC main-root",
        'def main() -> None:  # pragma: no cover - full local run\n'
        '    root = Path(__file__).resolve().parents[1]\n'
        '    output_dir = root / "results" / "pilot-v1" / "samap-v98"\n'
        '    output_dir.mkdir(parents=True, exist_ok=True)\n',
        'def main() -> None:  # pragma: no cover - full local run\n'
        '    root = Path(SOURCE_BASE)\n'
        '    output_dir = Path(OUT_DIR)\n'
        '    if not output_dir.is_dir():\n'
        '        print("ERROR: isolated output dir was not prepared by the wrapper", file=sys.stderr)\n'
        '        sys.exit(2)\n',
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
        "__name__": "isolated_source",
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
    add("source_sha256_recorded", src_sha == EXPECTED_SOURCE_SHA,
        "source=%s expected=%s (compared as full 64-hex)" % (src_sha, EXPECTED_SOURCE_SHA))

    text = SOURCE.read_text(encoding="utf-8")
    patched, applied = apply_patches(text)
    add("patches_applied", len(applied) == len(PATCHES), ",".join(applied))

    patched_path = Path(out_dir) / "_patched_source.py"
    try:
        ns = build_namespace(patched, out_dir, patched_path)
        add("patched_source_exec", True, "module-level exec OK (samalg imported only inside main)")
    except Exception as exc:  # noqa: BLE001
        add("patched_source_exec", False, repr(exc))
        ns = None

    if ns is not None:
        add("base_is_repo_root", Path(ns["BASE"]).resolve() == BASE.resolve(), str(ns["BASE"]))
        sf = ns["SPECIES_FILES"]
        add("species_expected", tuple(sorted(sf.keys())) == tuple(sorted(EXPECTED_SPECIES)), str(sorted(sf.keys())))
        for sp, rel in sf.items():
            add("h5ad:%s" % sp, (BASE / rel).is_file(), rel)
        add("truth_column", ns["TRUTH_COLUMN"] == "cell_type", str(ns["TRUTH_COLUMN"]))
        add("levels_expected", tuple(ns["LEVELS"]) == EXPECTED_LEVELS, str(ns["LEVELS"]))
        add("nperm_expected", ns["NPERM"] == EXPECTED_NPERM, str(ns["NPERM"]))
        add("directions_expected", len(tuple(ns["DIRECTIONS"])) == EXPECTED_DIRECTIONS, str(len(tuple(ns["DIRECTIONS"]))))
        add("mapping_tsv_exists", (BASE / "config" / "heart-celltype-map-v1.tsv").is_file())
        # 源码 main() 内实际读取（:280 MGI_HOM… / :306 human_orthos / :312 mouse_orthos），
        # 缺任一个 dry-run 仍会全 PASS、故障推迟到正式运行 —— 外部审阅第 1 轮要求补齐
        orth = BASE / "ortholog"
        add("ortholog_dir_exists", orth.is_dir(), str(orth))
        for f in ORTHOLOG_FILES:
            add("ortholog_file:%s" % f, (orth / f).is_file(), str(orth / f))

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
    diff = unified_diff(text, patched, "run_samap_compliant_v98.py")
    out_dir.mkdir(parents=True, exist_ok=False)

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
        "source_variant_note": (
            "local 437-line variant; frozen SAMap numbers came from the 410-line "
            "authoritative version (56bb6035) deployed as c0f05b89 via two seds - "
            "see docs/execution/20261011-genpilot-consultation-stage2-isolation.md"),
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
        BASE / "results" / "phase-20261010" / ("A-full-samap-%s" % stamp))
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
