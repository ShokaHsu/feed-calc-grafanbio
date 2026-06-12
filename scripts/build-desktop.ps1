# scripts/build-desktop.ps1
param(
    [switch]$SkipSeed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Paths — all relative to repo root (parent of this script's directory)
$Root        = Split-Path $PSScriptRoot -Parent
$Backend     = Join-Path $Root 'feed_calc_backend'
$Frontend    = Join-Path $Root 'feed_calc_frontend'
$SidecarSrc  = Join-Path $Backend  'dist\feed_calc_api.exe'
$SidecarDest = Join-Path $Frontend 'src-tauri\bin\feed_calc_api-x86_64-pc-windows-msvc.exe'

function Step($n, $msg) { Write-Host "`n=== Step ${n}: $msg ===" -ForegroundColor Cyan }
function OK($msg)        { Write-Host "  OK: $msg"             -ForegroundColor Green }
function Fail($msg)      { Write-Host "  FAIL: $msg"           -ForegroundColor Red; exit 1 }

# ── Step 0: Kill stale sidecar ───────────────────────────────────────────────
Step 0 'Kill stale sidecar'
$procs = @(Get-Process -Name feed_calc_api -ErrorAction SilentlyContinue)
if ($procs) {
    $procs | Stop-Process -Force
    OK "Killed $($procs.Count) stale process(es)"
} else {
    OK 'No stale process found'
}

# ── Step 1: Seed database ────────────────────────────────────────────────────
if (-not $SkipSeed) {
    Step 1 'Seed database'
    Push-Location $Backend
    try {
        Remove-Item 'db.sqlite3' -ErrorAction SilentlyContinue
        OK 'Deleted existing db.sqlite3 (clean slate)'

        python manage.py migrate --no-input
        if ($LASTEXITCODE -ne 0) { Fail 'manage.py migrate failed' }
        OK 'Migrations applied'

        python manage.py import_ingredients
        if ($LASTEXITCODE -ne 0) { Fail 'import_ingredients failed' }
        OK 'Ingredients seeded from Excel'

        $crawledFixture = Join-Path $Backend 'ingredients\fixtures\crawled_seed.json'
        if (Test-Path $crawledFixture) {
            python manage.py loaddata $crawledFixture
            if ($LASTEXITCODE -ne 0) { Fail 'loaddata crawled_seed failed' }
            OK 'Crawled ingredients loaded from fixture'
        } else {
            Write-Host "  WARNING: $crawledFixture not found — skipping crawled seed" -ForegroundColor Yellow
        }

        python manage.py load_nrc_json
        if ($LASTEXITCODE -ne 0) { Fail 'load_nrc_json failed' }
        OK 'NRC standards seeded'
    } finally {
        Pop-Location
    }
} else {
    Step 1 'Seed database (SKIPPED via -SkipSeed)'
}

# ── Step 2: Build sidecar with PyInstaller ───────────────────────────────────
Step 2 'Build sidecar with PyInstaller'
Push-Location $Backend
try {
    python -m PyInstaller feed_calc_api.spec --noconfirm
    if ($LASTEXITCODE -ne 0) { Fail 'PyInstaller failed' }
    if (-not (Test-Path 'dist\feed_calc_api.exe')) {
        Fail 'dist\feed_calc_api.exe not found after PyInstaller — check the spec'
    }
    OK "Sidecar built: $((Get-Item 'dist\feed_calc_api.exe').Length / 1MB -as [int]) MB"
} finally {
    Pop-Location
}

# ── Step 3: Copy binary to Tauri ─────────────────────────────────────────────
Step 3 'Copy sidecar binary to Tauri'
if (-not (Test-Path $SidecarSrc)) {
    Fail "Source not found: $SidecarSrc"
}
Copy-Item $SidecarSrc $SidecarDest -Force
OK "Copied to $SidecarDest"
OK "$((Get-Item $SidecarDest).Length / 1MB -as [int]) MB"

# ── Step 4: Tauri build ───────────────────────────────────────────────────────
Step 4 'Build Tauri installer'
Push-Location $Frontend
try {
    npx tauri build
    if ($LASTEXITCODE -ne 0) { Fail 'tauri build failed' }
    OK 'Tauri build complete'
} finally {
    Pop-Location
}

# ── Step 5: Report ────────────────────────────────────────────────────────────
Step 5 'Done — installer output'
$BundleDir = Join-Path $Frontend 'src-tauri\target\release\bundle'
$Installers = Get-ChildItem $BundleDir -Recurse -Include '*.exe','*.msi' -ErrorAction SilentlyContinue
if ($Installers) {
    $Installers | ForEach-Object {
        Write-Host "  $($_.FullName)  ($([int]($_.Length/1MB)) MB)" -ForegroundColor Green
    }
} else {
    Write-Host "  WARNING: No installer found in $BundleDir" -ForegroundColor Yellow
}
