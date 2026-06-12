# Desktop Packaging Pipeline — FeedCalc

**Date:** 2026-05-12
**Scope:** Reproducible build script (PowerShell) to go from clean source → seeded SQLite → PyInstaller sidecar → Tauri Windows installer

---

## Goals

Produce a single, repeatable command that builds a distributable Windows installer for the FomuMaster desktop app. The installer must bundle:
- The Vue frontend (Vite, built with `.env.desktop`)
- The Django sidecar (`feed_calc_api.exe`, produced by PyInstaller)
- A clean, fully seeded SQLite database (`db.sqlite3`)

---

## Architecture Overview

```
scripts/build-desktop.ps1
  │
  ├─ [Step 0] Kill stale feed_calc_api.exe process
  ├─ [Step 1] Seed db.sqlite3 (clean rebuild)
  │     └─ manage.py migrate → import_ingredients → load_nrc_json
  ├─ [Step 2] PyInstaller → dist/feed_calc_api.exe
  ├─ [Step 3] Copy binary to src-tauri/bin/feed_calc_api-x86_64-pc-windows-msvc.exe
  └─ [Step 4] cargo tauri build
                └─ beforeBuildCommand: npm run build:desktop (Vite with .env.desktop)
```

---

## Script

**File:** `scripts/build-desktop.ps1`

**Usage:**
```powershell
.\scripts\build-desktop.ps1           # full build (seed + PyInstaller + Tauri)
.\scripts\build-desktop.ps1 -SkipSeed # skip seeding (faster rebuilds when data unchanged)
```

### Steps

| Step | Command | Error behaviour |
|---|---|---|
| 0. Pre-flight | Kill `feed_calc_api` process | Warn and continue |
| 1. Seed DB | `migrate` → `import_ingredients` → `load_nrc_json` | Stop on error |
| 2. PyInstaller | `pyinstaller feed_calc_api.spec` | Stop on error |
| 3. Copy binary | `dist/feed_calc_api.exe` → `src-tauri/bin/feed_calc_api-x86_64-pc-windows-msvc.exe` | Stop on error |
| 4. Tauri build | `cargo tauri build` | Stop on error |
| 5. Report | Print path to produced installer | — |

---

## SQLite Seeding Strategy

Before PyInstaller runs, the script deletes and recreates `feed_calc_backend/db.sqlite3` to guarantee no dev artifacts (test formulas, dev sessions) leak into the bundle:

```powershell
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
python manage.py migrate --no-input
python manage.py import_ingredients
python manage.py load_nrc_json
```

All three management commands are idempotent and already run on every Railway deploy.

**On first install:** `desktop.py` copies the bundled DB to `%APPDATA%\FeedCalc\db.sqlite3` (missing → copy).

**On app update:** `run_api.py` calls `manage.py migrate` at every startup, so schema migrations apply automatically. Seed data (ingredients, NRC standards) is **not** re-applied to existing user DBs — this preserves user formulas. The copy-if-smaller logic in `desktop.py` only copies when the user DB is smaller than the bundle (handles empty/corrupted user DB cases).

---

## Binary Copy

PyInstaller outputs to `feed_calc_backend/dist/feed_calc_api.exe`.

Tauri v2 resolves `"externalBin": ["bin/feed_calc_api"]` by looking for `src-tauri/bin/feed_calc_api-<target-triple>.exe`. The correct triple for Windows x64 is `x86_64-pc-windows-msvc`.

```powershell
$src  = "feed_calc_backend\dist\feed_calc_api.exe"
$dest = "feed_calc_frontend\src-tauri\bin\feed_calc_api-x86_64-pc-windows-msvc.exe"
Copy-Item $src $dest -Force
```

---

## Tauri Build

```powershell
Set-Location feed_calc_frontend
cargo tauri build
```

`tauri.conf.json` has `"beforeBuildCommand": "npm run build:desktop"` — Vite runs automatically with `.env.desktop` (API at `http://127.0.0.1:8042/api`) before the Rust compilation. No separate npm step needed.

**Output:** `feed_calc_frontend/src-tauri/target/release/bundle/`
- NSIS installer (`.exe`)
- MSI installer (`.msi`)

Both produced because `tauri.conf.json` has `"targets": "all"`.

---

## Key Files

| File | Role |
|---|---|
| `scripts/build-desktop.ps1` | **New** — orchestrates the full build |
| `feed_calc_backend/feed_calc_api.spec` | PyInstaller spec — bundles Django + db.sqlite3 |
| `feed_calc_backend/run_api.py` | Sidecar entry point — runs `migrate` at startup, serves on port 8042 |
| `feed_calc_backend/config/settings/desktop.py` | DB path resolution and copy-on-first-run logic |
| `feed_calc_frontend/.env.desktop` | Vite env for desktop — `VITE_API_BASE=http://127.0.0.1:8042/api` |
| `feed_calc_frontend/src-tauri/tauri.conf.json` | Tauri config — externalBin, beforeBuildCommand |
| `feed_calc_frontend/src-tauri/bin/feed_calc_api-x86_64-pc-windows-msvc.exe` | Sidecar binary (overwritten by build script) |

---

## Out of Scope

- CI/CD or GitHub Actions release pipeline
- Cross-platform builds (macOS, Linux)
- Code signing / notarization
- Auto-update (Tauri updater plugin)
- Re-seeding existing user DBs on app update
