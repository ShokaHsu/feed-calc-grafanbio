<template>
  <div class="formula-table-container">
    <el-table 
      :data="formulaItems" 
      style="width: 100%" 
      class="custom-table"
    >
      <el-table-column prop="name" label="原料名稱" min-width="120" />
      
      <el-table-column label="使用量 (kg)" width="140" align="right">
        <template #default="scope">
          <div class="amount-input-wrapper">
            <el-input 
              v-model.number="scope.row.amount" 
              type="number"
              class="inline-amount-input no-print-input"
              @input="recalculate"
            />
            <span class="only-print">{{ scope.row.amount }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="%" width="80" align="right">
         <template #default="scope">
            <span class="percentage-text">
              {{ totalWeight > 0 ? ((scope.row.amount / totalWeight) * 100).toFixed(1) : 0 }}%
            </span>
         </template>
      </el-table-column>
      
      <el-table-column width="60" align="center" class-name="no-print">
        <template #default="scope">
            <el-button 
              type="danger" 
              link 
              class="delete-btn"
              @click="removeIngredient(scope.$index)"
            >
                <el-icon><Delete /></el-icon>
            </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 總計行 -->
    <div class="total-row">
      <div class="total-label">合計</div>
      <div class="total-values">
        <span class="total-weight">{{ (totalWeight || 0).toFixed(1) }} kg</span>
        <span class="total-percent">100.0%</span>
      </div>
    </div>

    <!-- 成本摘要條 (Cost Summary Strip) -->
    <div class="cost-summary-strip">
      <div class="cost-item">
        <span class="cost-label">飼料總成本</span>
        <span class="cost-value">NT$ {{ (totalCost || 0).toLocaleString(undefined, {maximumFractionDigits: 0}) }}</span>
      </div>
      <div class="cost-divider"></div>
      <div class="cost-item">
        <span class="cost-label">每公斤單價</span>
        <span class="cost-value highlight">NT$ {{ (totalWeight > 0 ? totalCost/totalWeight : 0).toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Delete } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../stores/useFormulaStore'

const formulaStore = useFormulaStore()
const { formulaItems, totalWeight, totalCost } = storeToRefs(formulaStore)
const { removeIngredient, recalculate } = formulaStore
</script>

<style scoped>
.formula-table-container {
  margin-top: 8px;
}

:deep(.custom-table) {
  --el-table-header-text-color: var(--text-placeholder);
  --el-table-header-bg-color: transparent;
}

:deep(.custom-table th) {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  border-bottom: 2px solid #f1f5f9 !important;
}

:deep(.custom-table tr:hover > td) {
  background-color: #f8fafc !important;
}

.amount-input-wrapper {
  display: flex;
  justify-content: flex-end;
}

:deep(.inline-amount-input .el-input__wrapper) {
  box-shadow: none !important;
  background-color: #f8fafc !important;
  padding: 0 12px !important;
  width: 90px;
}

:deep(.inline-amount-input .el-input__inner) {
  text-align: right;
  font-weight: 700;
  color: var(--text-main);
}

.percentage-text {
  color: var(--text-secondary);
  font-weight: 500;
}

.delete-btn {
  color: #cbd5e1;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.delete-btn:hover {
  color: #ef4444;
  background-color: #fef2f2;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 16px 24px;
  border-top: 2px solid #e2e8f0;
  font-weight: 700;
  color: var(--text-main);
  background-color: #fff;
}

.total-values {
  display: flex;
  gap: 40px;
}

.total-weight {
  min-width: 80px;
  text-align: right;
}

.total-percent {
  min-width: 60px;
  text-align: right;
}

.cost-summary-strip {
  margin-top: 24px;
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.cost-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cost-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.cost-value {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
}

.cost-value.highlight {
  color: #2563eb;
}

.cost-divider {
  width: 1px;
  height: 32px;
  background-color: #e2e8f0;
}

@media print {
  .no-print-input { display: none !important; }
  .only-print { display: inline-block !important; }
}
@media screen {
  .only-print { display: none !important; }
}
</style>
