# Desktop Packaging Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `scripts/build-desktop.ps1` — a single PowerShell script that goes from clean source to a Windows installer by seeding SQLite, building the Django sidecar with PyInstaller, and running `tauri build`.

**Architecture:** One new file at repo root (`scripts/build-desktop.ps1`). The script sequences six steps with error-checking between each. A `-SkipSeed` flag lets you skip the slow DB seeding step on quick rebuilds.

**Tech Stack:** PowerShell 5.1, PyInstaller, Django management commands, Tauri v2 CLI (`@tauri-apps/cli`), Cargo/Rust

---

## File Map

| Action | Path |
|---|---|
| **Create** | `scripts/build-desktop.ps1` |

No existing files are modified. The script overwrites `feed_calc_backend/db.sqlite3` (intentionally) and `feed_calc_frontend/src-tauri/bin/feed_calc_api-x86_64-pc-windows-msvc.exe` (the sidecar binary).

---

## Pre-flight: Verify toolchain

Before running the script for the first time, confirm these tools are on PATH:

```powershell
python --version         # needs to be the venv / system Python that has Django + PyInstaller
python -m PyInstaller --version
node --version
npm --version
rustc --version
cargo --version
```

Also confirm `@tauri-apps/cli` is installed in `feed_calc_frontend/`:
```powershell
Set-Location feed_calc_frontend
npx tauri --version
```

If any command fails, install the missing tool before running the build script.

---

### Task 1: Create `scripts/build-desktop.ps1` — skeleton + helpers

**Files:**
- Create: `scripts/build-desktop.ps1`

- [ ] **Step 1: Create the `scripts/` directory and write the skeleton**

```powershell
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

function Step($n, $msg) { Write-Host "`n=== Step $n: $msg ===" -ForegroundColor Cyan }
function OK($msg)        { Write-Host "  OK: $msg"             -ForegroundColor Green }
function Fail($msg)      { Write-Host "  FAIL: $msg"           -ForegroundColor Red; exit 1 }
```

- [ ] **Step 2: Verify the skeleton parses without error**

```powershell
powershell -NonInteractive -Command "& { . '.\scripts\build-desktop.ps1' -SkipSeed }"
```

Expected: script runs, prints nothing (no steps yet), exits 0. If you get a parse error, fix it before continuing.

- [ ] **Step 3: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: add build-desktop.ps1 skeleton"
```

---

### Task 2: Step 0 — Kill stale sidecar

**Files:**
- Modify: `scripts/build-desktop.ps1`

- [ ] **Step 1: Append Step 0 block to the script (after the helpers)**

```powershell
# ── Step 0: Kill stale sidecar ───────────────────────────────────────────────
Step 0 'Kill stale sidecar'
$procs = Get-Process -Name feed_calc_api -ErrorAction SilentlyContinue
if ($procs) {
    $procs | Stop-Process -Force
    OK "Killed $($procs.Count) stale process(es)"
} else {
    OK 'No stale process found'
}
```

- [ ] **Step 2: Run the script and verify Step 0 output**

```powershell
.\scripts\build-desktop.ps1 -SkipSeed
```

Expected output includes:
```
=== Step 0: Kill stale sidecar ===
  OK: No stale process found
```

(If a sidecar was running it will say "Killed 1 stale process(es)".)

- [ ] **Step 3: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: build-desktop step 0 — kill stale sidecar"
```

---

### Task 3: Step 1 — Seed database

**Files:**
- Modify: `scripts/build-desktop.ps1`

- [ ] **Step 1: Append Step 1 block**

```powershell
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
        OK 'Ingredients seeded'

        python manage.py load_nrc_json
        if ($LASTEXITCODE -ne 0) { Fail 'load_nrc_json failed' }
        OK 'NRC standards seeded'
    } finally {
        Pop-Location
    }
} else {
    Step 1 'Seed database (SKIPPED via -SkipSeed)'
}
```

- [ ] **Step 2: Run with seeding enabled and verify**

```powershell
.\scripts\build-desktop.ps1
```

Stop after this step completes (Ctrl+C before PyInstaller if you want to test incrementally — or just let it continue). Expected output:

```
=== Step 1: Seed database ===
  OK: Deleted existing db.sqlite3 (clean slate)
  OK: Migrations applied
  OK: Ingredients seeded
  OK: NRC standards seeded
```

Also confirm `feed_calc_backend/db.sqlite3` now exists and is non-zero:

```powershell
(Get-Item 'feed_calc_backend\db.sqlite3').Length
```

Expected: a number > 0 (typically several hundred KB).

- [ ] **Step 3: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: build-desktop step 1 — seed database"
```

---

### Task 4: Step 2 — Build sidecar with PyInstaller

**Files:**
- Modify: `scripts/build-desktop.ps1`

- [ ] **Step 1: Append Step 2 block**

```powershell
# ── Step 2: Build sidecar ────────────────────────────────────────────────────
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
```

- [ ] **Step 2: Run and verify**

```powershell
.\scripts\build-desktop.ps1 -SkipSeed
```

Expected output for step 2:
```
=== Step 2: Build sidecar with PyInstaller ===
  OK: Sidecar built: <N> MB
```

PyInstaller is slow (~2 minutes). If it fails with a missing module error, add the module to `hiddenimports` in `feed_calc_backend/feed_calc_api.spec` and re-run.

- [ ] **Step 3: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: build-desktop step 2 — PyInstaller sidecar"
```

---

### Task 5: Step 3 — Copy binary to Tauri

**Files:**
- Modify: `scripts/build-desktop.ps1`

- [ ] **Step 1: Append Step 3 block**

```powershell
# ── Step 3: Copy binary to Tauri ─────────────────────────────────────────────
Step 3 'Copy sidecar binary to Tauri'
if (-not (Test-Path $SidecarSrc)) {
    Fail "Source not found: $SidecarSrc"
}
Copy-Item $SidecarSrc $SidecarDest -Force
OK "Copied to $SidecarDest"
OK "$((Get-Item $SidecarDest).Length / 1MB -as [int]) MB"
```

- [ ] **Step 2: Run and verify the file is in place**

```powershell
.\scripts\build-desktop.ps1 -SkipSeed
```

Expected:
```
=== Step 3: Copy sidecar binary to Tauri ===
  OK: Copied to ...\feed_calc_frontend\src-tauri\bin\feed_calc_api-x86_64-pc-windows-msvc.exe
  OK: <N> MB
```

Also confirm the destination file exists:
```powershell
Test-Path 'feed_calc_frontend\src-tauri\bin\feed_calc_api-x86_64-pc-windows-msvc.exe'
```
Expected: `True`

- [ ] **Step 3: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: build-desktop step 3 — copy binary to Tauri"
```

---

### Task 6: Step 4 — Tauri build + Step 5 — Report

**Files:**
- Modify: `scripts/build-desktop.ps1`

- [ ] **Step 1: Append Step 4 and Step 5 blocks**

```powershell
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
```

- [ ] **Step 2: Run the full build end-to-end**

This is the first full run. Expect it to take 5-15 minutes (PyInstaller + Rust compile):

```powershell
.\scripts\build-desktop.ps1
```

Expected final output:
```
=== Step 5: Done — installer output ===
  C:\...\bundle\nsis\FomuMaster_0.1.0_x64-setup.exe  (N MB)
  C:\...\bundle\msi\FomuMaster_0.1.0_x64_en-US.msi   (N MB)
```

If the build fails at the Tauri step, check the Rust compile error — often a missing Tauri plugin or a CSP issue.

- [ ] **Step 3: Smoke-test the installer**

Run the produced `.exe` installer. After install:
1. Launch **FomuMaster** from the Start menu
2. Confirm the ingredient list loads (not empty) — this verifies the bundled SQLite is seeded
3. Open DevTools (F12) and confirm no network errors to `http://127.0.0.1:8042/api`
4. Open `%APPDATA%\FeedCalc\` in Explorer — confirm `db.sqlite3` is present (copied on first run)

- [ ] **Step 4: Commit**

```powershell
git add scripts/build-desktop.ps1
git commit -m "feat: build-desktop step 4+5 — Tauri build and report"
```

---

### Task 7: Final verification commit

- [ ] **Step 1: Run with -SkipSeed to verify quick-rebuild path works**

```powershell
.\scripts\build-desktop.ps1 -SkipSeed
```

Expected: all steps run, Step 1 says `(SKIPPED)`, full build completes.

- [ ] **Step 2: Confirm the script is the only new file**

```powershell
git status
```

Expected: working tree clean (the sidecar binary and `db.sqlite3` are already in `.gitignore` or tracked).

- [ ] **Step 3: Tag as ready**

No additional commit needed — all commits were made incrementally. The plan is complete.

---

## Troubleshooting

**PyInstaller: "ModuleNotFoundError" at runtime**
Add the missing module to `hiddenimports` in `feed_calc_backend/feed_calc_api.spec`, then re-run from Task 4.

**Tauri: "ERROR: sidecar not found"**
Confirm `feed_calc_frontend/src-tauri/bin/feed_calc_api-x86_64-pc-windows-msvc.exe` exists after Step 3.

**API unreachable in installed app**
Open `%APPDATA%\FeedCalc\startup.log` — `desktop.py` writes startup diagnostics there. Look for `[startup] ERROR` lines.

**db.sqlite3 empty after install**
Check `startup.log` for the copy decision. If `bundled_db.exists()=False`, PyInstaller didn't bundle the db — confirm `('db.sqlite3', '.')` is in the `datas` list in `feed_calc_api.spec`.
