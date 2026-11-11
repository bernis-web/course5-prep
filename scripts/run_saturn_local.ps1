<#
.SYNOPSIS
    本地 CPU 跑 SATURN 官方训练 + 六方向打分（Windows / 无 GPU）

.DESCRIPTION
    平台离线任务长时间不启动时的本地兜底路径。把 2026-11-11 实测踩过的坑
    全部固化成可重复执行的步骤。

    前置（只需一次）：
        .venv39\Scripts\python.exe scripts\make_scvi_stub.py
        .venv39\Scripts\python.exe -m pip install scikit-misc

.PARAMETER PretrainEpochs
    预训练轮数。默认 200（SATURN 原论文量级）。1 epoch ≈ 12.8 s（本机 8 核）。

.PARAMETER Epochs
    metric learning 轮数。默认 50。

.PARAMETER Tag
    输出子目录名（local_run_<Tag>）。默认 full。

.PARAMETER SkipTrain
    只打分不训练（用于对已有产物重跑打分）。

.EXAMPLE
    .\scripts\run_saturn_local.ps1 -PretrainEpochs 1 -Epochs 1 -Tag smoke
    .\scripts\run_saturn_local.ps1 -Tag full
    .\scripts\run_saturn_local.ps1 -SkipTrain -Tag full
#>
[CmdletBinding()]
param(
    [int]$PretrainEpochs = 200,
    [int]$Epochs = 50,
    [string]$Tag = "full",
    [switch]$SkipTrain,
    [int]$Seed = 0
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $Root

$Py = Join-Path $Root ".venv39\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw "找不到 Python: $Py" }

$Src = Join-Path $Root "wheelhouse\saturn-src"
$env:PYTHONPATH = $Src
$env:PYTHONIOENCODING = "utf-8"

$WorkDir = Join-Path $Root "local_run_$Tag"
$LogDir = Join-Path $WorkDir "log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$InData = Join-Path $Root "local_saturn_in_data.csv"
if (-not (Test-Path $InData)) {
    Write-Host "[1/4] 生成 in_data.csv"
    $emb = "D:/projects/course5-prep/wheelhouse/protein_embeddings_export/ESM2"
    $lines = @("species,path,embedding_path,in_label_col")
    foreach ($s in @("human", "mouse", "zebrafish")) {
        $lines += "$s,D:/projects/course5-prep/local_${s}_s.h5ad,$emb/${s}_embedding.torch,cell_type"
    }
    $lines -join "`n" | Set-Content -LiteralPath $InData -Encoding ASCII
} else {
    Write-Host "[1/4] in_data.csv 已存在，跳过"
}

# scvi stub 必须存在，否则 saturn_model.py 的 import 就崩
$StubInit = Join-Path $Root ".venv39\Lib\site-packages\scvi\__init__.py"
if (-not (Test-Path $StubInit)) {
    Write-Host "[2/4] 缺 scvi stub，生成中"
    & $Py (Join-Path $Root "scripts\make_scvi_stub.py")
    if ($LASTEXITCODE -ne 0) { throw "scvi stub 生成失败" }
} else {
    Write-Host "[2/4] scvi stub 在位"
}

if ($SkipTrain) {
    Write-Host "[3/4] -SkipTrain，跳过训练"
} else {
    Write-Host "[3/4] 开始训练：pretrain=$PretrainEpochs metric=$Epochs seed=$Seed"
    Write-Host "      输出 -> $WorkDir"
    $t0 = Get-Date
    & $Py (Join-Path $Src "train-saturn.py") `
        --in_data $InData `
        --device cpu `
        --work_dir $WorkDir `
        --log_dir $LogDir `
        --embedding_model ESM2 `
        --in_label_col cell_type `
        --ref_label_col cell_type `
        --pretrain_epochs $PretrainEpochs `
        --epochs $Epochs `
        --seed $Seed
    if ($LASTEXITCODE -ne 0) { throw "训练失败，退出码 $LASTEXITCODE" }
    Write-Host ("      训练耗时 {0:N1} 分钟" -f ((Get-Date) - $t0).TotalMinutes)
}

# 取最终产物（排除 pretrain 中间件）
$ResDir = Join-Path $WorkDir "saturn_results"
$Final = Get-ChildItem $ResDir -Filter "*.h5ad" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notlike "*pretrain*" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $Final) { throw "找不到最终 h5ad：$ResDir" }

Write-Host "[4/4] 打分：$($Final.Name)"
$Map = Join-Path $Root "config\heart-celltype-map-v2.tsv"
$OutJson = Join-Path $Root "results\saturn-official-20261111\saturn_scores_$Tag.json"
$scoreArgs = @((Join-Path $Root "scripts\saturn_output_scores.py"), "--adata", $Final.FullName, "--out", $OutJson)
if (Test-Path $Map) { $scoreArgs += @("--map", $Map) }
& $Py @scoreArgs
if ($LASTEXITCODE -ne 0) { throw "打分失败，退出码 $LASTEXITCODE" }

# 核对嵌入维度
& $Py -c @"
import anndata as ad, sys
a = ad.read_h5ad(r'$($Final.FullName)')
print('X shape:', a.X.shape, '| obsm:', list(a.obsm.keys()))
assert a.X.shape[1] == 256, f'期望 256 维，实际 {a.X.shape[1]}'
print('维度核对通过：256')
"@
if ($LASTEXITCODE -ne 0) { throw "维度核对失败" }

Write-Host ""
Write-Host "完成。产物：$($Final.FullName)"
Write-Host "分数：$OutJson"