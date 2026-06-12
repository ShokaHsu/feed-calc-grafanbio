<template>
  <el-dialog 
    v-model="visible" 
    title="儲存配方" 
    width="500px" 
    @open="fetchCustomers"
  >
    <el-form :model="form" label-position="top">
      <el-form-item label="歸屬客戶/牧場 (必填)">
        <div style="display: flex; gap: 10px; align-items: center;">
          <el-select 
            v-model="form.customer" 
            filterable 
            placeholder="請選擇客戶" 
            style="width: 100%" 
            :no-data-text="customerLoadError"
          >
            <el-option v-for="c in allCustomers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-button type="primary" size="small" @click="newCustomerVisible = true">新增</el-button>
        </div>
      </el-form-item>
      
      <el-form-item label="配方名稱">
        <el-input v-model="form.name" placeholder="例如：肉豬生長-夏季配方" />
      </el-form-item>
      
      <el-form-item label="備註">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submitSave" :loading="saving" :disabled="!form.name || !form.customer">
        確認儲存
      </el-button>
    </template>

    <el-dialog v-model="newCustomerVisible" title="建立新客戶" width="400px" append-to-body>
        <el-form :model="newCustomerForm" label-width="80px">
            <el-form-item label="名稱" required><el-input v-model="newCustomerForm.name" /></el-form-item>
            <el-form-item label="聯絡人"><el-input v-model="newCustomerForm.contact_name" /></el-form-item>
            <el-form-item label="電話"><el-input v-model="newCustomerForm.phone" /></el-form-item>
            <el-form-item label="地址"><el-input v-model="newCustomerForm.address" /></el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="newCustomerVisible = false">取消</el-button>
            <el-button type="success" @click="createCustomer" :loading="creatingCustomer">建立</el-button>
        </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../../stores/useFormulaStore'

// Props: 接收表單資料 (雙向綁定)
const props = defineProps(['modelValue', 'formData']) 
const emit = defineEmits(['update:modelValue', 'update:formData', 'saved'])

const formulaStore = useFormulaStore()
const { formulaItems, targetStandardId } = storeToRefs(formulaStore)

// Local State
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = computed({
    get: () => props.formData,
    set: (val) => emit('update:formData', val)
})

const allCustomers = ref([])
const customerLoadError = ref('載入中...')
const saving = ref(false)

// New Customer State
const newCustomerVisible = ref(false)
const creatingCustomer = ref(false)
const newCustomerForm = reactive({ name: '', contact_name: '', phone: '', address: '', species: 'OTHER', scale: 'SMALL' })

// Methods
const fetchCustomers = async () => {
    try {
        const res = await request.get('auth/customers/')
        allCustomers.value = res.data.results || res.data
        if (allCustomers.value.length === 0) customerLoadError.value = '無客戶資料'
    } catch (e) { customerLoadError.value = '載入失敗' }
}

const submitSave = async () => {
    if (!form.value.name || !form.value.customer) return;
    saving.value = true
    try {
        const payload = { 
            name: form.value.name, 
            customer_id: form.value.customer, 
            description: form.value.description, 
            standard_id: targetStandardId.value, 
            items: formulaItems.value.map(i => ({ ingredient: i.id, amount_kg: i.amount })) 
        }
        await request.post('formulas/', payload)
        ElMessage.success('儲存成功'); 
        visible.value = false;
        emit('saved')
    } catch (e) { ElMessage.error('儲存失敗') } finally { saving.value = false }
}

const createCustomer = async () => {
    if (!newCustomerForm.name) return
    creatingCustomer.value = true
    try {
        const res = await request.post('auth/customers/', newCustomerForm)
        await fetchCustomers(); 
        form.value.customer = res.data.id; // 自動選取新建的客戶
        newCustomerVisible.value = false;
        ElMessage.success('客戶建立成功')
    } catch (e) { ElMessage.error('建立失敗') } finally { creatingCustomer.value = false }
}
</script>