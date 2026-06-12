# Calculator UX Improvements — Design Spec
**Date:** 2026-06-12  
**Scope:** Feed Formula Calculator desktop app — 5 UX improvements to the FormulaCalculator flow

---

## 1. Overview

Five targeted improvements to the FormulaCalculator and supporting components:

1. Customer bar above Step 1 with Add / Edit / Delete management
2. Auto-populated formula name (`Species_Stage_DD-MM-YYYY`)
3. Rename Step 1 label 2 from "生長階段" → "畜禽階段"
4. Rename Step 1 label 3 from "詳細規格" → "飼養標準"
5. Silent auto-fill of common ingredients when Step 1 is complete and formula is empty

---

## 2. Customer Bar

### Component
New file: `feed_calc_frontend/src/components/formula/CustomerBar.vue`

### Layout
A card (matching the existing Step 1 card style) placed between the action toolbar and the Step 1 card in `FormulaCalculator.vue`.

```
┌─────────────────────────────────────────────────────────────┐
│ 歸屬客戶/牧場  [  Dropdown (filterable)        ▼ ]  [新增] [編輯] [刪除] │
└─────────────────────────────────────────────────────────────┘
```

- Dropdown is filterable, width: 100% of its flex column
- **新增 (Add):** opens `CustomerManageDialog` in create mode
- **編輯 (Edit):** opens `CustomerManageDialog` in edit mode, pre-filled with selected customer; disabled when no customer selected
- **刪除 (Delete):** `ElMessageBox.confirm` prompt, then `DELETE auth/customers/:id/`; disabled when no customer selected; clears store selection on success

### State — lifted into `formulaStore`
```js
// new state fields
selectedCustomerId: null,
selectedCustomerName: '',
customerList: [],          // [{id, name, contact_name, phone, address}]
customerListLoaded: false,
```

New actions in `formulaStore`:
- `fetchCustomerList()` — `GET auth/customers/`, sets `customerList` and `customerListLoaded`
- `setCustomer(id, name)` — sets `selectedCustomerId` + `selectedCustomerName`
- `clearCustomer()` — resets both to null / ''

`CustomerBar.vue` calls `fetchCustomerList()` on `onMounted` (only if not already loaded).

### CustomerManageDialog
New file: `feed_calc_frontend/src/components/formula/CustomerManageDialog.vue`

Props: `mode` (`'create'` | `'edit'`), `customer` (object, edit mode only)  
Emits: `saved` (with the customer object returned by the API)

Fields: Name (required), Contact, Phone, Address  
On save:
- Create: `POST auth/customers/` → on success, call `formulaStore.fetchCustomerList()` + `setCustomer(newId, newName)`
- Edit: `PATCH auth/customers/:id/` → on success, refresh list, update store name if the edited customer is selected

### SaveFormulaDialog changes
- Remove the inline customer `el-select` and the nested new-customer `el-dialog`
- Replace with a read-only display: `歸屬客戶: {{ selectedCustomerName || '未選擇' }}`
- The save payload continues to use `form.value.customer` → now sourced from `formulaStore.selectedCustomerId`
- If `selectedCustomerId` is null, the Save button is disabled with tooltip "請先在計算機頁面選擇客戶"

---

## 3. Auto-populated Formula Name

### Computed in `formulaStore`
```js
autoFormulaName: computed(() => {
  const speciesMap = { SWINE:'Swine', POULTRY:'Poultry', RUMINANT:'Ruminant', AQUA:'Aqua', OTHER:'Other' }
  const sp = speciesMap[selectedSpecies.value] || ''
  const st = selectedStage.value || ''
  const today = new Date()
  const dd = String(today.getDate()).padStart(2,'0')
  const mm = String(today.getMonth()+1).padStart(2,'0')
  const yyyy = today.getFullYear()
  const dateStr = `${dd}-${mm}-${yyyy}`
  return sp && st ? `${sp}_${st}_${dateStr}` : ''
})
```

### SaveFormulaDialog
- On dialog `@open`, if `form.value.name` is empty, set it to `autoFormulaName`
- The name field remains a free-text `el-input` — user can always overwrite

---

## 4. Label Renames in FormulaTargetSelector

File: `feed_calc_frontend/src/components/formula/FormulaTargetSelector.vue`

| Before | After |
|---|---|
| `2. 生長階段` | `2. 畜禽階段` |
| `3. 詳細規格` | `3. 飼養標準` |

Placeholder text on field 3 also updated:
- `'3. 請先選擇物種'` → `'請先選擇物種'`
- `'3. 請選擇階段'` → `'請選擇階段'`
- `'3. 選擇詳細標準'` → `'選擇飼養標準'`

---

## 5. Auto-fill Common Ingredients

### Trigger
A watcher in `FormulaCalculator.vue` (or `formulaStore`) watches `targetStandardId`. When it becomes non-null and `formulaItems.length === 0`, call `autoFillDefaults()`.

### Action: `autoFillDefaults()` in `formulaStore`
Searches `allIngredients` array by partial name match (case-insensitive). Ingredient names are compared with `includes()`.

| Role | Primary pattern | Fallback pattern |
|---|---|---|
| Corn | `玉米` | — |
| Soybean meal | `豆粕` | — |
| Phosphate | `磷酸二鈣` | `磷酸一鈣` |
| Calcium carbonate | `碳酸鈣` | `石灰` |
| Salt | `食鹽` | — |
| Salad oil | `沙拉油` | `植物油` |
| Vitamin premix | `preferenceStore.vitaminPremixId` (by ID) | skip if not configured |
| Mineral premix | `preferenceStore.mineralPremixId` (by ID) | skip if not configured |

For each role, take the **first** ingredient that matches. If no match found (and no fallback), skip silently — no error.

All auto-filled ingredients are added via the existing `addIngredient()` action with `amount = 0`.

The watcher does **not** fire again if `targetStandardId` changes while the formula already has items (i.e., `formulaItems.length > 0`).

### Premix preference config
File: `feed_calc_frontend/src/stores/preferences.js`

Add two new fields:
```js
vitaminPremixId: null,   // ingredient ID
mineralPremixId: null,   // ingredient ID
```

Persisted to backend via the existing `user/preferences` API (add fields to the serializer/model if not present).

A configuration UI — two dropdowns (all ingredients as options) — is added to the `NutrientAnalysisPanel` header area or a dedicated small settings row at the top of `FormulaCalculator`. Label: `預設添加劑設定`. This is collapsed/minimal by default (e.g., a gear icon that expands two dropdowns inline).

---

## 6. Files Changed

| File | Change type |
|---|---|
| `src/components/formula/CustomerBar.vue` | **New** |
| `src/components/formula/CustomerManageDialog.vue` | **New** |
| `src/components/formula/FormulaTargetSelector.vue` | Edit — label renames |
| `src/components/formula/dialogs/SaveFormulaDialog.vue` | Edit — remove customer picker, read from store |
| `src/components/FormulaCalculator.vue` | Edit — add CustomerBar, auto-fill watcher, premix settings row |
| `src/stores/useFormulaStore.js` | Edit — customer state, autoFormulaName, autoFillDefaults, fetchCustomerList |
| `src/stores/preferences.js` | Edit — vitaminPremixId, mineralPremixId |

Backend — **requires model changes** (`UserPreference` uses explicit fields, not freeform JSON):
- Add `vitamin_premix_id = models.IntegerField(null=True, blank=True)` to `UserPreference`
- Add `mineral_premix_id = models.IntegerField(null=True, blank=True)` to `UserPreference`
- Add migration
- Add `vitamin_premix_id` and `mineral_premix_id` to `UserPreferenceSerializer` fields
- The preferences view (`GET/POST /api/user/preferences`) already handles upsert — no view changes needed

---

## 7. Out of Scope

- Customer management page (full CRUD table) — not part of this spec
- Auto-fill amounts (quantities remain 0, user enters them)
- Per-species different default ingredient lists — single shared list for all species
