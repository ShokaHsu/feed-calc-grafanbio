<template>
  <el-card class="box-card" style="margin-bottom: 20px;">
    <template #header>
      <div class="card-header"><span>步驟 1: 設定目標標準</span></div>
    </template>
    
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8" :md="6">
        <div class="input-label">1. 物種</div>
        <el-select 
          v-model="selectedSpecies" 
          placeholder="選擇物種" 
          @change="setSpecies" 
          style="width: 100%"
        >
          <el-option label="豬 (Swine)" value="SWINE" />
          <el-option label="雞 (Poultry)" value="POULTRY" />
          <el-option label="反芻 (Ruminant)" value="RUMINANT" />
          <el-option label="水產 (Aqua)" value="AQUA" />
          <el-option label="其他" value="OTHER" />
        </el-select>
      </el-col>

      <el-col :xs="24" :sm="8" :md="6">
        <div class="input-label">2. 生長階段</div>
        <el-select 
          v-model="selectedStage" 
          placeholder="選擇階段" 
          :disabled="!selectedSpecies" 
          @change="setStage" 
          style="width: 100%"
        >
          <el-option 
            v-for="stage in availableStages" 
            :key="stage.value" 
            :label="stage.label" 
            :value="stage.value" 
          />
        </el-select>
      </el-col>

      <el-col :xs="24" :sm="8" :md="12">
        <div class="input-label">3. 詳細規格</div>
        <el-select 
          v-model="targetStandardId" 
          :placeholder="placeholderText" 
          style="width: 100%" 
          :disabled="!selectedStage"
        >
          <el-option 
            v-for="std in filteredStandards" 
            :key="std.id" 
            :label="std.name" 
            :value="std.id" 
          />
        </el-select>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../stores/useFormulaStore'

const formulaStore = useFormulaStore()
const {
  selectedSpecies,
  selectedStage,
  targetStandardId,
  availableStages,
  filteredStandards
} = storeToRefs(formulaStore)

const { setSpecies, setStage } = formulaStore

const placeholderText = computed(() => {
    if (!selectedSpecies.value) return '3. 請先選擇物種';
    if (!selectedStage.value) return '3. 請選擇階段';
    return '3. 選擇詳細標準';
})
</script>

<style scoped>
.input-label { margin-bottom: 5px; font-weight: bold; font-size: 14px; color: #606266; }
</style>