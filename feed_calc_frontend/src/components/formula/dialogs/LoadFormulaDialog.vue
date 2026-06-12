<template>
  <el-dialog 
    v-model="visible" 
    title="載入舊配方" 
    width="900px" 
    @open="fetchSavedFormulas"
    destroy-on-close
  >
    <div style="margin-bottom: 15px; display: flex; gap: 10px;">
      <el-input v-model="searchFarmQuery" placeholder="輸入客戶..." style="width: 200px" clearable>
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-input v-model="searchNameQuery" placeholder="輸入配方名..." style="width: 200px" clearable>
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <el-table 
        :data="filteredSavedFormulas" 
        v-loading="loading" 
        stripe 
        style="width: 100%" 
        @row-click="handleLoad" 
        height="400"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="customer_name" label="客戶/牧場" width="150" sortable />
      <el-table-column prop="name" label="配方名稱" min-width="150" sortable />
      <el-table-column prop="created_at" label="時間" width="170" sortable>
         <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
      </el-table-column>
      
      <el-table-column label="操作" width="160" align="center">
        <template #default="scope">
          <div @click.stop style="display: flex; gap: 8px; justify-content: center; align-items: center;">
            
            <el-button link type="primary" @click="handleLoad(scope.row)">載入</el-button>
            
            <el-popconfirm 
                title="確定要刪除嗎？" 
                confirm-button-text="是" 
                cancel-button-text="否"
                width="200"
                @confirm="handleDelete(scope.row)"
            >
                <template #reference>
                    <el-button link type="danger">刪除</el-button>
                </template>
            </el-popconfirm>

          </div>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import request from '@/api/request'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../../stores/useFormulaStore'

// Props & Emits
const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue', 'loaded'])

// Store
const formulaStore = useFormulaStore()
const { allStandards, allIngredients, targetStandardId, formulaItems } = storeToRefs(formulaStore)
const { clearFormula, addIngredient, fetchAllIngredients, setSpecies, setStage } = formulaStore

// Local State
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
const savedFormulas = ref([])
const loading = ref(false)
const searchFarmQuery = ref('')
const searchNameQuery = ref('')

// Methods
const fetchSavedFormulas = async () => {
    loading.value = true
    try {
        const res = await request.get('formulas/')
        const rawData = res.data.results || res.data;
        savedFormulas.value = rawData.map(formula => ({
            ...formula,
            customer_name: formula.customer ? formula.customer.name : '未指定客戶'
        }));
    } catch (e) { ElMessage.error('載入列表失敗') } finally { loading.value = false }
}

const filteredSavedFormulas = computed(() => savedFormulas.value.filter(f => {
    const cName = f.customer_name || ''; 
    return (searchFarmQuery.value ? cName.includes(searchFarmQuery.value) : true) && 
           (searchNameQuery.value ? f.name.includes(searchNameQuery.value) : true)
}))

const handleLoad = async (row) => {
    try {
        const res = await request.get(`formulas/${row.id}/`)
        const data = res.data;

        // 1. 還原標準
        if (data.standard) {
            const stdId = typeof data.standard === 'object' ? data.standard.id : data.standard;
            const std = allStandards.value.find(s => s.id === stdId);
            if(std) { 
                setSpecies(std.species);
                setStage(std.stage);
                nextTick(() => targetStandardId.value = std.id) 
            }
        }
        
        // 2. 清空並加入原料 (always re-fetch to pick up any ingredients added since last load)
        clearFormula()
        await fetchAllIngredients()
        const map = new Map(allIngredients.value.map(i => [i.id, i]));

        data.items.forEach(item => {
            const fullIngredient = map.get(item.ingredient);
            if (fullIngredient) { 
                addIngredient(fullIngredient);
                const addedItem = formulaItems.value.find(i => i.id === fullIngredient.id);
                if(addedItem) addedItem.amount = parseFloat(item.amount_kg) || 0;
            }
        })
        
        ElMessage.success('載入成功');
        const customerObj = data.customer && typeof data.customer === 'object' ? data.customer : null
        emit('loaded', {
            name: data.name,
            description: data.description,
            customer: customerObj ? customerObj.id : (data.customer || null),
            customerName: customerObj ? customerObj.name : ''
        })
        visible.value = false;
    } catch (e) { console.error(e); ElMessage.error('載入失敗') }
}

// [新增] 刪除功能
const handleDelete = async (row) => {
    try {
        await request.delete(`formulas/${row.id}/`)
        ElMessage.success('配方已刪除')
        await fetchSavedFormulas() // 重新整理列表
    } catch (e) {
        console.error("刪除失敗:", e)
        ElMessage.error('刪除失敗')
    }
}
</script>