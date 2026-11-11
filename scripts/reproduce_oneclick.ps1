<#
  reproduce_oneclick.ps1 —— 课题5 一键复现（无 GPU / 无 WSL / 无 docker）
  用法：
    powershell -ExecutionPolicy Bypass -File scripts\reproduce_oneclick.ps1
    powershell -ExecutionPolicy Bypass -File scripts\reproduce_oneclick.ps1 -Fast        # 跳过 heavy 步
    powershell -ExecutionPolicy Bypass -File scripts\reproduce_oneclick.ps1 -Python "C:\...\python.exe"

  退出码：0 = 30/30 全过；非 0 = 有步骤失败，看打印的 manifest 路径。
#>
param(
    [string]$Python = "",
    [switch]$Fast,
    [string]$Out = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repo
$env:PYTHONIOENCODING = "utf-8"

# 1) 选解释器：显式指定 > .venv39 > PATH 上的 python
if (-not $Python) {
    $cand = Join-Path $repo ".venv39\Scripts\python.exe"
    if (Test-Path $cand) {
        $Python = $cand
    } else {
        $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    }
}
if (-not $Python -or -not (Test-Path $Python)) {
    Write-Host "[FAIL] 找不到可用的 python，请用 -Python 指定绝对路径" -ForegroundColor Red
    exit 2
}
Write-Host "[1/4] 解释器: $Python"
& $Python -c "import sys;print('      Python', sys.version.split()[0])"

# 2) 依赖自检（缺了直接说缺什么，不假装能跑）
$probe = & $Python -c @"
mods=[]
for m in ('numpy','scipy','sklearn'):
    try:
        __import__(m); mods.append(m)
    except Exception:
        pass
print(','.join(mods))
"@
Write-Host "[2/4] 已装依赖: $probe"
if ($probe -notmatch "numpy") {
    Write-Host "[FAIL] 缺 numpy/scipy/sklearn：先跑 $Python -m pip install -r requirements.txt" -ForegroundColor Red
    exit 3
}

# 3) 跑复现
$outArg = if ($Out) { $Out } else { "results\repro-oneclick-$(Get-Date -Format 'yyyyMMdd-HHmmss')" }
$args = @("scripts\reproduce_all.py", "--out", $outArg)
if ($Fast) { $args += "--fast" }
Write-Host "[3/4] 执行: $Python $($args -join ' ')"
& $Python @args
$rc = $LASTEXITCODE

# 4) 报告
Write-Host "[4/4] 退出码: $rc"
$manifest = Join-Path $repo (Join-Path $outArg "manifest.json")
if (Test-Path $manifest) {
    Write-Host "      manifest: $manifest"
    & $Python -c "import json,sys;m=json.load(open(sys.argv[1],encoding='utf-8'));print('      steps_ok=%s/%s duration=%.1fs'%(m.get('steps_ok'),m.get('steps_total'),m.get('duration_s') or 0))" $manifest
} else {
    Write-Host "      [WARN] 没找到 manifest.json" -ForegroundColor Yellow
}
exit $rc