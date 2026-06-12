<template>
  <el-dialog
    v-model="visible"
    title="儲存配方"
    width="500px"
    @open="handleOpen"
  >
    <el-form :model="form" label-position="top">
      <el-form-item label="歸屬客戶 / 牧場">
        <div class="customer-display" :class="{ 'no-customer': !selectedCustomerId }">
          <el-icon><OfficeBuilding /></el-icon>
          <span>{{ selectedCustomerName || '尚未選擇客戶（請在計算機頁面選擇）' }}</span>
        </div>
      </el-form-item>

      <el-form-item label="配方名稱">
        <el-input v-model="form.name" placeholder="例如：Swine_Nursery_12-06-2026" />
      </el-form-item>

      <el-form-item label="備註">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-tooltip
        :disabled="!!selectedCustomerId"
        content="請先在計算機頁面選擇客戶"
        placement="top"
      >
        <span>
          <el-button
            type="primary"
            @click="submitSave"
            :loading="saving"
            :disabled="!form.name || !selectedCustomerId"
          >
            確認儲存
          </el-button>
        </span>
      </el-tooltip>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { OfficeBuilding } from '@element-plus/icons-vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../../stores/useFormulaStore'

const props = defineProps(['modelValue', 'formData'])
const emit = defineEmits(['update:modelValue', 'update:formData', 'saved'])

const formulaStore = useFormulaStore()
const { formulaItems, targetStandardId, selectedCustomerId, selectedCustomerName, autoFormulaName } = storeToRefs(formulaStore)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = computed({
  get: () => props.formData,
  set: (val) => emit('update:formData', val)
})

const saving = ref(false)

const handleOpen = () => {
  if (!props.formData.name && autoFormulaName.value) {
    emit('update:formData', { ...props.formData, name: autoFormulaName.value })
  }
}

const submitSave = async () => {
  if (!form.value.name || !selectedCustomerId.value) return
  saving.value = true
  try {
    const payload = {
      name: form.value.name,
      customer_id: selectedCustomerId.value,
      description: form.value.description,
      standard_id: targetStandardId.value,
      items: formulaItems.value.map(i => ({ ingredient: i.id, amount_kg: i.amount }))
    }
    await request.post('formulas/', payload)
    ElMessage.success('儲存成功')
    visible.value = false
    emit('saved')
  } catch (e) {
    ElMessage.error('儲存失敗')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.customer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--border-radius-input);
  background: #f8fafc;
  border: 1px solid var(--border-color);
  color: var(--text-main);
  font-size: var(--el-font-size-base);
  width: 100%;
  box-sizing: border-box;
}
.customer-display.no-customer {
  color: var(--text-placeholder);
}
</style>
