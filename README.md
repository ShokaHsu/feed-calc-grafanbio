# 飼料配方計算系統 — Feed Formula Calculator

A full-stack livestock feed formulation tool for swine and poultry nutritionists.  
Compose feed formulas from an ingredient database, compare calculated nutrients against NRC standards, save formulas per customer/farm, and export reports.

---

## Versions

| Version | Platform | Backend | Auth |
|---|---|---|---|
| **Desktop** | Tauri v2 (Windows / macOS) | Local Django on `localhost:8000` | No login — auto local admin |
| **Cloud** | Browser via Vercel | Django on Railway (PostgreSQL) | Email + password |
| **Mobile** | Capacitor (iOS / Android) — _planned_ | Django on Railway (PostgreSQL) | Email + password |

---

## Features

- **Multi-species** — Swine, Poultry, Ruminant, Aquaculture
- **Real-time nutrient calculation** — CP, CF, Fat, DE / ME / NE (pig), AMEn (broiler), SID amino acids (Lys, Met, M+C, Thr, Trp, Val, Ile, Leu, Arg, His), Ca / P / avail-P / Na
- **NRC standard comparison** — progress bars show calculated vs. target for each nutrient
- **Ingredient database** — paginated table with search, category filter, favorites, and inline add/edit
- **Formula management** — save, load, and delete named formulas linked to a customer/farm
- **Export** — CSV download (UTF-8 BOM for Excel) and browser print-to-PDF report
- **Customer/farm management** — manage farm records and link to formulas
- **User preferences** — persistent favorite ingredients per user account
- **Membership tiers** — Free / Silver / Enterprise with ingredient limits and org sharing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + Composition API |
| State | Pinia |
| UI | Element Plus |
| HTTP | Axios (single `request.js` instance with auth interceptor) |
| Build | Vite |
| Desktop wrapper | Tauri v2 (Rust) |
| Backend | Django 5 + Django REST Framework |
| Auth | DRF Token Auth · Djoser · django-allauth |
| Database | SQLite (dev / desktop) · PostgreSQL (cloud via Railway) |
| CORS | django-cors-headers |
| Static files | WhiteNoise (cloud) |
| PDF | WeasyPrint · ReportLab |

---

## Project Structure

```
feed_calc_project/
├── feed_calc_frontend/
│   ├── src/
│   │   ├── api/request.js            # Axios instance — auth interceptor for all three platforms
│   │   ├── components/
│   │   │   ├── formula/              # FormulaTable, IngredientPicker, Save/Load dialogs
│   │   │   ├── panels/               # SwinePanel, PoultryPanel, GeneralPanel, NutrientRow
│   │   │   ├── FormulaCalculator.vue # Main calculator page
│   │   │   ├── FormulaExporter.vue   # CSV + print report
│   │   │   ├── IngredientList.vue    # Ingredient database management
│   │   │   └── StandardList.vue      # NRC standards management
│   │   ├── stores/
│   │   │   ├── useFormulaStore.js    # Formula state + nutrient calculation engine
│   │   │   ├── user.js               # Auth token persistence
│   │   │   └── preferences.js        # Favorite ingredients (synced to backend)
│   │   ├── utils/env.js              # Platform detection: isDesktopApp / isMobileApp / getPlatform
│   │   ├── views/                    # Dashboard, Login, Register
│   │   └── router/index.js
│   ├── src-tauri/                    # Tauri Rust shell
│   ├── .env                          # Dev: local backend URL
│   ├── .env.production               # Cloud build: Railway backend URL
│   ├── .env.desktop                  # Desktop build: localhost URL
│   ├── .env.mobile                   # Mobile build: Railway backend URL
│   ├── vercel.json                   # SPA rewrite rule for Vue Router
│   └── package.json
│
└── feed_calc_backend/
    ├── accounts/                     # User, Organization, Customer, UserPreference
    ├── ingredients/                  # Ingredient model + CRUD
    ├── standards/                    # NutrientRequirement (NRC data)
    ├── formulas/                     # Formula + FormulaItem — save/load
    ├── common/                       # TimeStampedModel base class
    ├── config/
    │   ├── settings/
    │   │   ├── base.py               # Shared settings
    │   │   ├── dev.py                # Local development (SQLite, CORS localhost)
    │   │   ├── prod.py               # Railway deployment (PostgreSQL, WhiteNoise, HTTPS)
    │   │   └── desktop.py            # Tauri desktop (SQLite, standalone bypass auth)
    │   ├── urls.py
    │   └── wsgi.py
    ├── Procfile                      # Railway process definition
    ├── railway.toml                  # Railway build/deploy config
    └── requirements.txt
```

---

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Rust toolchain — only for Tauri desktop ([rustup.rs](https://rustup.rs))

### Backend

```bash
cd feed_calc_backend

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt

python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
python manage.py runserver --settings=config.settings.dev
```

API available at `http://127.0.0.1:8000/api/`

### Frontend (Web mode)

```bash
cd feed_calc_frontend
npm install
npm run dev          # http://localhost:5173
```

### Frontend (Desktop — Tauri)

```bash
npm run tauri dev
```

Desktop mode auto-bypasses login and connects to the local backend as a standalone admin.

---

## Environment Variables

### Frontend env files

| File | Used by | `VITE_API_BASE` |
|---|---|---|
| `.env` | `npm run dev` | `http://127.0.0.1:8000/api` |
| `.env.production` | `npm run build` → Vercel | `https://your-app.up.railway.app/api` |
| `.env.desktop` | `npm run build:desktop` → Tauri | `http://127.0.0.1:8000/api` |
| `.env.mobile` | `npm run build:mobile` → Capacitor | `https://your-app.up.railway.app/api` |

### Backend env file — `feed_calc_backend/.env`

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

---

## Build Scripts

```bash
# Cloud / Vercel  (base: '/')
npm run build

# Desktop / Tauri  (base: './')
npm run build:desktop

# Mobile / Capacitor  (base: './')
npm run build:mobile
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login/` | Login — returns DRF token |
| POST | `/api/auth/register/` | Register new user |
| GET | `/api/auth/users/me/` | Current user profile |
| GET · POST | `/api/auth/customers/` | List / create customer farms |
| GET · POST | `/api/user/preferences` | Get / save favorite ingredient IDs |
| GET · POST | `/api/ingredients/` | List / create ingredients |
| PATCH · DELETE | `/api/ingredients/<id>/` | Update / delete ingredient |
| POST | `/api/ingredients/bulk-delete/` | Batch delete by ID list |
| GET | `/api/standards/requirements/` | NRC nutrient standards |
| GET · POST | `/api/formulas/` | List / save formulas |
| GET · PUT · DELETE | `/api/formulas/<id>/` | Formula detail / update / delete |

**Auth header:** `Authorization: Token <your-token>`

---

## Authentication Modes

| Platform | Mechanism |
|---|---|
| **Cloud / Mobile** | Email + password → `/api/auth/login/` returns a token, stored in `localStorage`. `request.js` attaches `Authorization: Token <key>` on every request. |
| **Desktop (Tauri)** | `request.js` sends `Authorization: Bearer standalone-admin`. Backend (`DesktopStandaloneAuthentication`) auto-creates a local superuser and returns it — no password required. |

---

## Deployment

### Backend → Railway

1. Create a new project in [Railway](https://railway.app), connect your repo
2. Set the **root directory** to `feed_calc_backend/`
3. Add a **PostgreSQL** plugin — Railway injects `DATABASE_URL` automatically
4. Set environment variables:

   | Variable | Value |
   |---|---|
   | `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
   | `SECRET_KEY` | a long random string |
   | `ALLOWED_HOSTS` | `your-app.up.railway.app` |
   | `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` |

5. Railway uses `railway.toml` to run: migrate → collectstatic → gunicorn

### Frontend → Vercel

1. Create a new project in [Vercel](https://vercel.com), connect your repo
2. Set the **root directory** to `feed_calc_frontend/`
3. Build command: `npm run build` · Output directory: `dist`
4. Set environment variable:

   | Variable | Value |
   |---|---|
   | `VITE_API_BASE` | `https://your-app.up.railway.app/api` |

5. `vercel.json` handles SPA routing (all paths → `index.html`)

> After both are live, update `CORS_ALLOWED_ORIGINS` in Railway with your Vercel URL, and `CSRF_TRUSTED_ORIGINS` in `prod.py` if needed.

---

## Admin Panel

`http://127.0.0.1:8000/admin/` (dev) or `https://your-app.up.railway.app/admin/` (prod)

Use it to manage ingredients, NRC standards, users, organizations, and formulas directly.

---

## Running Tests

```bash
cd feed_calc_backend
pytest
```
