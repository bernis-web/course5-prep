"""Task 1 隔离 wrapper：只跑 human -> mouse / coarse，只写 results/phase-20261010/A-smoke/。

WHY（为什么需要 wrapper）
  scripts/ortholog_pca_local_v1.py 无法限定物种、方向和层级，而且它的全量模式
  （第 158 行）会无守卫地直写冻结目录 results/pilot-v1/ortholog-pca-v98。
  Task 1 要求在不触碰冻结目录的前提下复现冻结的 coarse human->mouse 数字。

HOW（怎么做才可信）
  本 wrapper **不重写流程**。它读取权威脚本源码，施加一小组文本补丁，要求每个锚点
  恰好匹配一次（否则硬停止），把补丁后的源码落盘到输出目录，然后执行它。
  除补丁之外的一切与冻结协议逐字节一致，因此复现是"构造上协议保真"的，
  而不是"照着抄一遍"。

  **执行前会真的 exec 一次补丁源码**（`__name__` 不是 `__main__`，不会触发 main()），
  并断言 BASE 指向仓库根、全部输入文件存在、LEVELS 只剩 coarse。这组断言在创建输出
  目录之前完成，所以预检失败不会留下任何目录或文件。

补丁清单（锚点不匹配即失败，不会静默改错）
  P1 main-header   ：去掉 argparse/--smoke，out 固定为 OUT_DIR
  P2 species-loop  ：["human","mouse","zebrafish"] -> ["human","mouse"]
  P3 direction-map ：MAPS 只保留 ("human","mouse") -> hm
  P4 levels        ：LEVELS -> ("coarse",)
  P5 done-print    ：dir_res['exact'] -> dir_res['coarse']（P4 之后 exact 不存在）
  P6 base-scope    ：BASE = Path(__file__).resolve().parents[1] -> BASE = Path(SOURCE_BASE)
                     （补丁源码落在 A-smoke/ 下，若仍由 __file__ 推导 BASE，
                       则 ORTH_DIR / MAPPING_TSV / 三个 h5ad 全部指向
                       results/phase-20261010/ 下不存在的路径，运行必然
                       die("missing input")。由 Claude 外部审阅 C1 发现，已复核确认。）

产物（全部落在 --out，默认 results/phase-20261010/A-smoke/）
  脚本原生：manifest.json / metrics.json / environment.json / command.txt
            predictions/coarse_human_to_mouse.json / confusion/coarse_human_to_mouse.json
  wrapper 追加：confusion.json（顶层副本）、predictions.json（顶层副本）、environment.txt、
            sha256.tsv（A-smoke 全树哈希）、verification.json（对冻结数字的双重核对）、
            wrapper-provenance.json（wrapper/源码 SHA + 补丁 diff）、_patched_source.py

安全边界
  - 预检（输入路径/常量断言）失败 -> 退出码 2，且尚未创建任何输出目录。
  - 输出目录已存在且非空 -> 退出码 3，拒绝覆盖。
  - --out 解析后落在 results/pilot-v1 内 -> 退出码 3，拒绝执行。
  - 与冻结数字核对不一致 -> 写 verification.json 后退出码 4。

用法
  预检（会 exec 补丁源码并断言输入存在，但不跑计算、不写任何输出产物）：
      .venv39\\Scripts\\python.exe scripts\\ortholog_pca_task1_isolated.py --dry-run
  正式运行（需 Task 1 被放行后手动执行）：
      .venv39\\Scripts\\python.exe scripts\\ortholog_pca_task1_isolated.py

参考冻结值（results/pilot-v1/ortholog-pca-v98/metrics.json 的 human->mouse / coarse）
  acc=0.8618 majority=0.4817 shuffle_p=0.0 n_ref=1528 n_q=1505 n_q_total=1535
  coverage_q=0.9805 n_perm=200 shared_genes=15869 混淆对角线=1297
"""
import argparse
import difflib
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "scripts" / "ortholog_pca_local_v1.py"
DEFAULT_OUT = BASE / "results" / "phase-20261010" / "A-smoke"
FROZEN_METRICS = BASE / "results" / "pilot-v1" / "ortholog-pca-v98" / "metrics.json"
FROZEN_ROOT = (BASE / "results" / "pilot-v1").resolve()
DIRECTION = "human->mouse"
LEVEL = "coarse"
NPERM_EXPECTED = 200
ORTHOLOG_FILES = ("MGI_HOM_MouseHumanSequence.rpt", "human_orthos.txt", "mouse_orthos.txt")
# 冻结 metrics 里 acc/majority/shuffle_p/coverage_q 都是 round(x, 4) 写入，
# 因此核对必须先把重算值取整到同一精度，否则 ~1e-5 的表示差会误报。
ROUND_DP = 4
TOL = 1e-12

PATCHES = [
    (
        "P1 main-header",
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
        '        die("A-smoke output dir was not prepared by the wrapper: %s" % out)\n',
    ),
    (
        "P2 species-loop",
        '    for sp in ["human", "mouse", "zebrafish"]:',
        '    for sp in ["human", "mouse"]:',
    ),
    (
        "P3 direction-map",
        '    MAPS = {("human", "mouse"): hm, ("mouse", "human"): {v: k for k, v in hm.items()},\n'
        '            ("human", "zebrafish"): fh, ("zebrafish", "human"): {v: k for k, v in fh.items()},\n'
        '            ("mouse", "zebrafish"): fmm, ("zebrafish", "mouse"): {v: k for k, v in fmm.items()}}\n',
        '    MAPS = {("human", "mouse"): hm}\n',
    ),
    (
        "P4 levels",
        'LEVELS = ("exact", "coarse", "fine")',
        'LEVELS = ("coarse",)',
    ),
    (
        "P5 done-print",
        '        print(f"{src}->{tgt} done genes={len(shared)} acc(exact)={dir_res[\'exact\'][\'acc\']}", flush=True)',
        '        print(f"{src}->{tgt} done genes={len(shared)} acc(coarse)={dir_res[\'coarse\'][\'acc\']}", flush=True)',
    ),
    (
        "P6 base-scope",
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
    print("HARDSTOP|%s" % msg, flush=True)
    sys.exit(code)


def apply_patches(text):
    """每个锚点必须恰好匹配一次；否则硬停止，不做任何猜测性替换。"""
    patched = text
    records = []
    for name, anchor, replacement in PATCHES:
        n = patched.count(anchor)
        if n != 1:
            die("%s anchor matched %d times (expected exactly 1); source may have changed" % (name, n), 2)
        patched = patched.replace(anchor, replacement, 1)
        records.append({
            "name": name,
            "anchor_sha256": sha256_text(anchor),
            "replacement_sha256": sha256_text(replacement),
            "anchor_line_count": anchor.count("\n"),
        })
    return patched, records


def unified_diff(before, after):
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=str(SOURCE),
        tofile="_patched_source.py",
        n=2,
    ))


def build_namespace(patched, out, patched_path):
    """exec 补丁源码。__name__ 不是 __main__，因此只定义常量/函数，不触发 main()。"""
    namespace = {
        "__name__": "_ortholog_pca_task1_patched",
        "__file__": str(patched_path),
        "OUT_DIR": out,
        "SOURCE_BASE": str(BASE),
    }
    exec(compile(patched, str(patched_path), "exec"), namespace)
    return namespace


def preflight(namespace, patched):
    """创建输出目录之前的硬断言：常量与输入路径必须真实可用。"""
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    base_ok = Path(namespace["BASE"]) == BASE
    add("BASE_is_repo_root", base_ok,
        "BASE=%s expected=%s" % (namespace["BASE"], BASE))
    if not base_ok:
        # BASE 一错，下面所有输入路径都会假阴性，直接给出根因
        add("root_cause", False,
            "BASE 由 __file__ 推导；补丁源码落在输出目录下，必须由 P6 钉成 SOURCE_BASE")

    orth_dir = Path(namespace["ORTH_DIR"])
    add("ORTH_DIR_exists", orth_dir.is_dir(), str(orth_dir))
    for name in ORTHOLOG_FILES:
        p = orth_dir / name
        add("ortholog:%s" % name, p.is_file(), str(p))
    mapping = Path(namespace["MAPPING_TSV"])
    add("MAPPING_TSV_exists", mapping.is_file(), str(mapping))
    for sp in sorted(namespace["SPECIES_FILES"]):
        p = Path(namespace["SPECIES_FILES"][sp])
        add("input:%s" % sp, p.is_file(), str(p))

    add("LEVELS_coarse_only", tuple(namespace["LEVELS"]) == ("coarse",),
        "LEVELS=%s" % (namespace["LEVELS"],))
    add("NPERM_FULL_is_200", int(namespace["NPERM_FULL"]) == NPERM_EXPECTED,
        "NPERM_FULL=%s" % namespace["NPERM_FULL"])
    add("smoke_branch_removed", "args = ap.parse_args()" not in patched,
        "argparse smoke branch absent from patched source")
    add("out_is_injected", "    out = OUT_DIR" in patched,
        "main() uses OUT_DIR")

    # N2（外部审阅第二轮）：冻结 metrics 的结构必须在这里就验掉，
    # 否则形状异常时会在跑完模型、写完产物之后才 KeyError（退出码 1），
    # 而文档承诺的是写 verification.json + 退出码 4。
    if not FROZEN_METRICS.is_file():
        add("frozen_metrics:exists", False, str(FROZEN_METRICS))
    else:
        block = None
        try:
            frozen = load_json(FROZEN_METRICS)
            # 整条 .get 链都在 try 内：中间值若不是 dict（例如字符串），
            # 裸 .get 会抛 AttributeError，正是本项要消除的那类退出码 1。
            if isinstance(frozen, dict):
                block = frozen.get(DIRECTION, {}).get(LEVEL)
        except Exception as exc:  # noqa: BLE001 - 预检要报告而不是抛出
            add("frozen_metrics:parse", False, "%s: %s" % (type(exc).__name__, exc))
        add("frozen_metrics:has_%s/%s" % (DIRECTION, LEVEL), isinstance(block, dict),
            "present" if isinstance(block, dict) else "MISSING")
        if isinstance(block, dict):
            required = ("acc", "majority", "shuffle_p", "n_ref", "n_q", "n_q_total",
                        "coverage_q", "n_perm", "shared_genes", "confusion")
            missing = [k for k in required if k not in block]
            add("frozen_metrics:fields", not missing, "missing=%s" % (missing or "none"))
    return checks


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def diagonal_of(confusion):
    diag = 0
    for key, value in confusion.items():
        truth, _, pred = key.partition("=>")
        if truth == pred:
            diag += int(value)
    return diag


def write_failure_report(out, reason):
    """任何无法完成核对的情形都先落盘再退出，避免裸异常（退出码 1）绕过承诺的 verification.json。"""
    report = {
        "task": "task-1-a-smoke-verification",
        "direction": DIRECTION,
        "level": LEVEL,
        "status": "FAIL",
        "reason": reason,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (out / "verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def verify(out):
    """对冻结数字做双重核对，全部通过才算 PASS。"""
    new_metrics_path = out / "metrics.json"
    if not new_metrics_path.exists():
        write_failure_report(out, "A-smoke metrics.json missing: %s" % new_metrics_path)
        die("A-smoke metrics.json missing; cannot verify", 4)
    if not FROZEN_METRICS.exists():
        write_failure_report(out, "frozen metrics.json missing: %s" % FROZEN_METRICS)
        die("frozen metrics.json missing: %s" % FROZEN_METRICS, 4)

    # 形状异常必须走退出码 4 + verification.json，而不是裸 KeyError（退出码 1）
    try:
        new = load_json(new_metrics_path)[DIRECTION][LEVEL]
    except Exception as exc:  # noqa: BLE001
        write_failure_report(out, "cannot read %s / %s from A-smoke metrics: %s: %s"
                             % (DIRECTION, LEVEL, type(exc).__name__, exc))
        die("A-smoke metrics shape invalid; cannot verify", 4)
    try:
        frozen = load_json(FROZEN_METRICS)[DIRECTION][LEVEL]
    except Exception as exc:  # noqa: BLE001
        write_failure_report(out, "cannot read %s / %s from frozen metrics: %s: %s"
                             % (DIRECTION, LEVEL, type(exc).__name__, exc))
        die("frozen metrics shape invalid; cannot verify", 4)

    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    for key in ("acc", "majority", "shuffle_p", "n_ref", "n_q", "n_q_total",
                "coverage_q", "n_perm", "shared_genes"):
        if key not in new:
            add("field:%s" % key, False, "missing in A-smoke metrics")
            continue
        diff = abs(float(new[key]) - float(frozen[key]))
        add("field:%s" % key, diff <= TOL,
            "new=%s frozen=%s abs_diff=%s (tol=%s)" % (new[key], frozen[key], diff, TOL))

    add("confusion:identical", new["confusion"] == frozen["confusion"],
        "new_entries=%d frozen_entries=%d" % (len(new["confusion"]), len(frozen["confusion"])))

    new_diag = diagonal_of(new["confusion"])
    new_total = sum(int(v) for v in new["confusion"].values())
    frozen_diag = diagonal_of(frozen["confusion"])
    new_nq = int(new["n_q"])

    add("independent:confusion_total_eq_n_q", new_total == new_nq,
        "confusion_total=%d n_q=%d" % (new_total, new_nq))
    add("independent:round(diag/n_q,dp)_eq_acc",
        round(new_diag / new_nq, ROUND_DP) == float(new["acc"]),
        "diag=%d n_q=%d round(diag/n_q,%d)=%s acc=%s"
        % (new_diag, new_nq, ROUND_DP, round(new_diag / new_nq, ROUND_DP), new["acc"]))
    add("independent:abs(acc*n_q-diag)_lt_0.5",
        abs(float(new["acc"]) * new_nq - new_diag) < 0.5,
        "acc*n_q=%s diag=%d" % (float(new["acc"]) * new_nq, new_diag))
    add("independent:diag_matches_frozen", new_diag == frozen_diag,
        "new_diag=%d frozen_diag=%d" % (new_diag, frozen_diag))
    add("independent:frozen_round(diag/n_q,dp)_eq_frozen_acc",
        round(frozen_diag / int(frozen["n_q"]), ROUND_DP) == float(frozen["acc"]),
        "frozen_diag=%d frozen_n_q=%s frozen_acc=%s"
        % (frozen_diag, frozen["n_q"], frozen["acc"]))
    add("protocol:n_perm_is_full", int(new["n_perm"]) == NPERM_EXPECTED,
        "n_perm=%s expected=%d" % (new["n_perm"], NPERM_EXPECTED))

    passed = all(c["ok"] for c in checks)
    report = {
        "task": "task-1-a-smoke-verification",
        "direction": DIRECTION,
        "level": LEVEL,
        "status": "PASS" if passed else "FAIL",
        "tolerance": TOL,
        "round_dp": ROUND_DP,
        "note": (
            "冻结 metrics 的 acc/majority/shuffle_p/coverage_q 为 round(x, 4)；"
            "核对按同一精度取整后再比，避免 ~1e-5 的表示差造成误停。"
        ),
        "a_smoke_metrics": str(new_metrics_path.relative_to(BASE)).replace("\\", "/"),
        "a_smoke_metrics_sha256": sha256_file(new_metrics_path),
        "frozen_metrics": str(FROZEN_METRICS.relative_to(BASE)).replace("\\", "/"),
        "frozen_metrics_sha256": sha256_file(FROZEN_METRICS),
        "checks": checks,
        "failed_checks": [c["check"] for c in checks if not c["ok"]],
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (out / "verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if not passed:
        die("verification FAILED: %s" % ", ".join(report["failed_checks"]), 4)
    return report


def write_sha256_tsv(out):
    lines = ["path\tsize_bytes\tsha256"]
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "sha256.tsv":
            lines.append("%s\t%d\t%s" % (
                str(p.relative_to(out)).replace("\\", "/"), p.stat().st_size, sha256_file(p)))
    (out / "sha256.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines) - 1


def main():
    t0 = time.time()
    ap = argparse.ArgumentParser(description="Task 1 isolated A-smoke wrapper (human->mouse / coarse).")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help="输出目录，默认 results/phase-20261010/A-smoke/")
    ap.add_argument("--dry-run", action="store_true",
                    help="只做预检：exec 补丁源码并断言常量与输入路径，不跑计算、不写任何输出产物")
    args = ap.parse_args()

    out = Path(args.out).resolve()
    if FROZEN_ROOT == out or FROZEN_ROOT in out.parents:
        die("refusing to write inside the frozen root: %s" % out, 3)

    if not SOURCE.exists():
        die("authoritative source missing: %s" % SOURCE, 2)

    original = SOURCE.read_text(encoding="utf-8")
    patched, patch_records = apply_patches(original)
    diff = unified_diff(original, patched)

    # 预检发生在创建输出目录之前：失败不留任何目录或文件。
    probe_path = out / "_patched_source.py"
    namespace = build_namespace(patched, out, probe_path)
    checks = preflight(namespace, patched)
    failed = [c for c in checks if not c["ok"]]

    if args.dry_run:
        print("DRYRUN|source=%s" % SOURCE)
        print("DRYRUN|source_sha256=%s" % sha256_text(original))
        print("DRYRUN|patched_sha256=%s" % sha256_text(patched))
        print("DRYRUN|patches_applied=%d" % len(patch_records))
        print("DRYRUN|out=%s" % out)
        print("DRYRUN|out_exists=%s" % out.exists())
        print("DRYRUN|frozen_metrics_exists=%s" % FROZEN_METRICS.exists())
        print("DRYRUN|preflight_checks=%d failed=%d" % (len(checks), len(failed)))
        for c in checks:
            print("DRYRUN|check %-28s %s  %s" % (c["check"], "OK" if c["ok"] else "FAIL", c["detail"]))
        for rec in patch_records:
            print("DRYRUN|patch=%s anchor_sha256=%s" % (rec["name"], rec["anchor_sha256"]))
        print("DRYRUN|diff_begin")
        print(diff, end="" if diff.endswith("\n") else "\n")
        print("DRYRUN|diff_end")
        if failed:
            die("preflight FAILED: %s" % ", ".join(c["check"] for c in failed), 2)
        print("DRYRUN|preflight=PASS")
        return 0

    if failed:
        die("preflight FAILED (no output dir created): %s"
            % ", ".join(c["check"] for c in failed), 2)

    if out.exists() and any(out.iterdir()):
        die("output dir already exists and is not empty: %s (refusing to overwrite)" % out, 3)
    out.mkdir(parents=True, exist_ok=True)

    patched_path = out / "_patched_source.py"
    # F1（外部审阅第三轮发现，已复核）：write_text 在 Windows 上把 \n 翻成 CRLF，
    # 于是磁盘字节哈希 != sha256_text(patched)；而 manifest 的 script_sha256 走
    # sha256_file(__file__)、provenance 的 patched_source_sha256 走 sha256_text，
    # 同一份产物里会出现两个都自称"补丁源码哈希"的不同值。
    # 注意 Python 3.9 的 Path.write_text 没有 newline 参数（3.10 才加），
    # 所以直接写字节：权威源码本身是纯 LF，落盘后哈希与 sha256_text 一致。
    patched_path.write_bytes(patched.encode("utf-8"))
    written_sha = sha256_file(patched_path)
    if written_sha != sha256_text(patched):
        die("patched source on disk (%s) does not match the recorded text hash (%s)"
            % (written_sha, sha256_text(patched)), 2)

    run_ns = build_namespace(patched, out, patched_path)
    run_ns["main"]()

    # 顶层副本，满足 Task 1 的产物清单
    native_pred = out / "predictions" / "coarse_human_to_mouse.json"
    native_conf = out / "confusion" / "coarse_human_to_mouse.json"
    if not native_pred.exists() or not native_conf.exists():
        die("patched run did not emit the expected per-cell/confusion files", 4)
    (out / "predictions.json").write_text(native_pred.read_text(encoding="utf-8"), encoding="utf-8")
    (out / "confusion.json").write_text(native_conf.read_text(encoding="utf-8"), encoding="utf-8")

    env_json = load_json(out / "environment.json")
    (out / "environment.txt").write_text(
        "\n".join([
            "task=task-1-a-smoke",
            "direction=%s" % DIRECTION,
            "level=%s" % LEVEL,
            "nperm=%d" % NPERM_EXPECTED,
            "interpreter=%s" % sys.executable,
            "python=%s" % platform.python_version(),
            "platform=%s" % platform.platform(),
            "numpy=%s" % env_json.get("numpy"),
            "anndata=%s" % env_json.get("anndata"),
            "scanpy=%s" % env_json.get("scanpy"),
            "sklearn=%s" % env_json.get("sklearn"),
            "wrapper=%s" % Path(__file__).resolve(),
            "wrapper_sha256=%s" % sha256_file(Path(__file__).resolve()),
            "authoritative_source=%s" % SOURCE,
            "authoritative_source_sha256=%s" % sha256_text(original),
            "patched_source_sha256=%s" % sha256_text(patched),
        ]) + "\n", encoding="utf-8")

    (out / "wrapper-provenance.json").write_text(json.dumps({
        "task": "task-1-a-smoke-provenance",
        "why": ("ortholog_pca_local_v1.py 无法限定物种/方向/层级，且全量模式无守卫直写冻结目录；"
                "本 wrapper 用锚点断言过的文本补丁把执行范围限制到 human->mouse / coarse，"
                "并把补丁后的源码落盘执行，使复现在构造上协议保真。"),
        "wrapper": str(Path(__file__).resolve()),
        "wrapper_sha256": sha256_file(Path(__file__).resolve()),
        "authoritative_source": str(SOURCE),
        "authoritative_source_sha256": sha256_text(original),
        "patched_source": str(patched_path),
        "patched_source_sha256": sha256_text(patched),
        "patches": patch_records,
        "patch_count": len(patch_records),
        "unified_diff": diff,
        "preflight_checks": checks,
        "scope": {"species": ["human", "mouse"], "directions": [DIRECTION],
                  "levels": [LEVEL], "nperm": NPERM_EXPECTED},
        "frozen_root_untouched": str(FROZEN_ROOT),
        "invocation": " ".join([sys.executable] + sys.argv),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    report = verify(out)
    n_files = write_sha256_tsv(out)
    print("DONE|status=%s|files_hashed=%d|elapsed=%.1fs"
          % (report["status"], n_files, time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
