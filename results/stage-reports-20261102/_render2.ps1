param(
  [Parameter(Mandatory=$true)][string]$Pptx,
  [Parameter(Mandatory=$true)][string]$OutDir
)
$ErrorActionPreference = 'Stop'
$soffice = 'C:\Program Files\LibreOffice\program\soffice.com'
$pdftoppm = (Get-Command pdftoppm).Source
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Pptx = (Resolve-Path $Pptx).Path
& $soffice --headless --norestore --convert-to pdf --outdir $OutDir $Pptx | Out-Null
$pdf = Join-Path $OutDir ([System.IO.Path]::GetFileNameWithoutExtension($Pptx) + '.pdf')
if(-not (Test-Path $pdf)){ throw "pdf not produced: $pdf" }
Get-ChildItem (Join-Path $OutDir 's*.png') -ErrorAction SilentlyContinue | Remove-Item -Force
& $pdftoppm -png -r 110 $pdf (Join-Path $OutDir 's')
$pngs = Get-ChildItem (Join-Path $OutDir 's*.png') | Sort-Object Name
Write-Host "pages: $($pngs.Count)"
$pngs | ForEach-Object {
  Add-Type -AssemblyName System.Drawing
  $img = [System.Drawing.Image]::FromFile($_.FullName)
  "{0}  {1}x{2}" -f $_.Name, $img.Width, $img.Height
  $img.Dispose()
}
