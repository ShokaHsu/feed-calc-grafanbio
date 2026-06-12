<template>
  <div class="page-container" id="pdf-content">
    
    <div class="toolbar no-print" style="margin-bottom: 20px; display: flex; gap: 10px; justify-content: flex-end;">
      <el-button type="info" @click="loadDialogVisible = true">
        <el-icon style="margin-right: 5px"><FolderOpened /></el-icon> 載入舊配方
      </el-button>
      <el-button type="warning" @click="triggerCsvImport" :loading="importLoading">
        <el-icon style="margin-right: 5px"><Upload /></el-icon> 匯入 CSV
      </el-button>
      <el-button type="success" @click="saveDialogVisible = true" :disabled="formulaItems.length === 0">
        <el-icon style="margin-right: 5px"><Checked /></el-icon> 儲存配方
      </el-button>
      <el-button type="danger" @click="openExportDialog" :disabled="formulaItems.length === 0">
        <el-icon style="margin-right: 5px"><Document /></el-icon> 匯出 / 預覽
      </el-button>
    </div>
    <input ref="csvFileInput" type="file" accept=".csv" style="display:none" @change="handleCsvImport">

    <FormulaTargetSelector />

    <el-row :gutter="20">
      <el-col :xs="24" :lg="14" style="margin-bottom: 20px;">
        <el-card class="box-card">
          <template #header>
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
              <span>步驟 2: 設計配方</span>
              <IngredientPicker :all-ingredients="allIngredients" />
            </div>
          </template>

          <FormulaTable />

        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <NutrientAnalysisPanel />
      </el-col>
    </el-row>

    <LoadFormulaDialog
        v-model="loadDialogVisible"
        @loaded="(data) => { Object.assign(saveForm, data) }"
    />

    <SaveFormulaDialog 
        v-model="saveDialogVisible" 
        v-model:form-data="saveForm" 
    />

    <FormulaExporter 
        v-model="exportDialogVisible" 
        :data="exportData" 
    />

  </div>
</template>

<script setup>
import { ref, computed, reactive, markRaw, onMounted, nextTick } from 'vue'
import { FolderOpened, Checked, Document, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../stores/useFormulaStore'
import request from '../api/request'

// 引入子元件
import FormulaTargetSelector from './formula/FormulaTargetSelector.vue'
import FormulaTable from './formula/FormulaTable.vue'
import IngredientPicker from './formula/IngredientPicker.vue'
import LoadFormulaDialog from './formula/dialogs/LoadFormulaDialog.vue'
import SaveFormulaDialog from './formula/dialogs/SaveFormulaDialog.vue'
import FormulaExporter from './FormulaExporter.vue'
import NutrientAnalysisPanel from './formula/NutrientAnalysisPanel.vue'


// Store 初始化
const formulaStore = useFormulaStore()
const {
    selectedSpecies,
    selectedStage,
    targetStandardData,
    formulaItems,
    calculated,
    totalWeight,
    totalCost,
    allIngredients,
    allStandards,
    targetStandardId,
} = storeToRefs(formulaStore)

const { fetchAllIngredients, fetchStandards, clearFormula, addIngredient, setSpecies, setStage } = formulaStore

// 本地狀態
const saveDialogVisible = ref(false)
const loadDialogVisible = ref(false)
const exportDialogVisible = ref(false)
const saveForm = reactive({ name: '', description: '', customer: null, customerName: '' })
const exportData = ref({ meta: {}, items: [], totals: {}, nutrients: {} })

// 輔助邏輯
const SPECIES_OPTIONS = [
    { label: '豬 (Swine)', value: 'SWINE' }, 
    { label: '雞 (Poultry)', value: 'POULTRY' }, 
    { label: '反芻 (Ruminant)', value: 'RUMINANT' }, 
    { label: '水產 (Aqua)', value: 'AQUA' }, 
    { label: '其他', value: 'OTHER' },
]

const speciesLabel = (val) => {
    const option = SPECIES_OPTIONS.find(o => o.value === val);
    return option ? option.label : val;
}
const selectedSpeciesLabel = computed(() => speciesLabel(selectedSpecies.value))



// 匯出邏輯 (Helper)
const getTargetValue = (std, key, isMax=false) => {
    if(!std) return 0; 
    let dbKey = key; 
    if (key === 'me_pig_kcal_per_kg') dbKey = 'min_me_pig_kcal_per_kg'; 
    if (key === 'lysine_total_g_kg') dbKey = 'min_lysine_total_g_kg';
    const max = `max_${dbKey}`, min = `min_${dbKey}`
    if (isMax && std[max] !== undefined) return std[max]
    if (!isMax && std[min] !== undefined) return std[min]
    if (std[dbKey] !== undefined) return std[dbKey]
    return 0
}

// 匯出資料準備
const nutrientGroups = computed(() => {
    const std = targetStandardData.value || {}; 
    const c = calculated.value
    const sp = selectedSpecies.value
    
    // 基礎與礦物質
    const groups = {
        proximate: [
            { label: '粗蛋白 (CP)', current: c.cp, target: getTargetValue(std, 'crude_protein_percent'), unit: '%', decimals: 2 },
            { label: '粗纖維 (CF)', current: c.cf, target: getTargetValue(std, 'crude_fiber_percent', true), unit: '%', decimals: 2 },
            { label: '粗脂肪 (Fat)', current: c.fat, target: getTargetValue(std, 'crude_fat_percent', true), unit: '%', decimals: 2 },
        ],
        minerals: [
            { label: '鈣 (Ca)', current: c.ca/10, target: getTargetValue(std, 'calcium_g_per_kg')/10, unit: '%', decimals: 2 },
            { label: '總磷 (P)', current: c.p/10, target: getTargetValue(std, 'phosphorus_g_per_kg')/10, unit: '%', decimals: 2 },
            { label: '有效磷 (Avail.P)', current: c.avail_p/10, target: getTargetValue(std, 'available_phosphorus_g_per_kg')/10, unit: '%', decimals: 2 },
            { label: '鈉 (Na)', current: c.na/10, target: getTargetValue(std, 'sodium_g_per_kg')/10, unit: '%', decimals: 2 },
        ]
    }
    // 能量與胺基酸
    if (sp === 'SWINE') {
        groups.energy = [
            { label: '豬消化能 (DE)', current: c.de_pig, target: getTargetValue(std, 'de_pig_kcal_per_kg'), unit: 'kcal', decimals: 0 },
            { label: '豬代謝能 (ME)', current: c.me_pig, target: getTargetValue(std, 'me_pig_kcal_per_kg'), unit: 'kcal', decimals: 0 },
            { label: '肉豬淨能 (NEg)', current: c.ne_pig_g, target: getTargetValue(std, 'ne_pig_growth_kcal_per_kg'), unit: 'kcal', decimals: 0 },
        ];
        groups.amino_acids = [
            { label: 'SID 離氨酸 (Lys)', current: c.lys_sid_pig/10, target: getTargetValue(std, 'lysine_sid_pig_g_kg')/10, unit: '%', decimals: 3 },
            { label: 'SID 蛋氨酸 (Met)', current: c.met_sid_pig/10, target: getTargetValue(std, 'methionine_sid_pig_g_kg')/10, unit: '%', decimals: 3 },
            { label: 'SID 含硫胺基酸 (M+C)', current: c.met_cys_sid_pig/10, target: getTargetValue(std, 'met_cys_sid_pig_g_kg')/10, unit: '%', decimals: 3 },
            { label: 'SID 羥丁胺酸 (Thr)', current: c.thr_sid_pig/10, target: getTargetValue(std, 'threonine_sid_pig_g_kg')/10, unit: '%', decimals: 3 },
            { label: 'SID 色胺酸 (Trp)', current: c.trp_sid_pig/10, target: getTargetValue(std, 'tryptophan_sid_pig_g_kg')/10, unit: '%', decimals: 3 },
        ];
    } else if (sp === 'POULTRY') {
        groups.energy = [
            { label: '肉雞代謝能 (AMEn)', current: c.amen_broiler, target: getTargetValue(std, 'amen_broiler_kcal_per_kg'), unit: 'kcal', decimals: 0 },
        ];
        groups.amino_acids = [
            { label: '總離氨酸 (Lys)', current: c.lys_total/10, target: getTargetValue(std, 'lysine_total_g_kg')/10, unit: '%', decimals: 3 },
            { label: '總蛋氨酸 (Met)', current: c.met_total/10, target: getTargetValue(std, 'methionine_total_g_kg')/10, unit: '%', decimals: 3 },
            { label: '總含硫胺基酸 (M+C)', current: c.met_cys_total/10, target: getTargetValue(std, 'met_cys_total_g_kg')/10, unit: '%', decimals: 3 },
        ];
    } else {
        groups.energy = [{ label: '代謝能 (ME)', current: c.me_pig, target: 0, unit: 'kcal', decimals: 0 }];
        groups.amino_acids = [{ label: '總離氨酸', current: c.lys_total/10, target: 0, unit: '%', decimals: 3 }];
    }
    return { proximate: groups.proximate, energy: groups.energy, amino_acids: groups.amino_acids, minerals: groups.minerals }
})

const openExportDialog = () => {
    if (formulaItems.value.length === 0) { ElMessage.warning("無資料"); return; }
    try {
        const customerName = saveForm.customerName || '未指定客戶';
        const standardName = targetStandardData.value ? targetStandardData.value.name : '未選標準';
        const totalW = totalWeight.value || 1;

        exportData.value = {
            meta: {
                recipeName: saveForm.name || '新配方',
                date: new Date().toISOString().slice(0, 10),
                customerName: customerName,
                species: selectedSpeciesLabel.value || '未選擇',
                stage: selectedStage.value || '未選擇',
                standardName: standardName,
                description: saveForm.description || ''
            },
            items: formulaItems.value.map(i => ({
                id: i.id, name: i.name, amount: i.amount,
                percentage: totalW > 0 ? ((i.amount / totalW) * 100).toFixed(1) : "0.0"
            })),
            totals: {
                weight: totalW.toFixed(1),
                cost: totalCost.value.toFixed(0),
                unitCost: (totalCost.value / totalW).toFixed(2)
            },
            nutrients: JSON.parse(JSON.stringify(nutrientGroups.value))
        }
        exportDialogVisible.value = true;
    } catch (e) { console.error("匯出錯誤:", e); ElMessage.error(`匯出準備失敗`); }
}

// CSV 匯入
const csvFileInput = ref(null)
const importLoading = ref(false)

const triggerCsvImport = () => {
    csvFileInput.value.value = ''
    csvFileInput.value.click()
}

const handleCsvImport = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    importLoading.value = true
    try {
        const res = await request.post('formulas/import-csv/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        const { formula, unmatched } = res.data

        if (formula.standard) {
            const stdId = typeof formula.standard === 'object' ? formula.standard.id : formula.standard
            const std = allStandards.value.find(s => s.id === stdId)
            if (std) {
                setSpecies(std.species)
                setStage(std.stage)
                await nextTick()
                targetStandardId.value = std.id
            }
        }

        clearFormula()
        if (allIngredients.value.length === 0) await fetchAllIngredients()
        const map = new Map(allIngredients.value.map(i => [i.id, i]))

        formula.items.forEach(item => {
            const fullIngredient = map.get(item.ingredient)
            if (fullIngredient) {
                addIngredient(fullIngredient)
                const addedItem = formulaItems.value.find(i => i.id === fullIngredient.id)
                if (addedItem) addedItem.amount = parseFloat(item.amount_kg) || 0
            }
        })

        const customerObj = formula.customer && typeof formula.customer === 'object' ? formula.customer : null
        saveForm.name = formula.name
        saveForm.description = formula.description
        saveForm.customer = customerObj ? customerObj.id : null
        saveForm.customerName = customerObj ? customerObj.name : ''

        if (unmatched.length > 0) {
            ElMessage.warning(`匯入成功，但以下原料未能比對: ${unmatched.join('、')}`)
        } else {
            ElMessage.success('CSV 匯入成功')
        }
    } catch (e) {
        console.error(e)
        const msg = e.response?.data?.error || '匯入失敗，請確認 CSV 格式'
        ElMessage.error(msg)
    } finally {
        importLoading.value = false
    }
}

onMounted(() => {
    fetchAllIngredients();
    fetchStandards();
})
</script>

<style scoped>
.analysis-card { min-height: 500px; }
</style>