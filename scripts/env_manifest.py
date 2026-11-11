# -*- coding: utf-8 -*-
"""生成环境清单：解释器 / 版本 / 关键依赖 / OS —— 复现前先看这份。"""
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\projects\course5-prep")
V39 = ROOT / ".venv39" / "Scripts" / "python.exe"
V313 = Path(r"C:\Users\28417\AppData\Local\Programs\Python\Python313\python.exe")


def probe(py: Path):
    if not py.exists():
        return {"path": str(py), "exists": False}
    code = (
        "import json,sys,platform;"
        "d={'python':sys.version.split()[0],'exe':sys.executable,'platform':platform.platform(),"
        "'machine':platform.machine()};"
        "\nfor m in ('numpy','scipy','sklearn','docx','pptx','fitz','h5py','pandas'):\n"
        "    try:\n"
        "        mod=__import__(m); d[m]=getattr(mod,'__version__','?')\n"
        "    except Exception as e:\n"
        "        d[m]='缺('+type(e).__name__+')'\n"
        "print(json.dumps(d,ensure_ascii=False))"
    )
    out = subprocess.run([str(py), "-c", code], capture_output=True, text=True, timeout=120,
                               encoding="utf-8", errors="replace")
    try:
        d = json.loads(out.stdout.strip().splitlines()[-1])
    except Exception:
        d = {"path": str(py), "error": out.stdout[-300:] + out.stderr[-300:]}
    d["path"] = str(py)
    return d


rows = {"os": platform.platform(), "host": platform.node(),
        "python_venv39": probe(V39), "python313": probe(V313)}

# requirements 声明值
req = ROOT / "requirements.txt"
declared = {}
if req.exists():
    for ln in req.read_text(encoding="utf-8").splitlines():
        if "==" in ln:
            k, v = ln.split("==", 1)
            declared[k.strip()] = v.strip()
rows["requirements"] = declared

L = ["# 复现环境清单（2026-11-11）", "",
     f"- 操作系统：`{rows['os']}`",
     f"- 主机：`{rows['host']}`",
     "- 说明：**不依赖 GPU / WSL / docker**；纯 CPU 可跑完 30 个步骤。", "",
     "## 解释器与依赖", "",
     "| 环境 | 路径 | Python | numpy | scipy | scikit-learn | python-docx | python-pptx | PyMuPDF | h5py | pandas |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for k in ("python_venv39", "python313"):
    d = rows[k]
    if not d.get("exists", True):
        L.append(f"| {k} | `{d['path']}` | 不存在 | - | - | - | - | - | - |")
        continue
    L.append(f"| {k} | `{d.get('exe', d['path'])}` | {d.get('python', '?')} | {d.get('numpy','?')} | "
             f"{d.get('scipy','?')} | {d.get('sklearn','?')} | {d.get('docx','?')} | "
             f"{d.get('pptx','?')} | {d.get('fitz','?')} | {d.get('h5py','?')} | {d.get('pandas','?')} |")
L += ["", "## requirements.txt 声明值", "", "| 包 | 声明版本 |", "|---|---|"]
L += [f"| {k} | {v} |" for k, v in declared.items()]
L += ["", "## 一键入口", "",
      "```powershell",
      "cd D:\\projects\\course5-prep",
      "powershell -ExecutionPolicy Bypass -File scripts\\reproduce_oneclick.ps1",
      "```", "",
      "脚本做的事：选解释器 → 建 sandbox → 跑 30 步 → 校验退出码 → 打印 manifest 路径。",
      ""]
out = ROOT / "docs" / "execution" / "env-manifest-20261111.md"
out.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
print("写出", out)