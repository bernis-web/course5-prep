"""Peak-memory self-report for the frozen oPCA run (no extra deps).

Wraps scripts/opca_stability_run.py: imports it, runs main(), then reads this
process's peak working set via ctypes + psapi.GetProcessMemoryInfo (Windows) or
/proc/self/status VmHWM (Linux).  Prints a single PEAK line that callers parse.

Why in-process: an external poller (Start-Process + Refresh) reported ~4 MB,
which is the poller's own accounting, not the child's -- unreliable.  Reading
PeakWorkingSetSize from inside the measuring process is exact.
"""
import ctypes
import json
import os
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def peak_ws_mb():
    if sys.platform == "win32":
        c = PROCESS_MEMORY_COUNTERS()
        c.cb = ctypes.sizeof(c)
        h = ctypes.windll.kernel32.GetCurrentProcess()
        for dll, fn in ((ctypes.windll.psapi, "GetProcessMemoryInfo"),
                        (ctypes.windll.kernel32, "K32GetProcessMemoryInfo")):
            try:
                f = getattr(dll, fn)
                f.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
                f.restype = wintypes.BOOL
                if f(h, ctypes.byref(c), c.cb):
                    return (round(c.PeakWorkingSetSize / (1024 * 1024), 1),
                            round(c.PeakPagefileUsage / (1024 * 1024), 1))
            except Exception:
                continue
        return None, None
    for line in open("/proc/self/status", encoding="utf-8"):
        if line.startswith("VmHWM:"):
            kb = int(line.split()[1])
            return round(kb / 1024, 1), None
    return None, None


def main():
    sys.path.insert(0, str(ROOT / "scripts"))
    import opca_stability_run as h
    t0 = time.time()
    h.main()
    wall = round(time.time() - t0, 2)
    ws, priv = peak_ws_mb()
    rec = {
        "wall_sec_total": wall,
        "peak_working_set_mb": ws,
        "peak_pagefile_mb": priv,
        "python": sys.version.split()[0],
        "seed": os.environ.get("STAB_SEED"),
        "nperm": os.environ.get("STAB_NPERM"),
        "h5ad_dir": os.environ.get("OPCA_H5AD_DIR"),
        "out": os.environ.get("OPCA_OUT"),
    }
    print("PEAK|" + json.dumps(rec), flush=True)
    outp = Path(os.environ["OPCA_OUT"]) / "resource.json"
    outp.write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
