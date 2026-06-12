# Desktop Packaging Pitfalls & Solutions

Reference document for the Tauri + Django sidecar build pipeline.
Run `.\scripts\build-desktop.ps1` (or `.\scripts\build-desktop.ps1 -SkipSeed`) to produce installers.

---

## Bug 1: `ModuleNotFoundError: No module named 'djoser.urls'`

**Symptom:** All API calls return HTTP 500 after install. Django crashes on startup.

**Root cause:** PyInstaller cannot statically trace string-based Django URL includes (`include('djoser.urls')`). Django's `AppRegistryNotReady` prevents `collect_submodules('djoser.urls')` from working either.

**Fix:** Guard the djoser URL includes behind `sys.frozen` in `accounts/urls.py`:
```python
if not getattr(sys, 'frozen', False):
    urlpatterns += [
        path('', include('djoser.urls')),
        path('', include('djoser.urls.authtoken')),
    ]
```
The desktop app uses `StandaloneBypassAuth` and never needs these endpoints.

---

## Bug 2: CORS blocked — `x-client-mode` header not allowed

**Symptom:** All API calls blocked with CORS preflight error after fixing Bug 1.

**Root cause:** `request.js` sends a custom `X-Client-Mode: desktop` header. Django's default CORS allowed-headers list does not include it.

**Fix:** Add it to `config/settings/desktop.py`:
```python
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ['x-client-mode']
```

---

## Bug 3: `ERR_CONNECTION_REFUSED` on all API calls at startup

**Symptom:** The window opens and all API calls fail immediately with connection refused.

**Root cause:** Race condition — the Tauri window (and Vue's `onMounted` API calls) loads before the Django sidecar has finished starting (settings init → migrations → `waitress.serve()`). This takes 5–15 seconds on first run with a fresh database.

**Fix:** Vue-side loading screen in `App.vue` that polls the API every second and blocks rendering until Django responds:
```javascript
// App.vue — polls /api/ingredients/?page_size=1 every 1 second
// Shows a spinner ("正在啟動服務...") until the backend is ready
```
- Do NOT use `visible: false` + Rust TCP/HTTP polling — the sidecar startup sequence is too variable for reliable Rust-side gating.
- The store fetch functions also have 3-retry logic (2-second gap) as a safety net.

---

## Bug 4: `TypeError: Assignment to constant variable` in FormulaCalculator

**Symptom:** Crash when loading a saved formula via the "載入舊配方" dialog.

**Root cause:** `saveForm` is declared as `const saveForm = reactive({...})`. The `@loaded` handler tried to reassign it: `saveForm = { ...saveForm, ...data }`.

**Fix:** Use `Object.assign` to mutate the reactive object in place:
```javascript
@loaded="(data) => { Object.assign(saveForm, data) }"
```

---

## Startup Log

Django writes diagnostics to `%APPDATA%\FeedCalc\startup.log` on every launch.
A healthy startup ends with:
```
[run_api] wsgi application ready
[run_api] __main__ block entered
[run_api] running migrations...
[run_api] migrations done
[run_api] calling serve() on port 8042
```
If any line is missing, check the entries before it for the failure point.

---

## Build Script Flags

| Command | When to use |
|---|---|
| `.\scripts\build-desktop.ps1` | Full build — seeds DB, runs PyInstaller, builds Tauri |
| `.\scripts\build-desktop.ps1 -SkipSeed` | Frontend/Rust changes only — skips DB seed, still reruns PyInstaller if Python changed |

PyInstaller uses cached output if no Python files changed, so `-SkipSeed` is fast when only Rust/Vue changed.
