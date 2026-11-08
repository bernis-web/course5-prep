from pathlib import Path
import subprocess
import sys

import fitz

root = Path(__file__).resolve().parent
pptx = root / "课题5第01次汇报_先把比较做公平.pptx"
out_dir = root / "render-reframed"
out_dir.mkdir(exist_ok=True)
soffice = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")

result = subprocess.run(
    [str(soffice), "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx)],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout.strip())
if result.returncode:
    print(result.stderr.strip(), file=sys.stderr)
    raise SystemExit(result.returncode)

pdf = out_dir / (pptx.stem + ".pdf")
doc = fitz.open(pdf)
print(f"PAGES={doc.page_count}")
problems = []
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=110)
    pix.save(out_dir / f"p{i + 1:02}.png")
    width, height = page.rect.width, page.rect.height
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text = block[:5]
        if text.strip() and (x0 < -1 or y0 < -1 or x1 > width + 1 or y1 > height + 1):
            problems.append(f"p{i + 1} OUT_OF_PAGE {text.strip()[:40]!r}")
doc.close()
print("BOUNDS_CLEAN" if not problems else "\n".join(problems))
