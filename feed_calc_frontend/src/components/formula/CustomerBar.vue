<template>
  <el-card class="box-card" style="margin-bottom: 16px;">
    <div class="customer-bar">
      <span class="customer-label">歸屬客戶 / 牧場</span>
      <el-select
        v-model="localCustomerId"
        filterable
        clearable
        placeholder="請選擇客戶"
        class="customer-select"
      >
        <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="openAdd">新增</el-button>
      <el-button :disabled="!selectedCustomerId" @click="openEdit">編輯</el-button>
      <el-button type="danger" plain :disabled="!selectedCustomerId" @click="handleDelete">刪除</el-button>
    </div>
  </el-card>

  <CustomerManageDialog
    v-model="dialogVisible"
    :mode="dialogMode"
    :customer="editingCustomer"
    @saved="onSaved"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../stores/useFormulaStore'
import request from '@/api/request'
import CustomerManageDialog from './CustomerManageDialog.vue'

const formulaStore = useFormulaStore()
const { selectedCustomerId, customerList } = storeToRefs(formulaStore)
const { fetchCustomerList, setCustomer, clearCustomer } = formulaStore

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingCustomer = ref(null)

onMounted(() => fetchCustomerList())

const localCustomerId = computed({
  get: () => selectedCustomerId.value,
  set: (val) => {
    if (!val) {
      clearCustomer()
    } else {
      const c = customerList.value.find(c => c.id === val)
      if (c) setCustomer(c.id, c.name)
    }
  }
})

const openAdd = () => {
  dialogMode.value = 'create'
  editingCustomer.value = null
  dialogVisible.value = true
}

const openEdit = () => {
  editingCustomer.value = customerList.value.find(c => c.id === selectedCustomerId.value) || null
  dialogMode.value = 'edit'
  dialogVisible.value = true
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('確定要刪除此客戶嗎？', '刪除確認', {
      confirmButtonText: '刪除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.delete(`auth/customers/${selectedCustomerId.value}/`)
    clearCustomer()
    await fetchCustomerList(true)
    ElMessage.success('客戶已刪除')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('刪除失敗')
  }
}

const onSaved = async () => {
  await fetchCustomerList(true)
}
</script>

<style scoped>
.customer-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}
.customer-label {
  white-space: nowrap;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
}
.customer-select {
  flex: 1;
}
</style>
