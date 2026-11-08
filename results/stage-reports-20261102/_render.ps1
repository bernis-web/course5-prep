# 把 stage-reports-20261102 里的 pptx 重新导出 PDF + s01..s15.png
# 复用本机现成工具链：LibreOffice(soffice) -> Poppler(pdftoppm)，110 dpi 与旧图一致
# 用法: pwsh -File _render.ps1
$ErrorActionPreference = 'Stop'

$dir  = 'D:\projects\course5-prep\results\stage-reports-20261102'
$pptx = Join-Path $dir '课题5第03次汇报_三场景结论与可复现闭环.pptx'
$out  = Join-Path $dir 'render'

if (-not (Test-Path $pptx)) { throw "missing pptx: $pptx" }
New-Item -ItemType Directory -Force -Path $out | Out-Null

$soffice = 'C:\Program Files\LibreOffice\program\soffice.exe'
$pdftoppm = (Get-Command pdftoppm.exe).Source

# 1) pptx -> pdf（独立 profile，避免和已开的 soffice 抢锁）
$profile = Join-Path $env:TEMP ('lo-prof-' + [guid]::NewGuid().ToString('N'))
& $soffice "--headless" "-env:UserInstallation=file:///$($profile -replace '\\','/')" `
    "--convert-to" "pdf" "--outdir" $out $pptx | Out-Null

$pdf = Join-Path $out ([IO.Path]::GetFileNameWithoutExtension($pptx) + '.pdf')
if (-not (Test-Path $pdf)) { throw "pdf not produced: $pdf" }

# 2) pdf -> png（-sep "" 得到 s01.png..s15.png）
Get-ChildItem $out -Filter 's??.png' | Remove-Item -Force
& $pdftoppm -png -r 110 -sep '' $pdf (Join-Path $out 's') | Out-Null

$imgs = Get-ChildItem $out -Filter 's??.png' | Sort-Object Name
"pdf : {0} ({1:N0} bytes)" -f (Split-Path $pdf -Leaf), (Get-Item $pdf).Length
"png : {0} files" -f $imgs.Count
$imgs | ForEach-Object { "  {0}  {1:N0} bytes" -f $_.Name, $_.Length }

Remove-Item -Recurse -Force $profile -ErrorAction SilentlyContinue
