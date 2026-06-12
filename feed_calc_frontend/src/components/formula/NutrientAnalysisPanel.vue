<template>
  <el-card class="box-card analysis-card">
    <template #header>
      <div class="card-header">
        <span class="title">營養分析 ({{ currentSpeciesLabel }})</span>
        <el-radio-group v-model="displayMode" size="small" @change="handleModeChange">
          <el-radio-button label="basic">基礎模式</el-radio-button>
          <el-radio-button label="advanced">進階模式</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    
    <div class="nutrient-panel">
       <component 
          :is="currentPanelComponent" 
          :data="calculated" 
          :standard="targetStandardData" 
          :mode="displayMode"
       />
    </div>
  </el-card>
</template>

<script setup>
import { computed, markRaw, ref, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../stores/useFormulaStore'
import { usePreferenceStore } from '../../stores/preferences'

// 引入具體的分析面板
import SwinePanel from '../panels/SwinePanel.vue'
import PoultryPanel from '../panels/PoultryPanel.vue'
import GeneralPanel from '../panels/GeneralPanel.vue'

// 1. 連接 Store
const formulaStore = useFormulaStore()
const preferenceStore = usePreferenceStore()

const { 
  selectedSpecies, 
  targetStandardData, 
  calculated 
} = storeToRefs(formulaStore)

const { nutrientDisplayMode } = storeToRefs(preferenceStore)

// 2. 本地狀態
const displayMode = ref('basic')

onMounted(async () => {
  await preferenceStore.fetchFavorites()
  displayMode.value = nutrientDisplayMode.value || 'basic'
})

watch(nutrientDisplayMode, (newMode) => {
  if (newMode) displayMode.value = newMode
})

const handleModeChange = (val) => {
  preferenceStore.saveNutrientMode(val)
}

// 3. 物種顯示文字 (Helper)
const SPECIES_MAP = {
    'SWINE': '豬 (Swine)',
    'POULTRY': '雞 (Poultry)',
    'RUMINANT': '反芻 (Ruminant)',
    'AQUA': '水產 (Aqua)',
    'OTHER': '其他'
}

const currentSpeciesLabel = computed(() => {
    return SPECIES_MAP[selectedSpecies.value] || '通用模式'
})

// 4. 決定要顯示哪個面板
const currentPanelComponent = computed(() => {
    const sp = selectedSpecies.value
    if (sp === 'SWINE') return markRaw(SwinePanel)
    if (sp === 'POULTRY') return markRaw(PoultryPanel)
    return markRaw(GeneralPanel)
})
</script>

<style scoped>
.analysis-card {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 700;
}

:deep(.el-radio-button__inner) {
  padding: 8px 16px;
  font-size: 13px;
}
</style>
