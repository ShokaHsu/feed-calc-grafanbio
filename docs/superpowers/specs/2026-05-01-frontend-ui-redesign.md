# Frontend UI Redesign — FeedCalc

**Date:** 2026-05-01  
**Revised:** 2026-05-04  
**Branch:** refactor/intro-pinia  
**Scope:** Visual polish + Nutrient panel redesign (Approach A — incremental enhancement)

---

## Goals

Make the app look modern and professional without changing behavior or workflow. Primary motivation is aesthetics — not navigation restructure or workflow changes. Target users are 40+ years old, so large font sizes and touch targets are preserved as a feature.

---

## 1. Visual Theme (Clean Light)

Replace the current Element Plus default overrides in `main-layout.css` with a refined Clean Light token set.

**Updated CSS variables:**

| Token | Old | New |
|---|---|---|
| `--brand-color` | `#409EFF` | `#2563eb` |
| `--bg-body` | `#f5f7fa` | `#f1f5f9` |
| `--bg-card` | `#ffffff` | `#ffffff` |
| `--border-color` | `#dcdfe6` | `#e2e8f0` |
| `--border-radius` | `8px` | `12px` (cards), `8px` (inputs) |
| `--shadow-card` | `0 4px 12px rgba(0,0,0,0.05)` | `0 1px 4px rgba(0,0,0,0.06)` |
| `--text-main` | `#303133` | `#1e293b` |
| `--text-secondary` | `#606266` | `#64748b` |
| `--text-placeholder` | `#909399` | `#94a3b8` |

**Font sizes stay unchanged** — 16pt base, 50px input height. These are intentional for 40+ target users.

**Component restyling (Element Plus overrides):**
- Cards: `border-radius: 12px`, remove card header background tint, use `border-bottom: 1px solid #f1f5f9` as divider
- Inputs/Selects: `border-color: #e2e8f0`, `background: #f8fafc` (unfocused), `border-color: #93c5fd` (focused)
- Buttons: primary uses `#2563eb`, hover `#1d4ed8`, `border-radius: 8px`
- Tables: zebra stripe via `#f8fafc` on alternate rows, header `background: #f8fafc`, `color: #94a3b8` uppercase labels
- Progress bars: `height: 6px`, `border-radius: 4px`, background `#f1f5f9`

---

## 2. Top Navigation Bar

Keep the existing tab-based navigation. Restyle only.

**Changes to `Dashboard.vue`:**
- Height: `54px` (from `60px`)
- Add brand wordmark: `Feed` + `Calc` (blue accent on "Calc")
- Active tab: `border-bottom: 2px solid #2563eb`, `color: #2563eb`, `font-weight: 600`
- Inactive tab: `color: #64748b`, hover `color: #334155`
- Box shadow: `0 1px 3px rgba(0,0,0,0.04)` (subtle lift)
- No background color change (stays white)

---

## 3. Formula Calculator Layout

**File:** `FormulaCalculator.vue`

### Desktop (≥ 900px)
Keep existing `<el-row>/<el-col>` structure. Adjust column ratios to `:lg="14"` / `:lg="10"` (approximates 1.3fr 1fr). No CSS Grid migration — keeps consistency with the rest of the app.
- Left: ingredient table card
- Right: nutrient analysis card
- Gap: `16px`

### Mobile (< 900px)
Single column stacked:
- Top: ingredient table
- Bottom: nutrient analysis (collapsed to card grid of key nutrients)

### Target Selector Bar (`FormulaTargetSelector.vue`)
Restyled as a horizontal pill bar above the two panels:
- White card, `border-radius: 12px`, subtle shadow
- Species → Stage → Standard shown as `selector-chip` elements with `›` dividers
- Selected chips: `background: #eff6ff`, `border-color: #93c5fd`, `color: #1d4ed8`

### Formula Table Card (`FormulaTable.vue`)
- Table header: uppercase labels, `color: #94a3b8`, `font-size: 13px`
- Row hover: `background: #f8fafc`
- Amount inputs: inline styled inputs (`width: 80px`, right-aligned)
- Delete button: `color: #cbd5e1` → hover `color: #ef4444`, `background: #fef2f2`
- Total row: `font-weight: 700`, `border-top: 2px solid #e2e8f0`
- **Cost summary strip** added below table: two cells showing 飼料成本 and 每公斤單價

---

## 4. Nutrient Analysis Panel Redesign

Affects `NutrientAnalysisPanel.vue`, `SwinePanel.vue`, `PoultryPanel.vue`, `GeneralPanel.vue`, `NutrientRow.vue`, `NutrientGroup.vue` (already exists), `preferences.js`, and a new composable `useGroupStatus.js`.

### 4a. Basic / Advanced Mode Toggle

A segmented control at the top of `NutrientAnalysisPanel.vue`:

```
[ 基礎模式 ]  [ 進階模式 ]
```

- `NutrientAnalysisPanel.vue` reads `nutrientDisplayMode` from `usePreferenceStore` and passes it as a `mode` prop to whichever panel is active (Swine / Poultry / General)
- State stored in `preferences` Pinia store as `nutrientDisplayMode: 'basic' | 'advanced'`
- Default: `'basic'`
- Persisted via `POST /user/preferences` with `{ favorites: [...], nutrient_display_mode: mode }` — same upsert endpoint already used for favorites (see Section 6)

### 4b. Nutrient Groups

Nutrients are reorganized into four named groups inside each panel. Each group wraps its rows in `<NutrientGroup>`.

| Group | Colour | Nutrients included |
|---|---|---|
| 能量與概略養分 | `#2563eb` (blue) | CP, CF, EE, Ash — plus species energy: Swine (DE `de_pig`, ME `me_pig`, NE `ne_pig_g`), Poultry (AMEn `amen_broiler`), General (ME) |
| 胺基酸 | `#7c3aed` (purple) | Total AA (Lys, Met, M+C, Thr, Trp) + SID AA in advanced mode |
| 礦物質 | `#d97706` (amber) | Ca, P, aP, Na, Cl, K, Mg |
| 維生素 | `#16a34a` (green) | Vit A, D, E, K, B1, B2, B3, B5, B6, B12, Choline, Folic, Biotin |

Vitamins are species-agnostic — the same group appears in all three panels. No standard targets exist for vitamins, so all vitamin rows use the no-target display path (static bar, excluded from badge computation).

**In Basic mode:**
- 能量與概略養分: always expanded
- 胺基酸: expanded (Total AA only — SID rows hidden)
- 礦物質: collapsed — shows header + badge + "進階模式顯示 ›" hint
- 維生素: collapsed — same treatment

**In Advanced mode:**
- All four groups expanded
- SID amino acid rows visible within the 胺基酸 group:
  - Swine: `lys_sid_pig`, `met_sid_pig`, `met_cys_sid_pig`, `thr_sid_pig`, `trp_sid_pig`
  - Poultry: `lys_sid_poultry`, `met_sid_poultry`, `met_cys_sid_poultry`, `thr_sid_poultry`
  - Label prefix: `SID-` (e.g. `SID-離胺酸`)

### 4c. Group Header (`NutrientGroup.vue` — already exists)

No changes to the component. Each panel computes and passes:
- `name`: group display name
- `color`: hex accent
- `status`: `'ok' | 'deficient' | 'excess'` — derived from `useGroupStatus`
- `count`: number of off-target nutrients
- `initialCollapsed`: `mode === 'basic'` for minerals and vitamins groups
- `mode`: passed through for the "進階模式顯示 ›" hint logic

### 4d. Status Badge Composable (`useGroupStatus.js`)

New file: `src/composables/useGroupStatus.js`

```js
// useGroupStatus({ current, target, isMax }[])
// → { status: 'ok' | 'deficient' | 'excess', count: number }
```

Rules:
- Rows with no target are excluded from evaluation
- All targeted rows met → `{ status: 'ok', count: 0 }`
- Any row below min → `{ status: 'deficient', count: N }`
- Any row above max → `{ status: 'excess', count: N }`
- `deficient` takes priority over `excess` if both present

Each panel (Swine, Poultry, General) calls `useGroupStatus` once per group inside a `computed`, then passes the result as props to `<NutrientGroup>`.

For `GeneralPanel`, all groups have no targets → always passes `status: null`, `NutrientGroup` shows no badge (handled by existing `v-if` in the component).

### 4e. NutrientRow restyling

Replaces `<el-progress>` with a custom div-based bar. Adds `accentColor` prop.

- Label: `font-size: 14px`, `color: #64748b`
- Value: `font-size: 14px`, `font-weight: 700`, displayed above the bar
  - OK: `color: #1e293b`
  - Below min: `color: #dc2626` + ` ↓` suffix
  - Above max: `color: #d97706` + ` ↑` suffix
- Bar: `height: 6px`, `border-radius: 4px`, fill color = `accentColor` prop
- No target: `accentColor` defaults to `#cbd5e1`, bar width proportional to a sensible display max
- `accentColor` by group: 能量 `#2563eb`, 胺基酸 `#7c3aed`, 礦物質 `#d97706`, 維生素 `#16a34a`

---

## 5. Ingredient Picker Restyling

`IngredientPicker.vue` — no behavior change, visual only:
- Search input: full-width with search icon prefix
- Category filter: pill-style toggle buttons (single-select) instead of dropdown

---

## 6. Preferences Persistence

**Backend — `UserPreference` model**
Add one new nullable field:
```python
nutrient_display_mode = models.CharField(max_length=10, null=True, blank=True)
```
The existing `POST /user/preferences` endpoint already upserts — extend it to read/write this field alongside `favorites`.

**Frontend — `preferences.js`**
Add `nutrientDisplayMode` ref (`'basic'` default). Add `saveNutrientMode(mode)` action that calls `POST /user/preferences` with both `favorites` and `nutrient_display_mode`. On `fetchFavorites`, also read and set `nutrientDisplayMode` from the response.

---

## 7. Vitamins — Backend Extension

**Django migration**
Add three new optional fields to `Ingredient`:
```python
vitamin_b1_mg_kg  = models.FloatField(null=True, blank=True)
vitamin_b6_mg_kg  = models.FloatField(null=True, blank=True)
biotin_mcg_kg     = models.FloatField(null=True, blank=True)
```
All vitamin fields are nullable — existing ingredient records stay valid without reseeding.

**`IngredientSerializer`**
Add all vitamin fields (including the three new ones) to the serializer so they flow to the frontend when ingredients are loaded.

**`useFormulaStore.js`**
Extend `calculated` with vitamin aggregation fields (e.g. `vit_a`, `vit_d`, `vit_e`, `vit_k`, `vit_b1`, `vit_b2`, `vit_b3`, `vit_b5`, `vit_b6`, `vit_b12`, `choline`, `folic`, `biotin`). Same `+= ing.field * weight_fraction` pattern as all other nutrients.

---

## 8. Responsive Breakpoint

Add a CSS breakpoint at `900px` in `main-layout.css`:

```css
@media (max-width: 900px) {
  .panels { grid-template-columns: 1fr; }
}
```

Mobile nutrient display: key nutrients (ME, CP, Lys) shown as colored stat cards (value + label), full panel hidden behind "查看完整分析" expand.

---

## 9. Files Changed

| File | Change type |
|---|---|
| `src/assets/main-layout.css` | Token update + component overrides + 900px breakpoint |
| `src/views/Dashboard.vue` | Nav bar restyle |
| `src/components/formula/FormulaCalculator.vue` | Column ratio adjustment only |
| `src/components/formula/FormulaTable.vue` | Table + cost strip restyle |
| `src/components/formula/FormulaTargetSelector.vue` | Selector chip restyle |
| `src/components/formula/NutrientAnalysisPanel.vue` | Add mode toggle, pass `mode` prop to panels |
| `src/components/formula/IngredientPicker.vue` | Search + category pill restyle |
| `src/components/panels/SwinePanel.vue` | Wrap sections in NutrientGroup, call useGroupStatus |
| `src/components/panels/PoultryPanel.vue` | Wrap sections in NutrientGroup, call useGroupStatus |
| `src/components/panels/GeneralPanel.vue` | Wrap sections in NutrientGroup, no-target treatment |
| `src/components/panels/NutrientRow.vue` | Replace el-progress with custom bar, add accentColor prop |
| `src/components/panels/NutrientGroup.vue` | **Already exists — no changes needed** |
| `src/stores/preferences.js` | Add nutrientDisplayMode state + saveNutrientMode action |
| `src/composables/useGroupStatus.js` | **New file** — group status badge composable |
| `feed_calc_backend/ingredients/models.py` | Add vitamin_b1, vitamin_b6, biotin fields |
| `feed_calc_backend/ingredients/serializers.py` | Expose new vitamin fields |
| `feed_calc_backend/accounts/models.py` | Add nutrient_display_mode to UserPreference |
| `feed_calc_backend/accounts/serializers.py` | Add nutrient_display_mode to UserPreferenceSerializer |
| `feed_calc_backend/accounts/views.py` | Read/write nutrient_display_mode in preferences endpoint |

---

## 10. Out of Scope

- Login / Register pages
- IngredientList tab
- StandardList tab
- FormulaExporter / print styles
- Adding vitamin target values to NRC standards data
- New features beyond basic/advanced mode toggle
