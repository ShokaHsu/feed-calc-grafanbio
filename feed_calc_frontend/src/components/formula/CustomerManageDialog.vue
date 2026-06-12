<template>
  <el-dialog v-model="visible" :title="mode === 'create' ? '建立新客戶' : '編輯客戶'" width="420px">
    <el-form :model="form" label-position="top">
      <el-form-item label="名稱" required>
        <el-input v-model="form.name" placeholder="客戶 / 牧場名稱" />
      </el-form-item>
      <el-form-item label="聯絡人">
        <el-input v-model="form.contact_name" />
      </el-form-item>
      <el-form-item label="電話">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.address" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit" :loading="submitting" :disabled="!form.name">
        {{ mode === 'create' ? '建立' : '儲存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useFormulaStore } from '../../stores/useFormulaStore'
import request from '@/api/request'

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, default: 'create' },
  customer: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formulaStore = useFormulaStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const form = reactive({ name: '', contact_name: '', phone: '', address: '' })
const submitting = ref(false)

watch(() => props.modelValue, (open) => {
  if (!open) return
  if (props.mode === 'edit' && props.customer) {
    Object.assign(form, {
      name: props.customer.name || '',
      contact_name: props.customer.contact_name || '',
      phone: props.customer.phone || '',
      address: props.customer.address || ''
    })
  } else {
    Object.assign(form, { name: '', contact_name: '', phone: '', address: '' })
  }
})

const submit = async () => {
  if (!form.name) return
  submitting.value = true
  try {
    let res
    if (props.mode === 'create') {
      res = await request.post('auth/customers/', form)
      formulaStore.setCustomer(res.data.id, res.data.name)
    } else {
      res = await request.patch(`auth/customers/${props.customer.id}/`, form)
      if (formulaStore.selectedCustomerId === res.data.id) {
        formulaStore.setCustomer(res.data.id, res.data.name)
      }
    }
    ElMessage.success(props.mode === 'create' ? '客戶建立成功' : '客戶更新成功')
    visible.value = false
    emit('saved', res.data)
  } catch (e) {
    ElMessage.error('操作失敗')
  } finally {
    submitting.value = false
  }
}
</script>
