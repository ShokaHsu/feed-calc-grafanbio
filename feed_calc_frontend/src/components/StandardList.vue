<template>
  <div class="page-container">
    
    <div class="toolbar" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
      <div class="search-box" style="display: flex; gap: 10px;">
        <el-input v-model="searchQuery" placeholder="搜尋標準名稱..." style="width: 300px;" clearable @clear="fetchStandards" @keyup.enter="fetchStandards">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="fetchStandards">搜尋</el-button>
      </div>

      <el-button type="success" @click="openCreateDialog">
        <el-icon style="margin-right: 5px"><Plus /></el-icon> 新增自訂標準
      </el-button>
    </div>

    <el-table :data="tableData" border style="width: 100%" v-loading="loading" stripe height="600">
      <el-table-column prop="id" label="ID" width="60" align="center" />
      <el-table-column prop="name" label="標準名稱" min-width="180" sortable show-overflow-tooltip />
      
      <el-table-column label="物種" width="100" align="center" sortable>
        <template #default="scope">{{ getSpeciesLabel(scope.row.species) }}</template>
      </el-table-column>
      
      <el-table-column label="階段" width="120" align="center" sortable>
        <template #default="scope">{{ getStageLabel(scope.row.stage) }}</template>
      </el-table-column>

      <el-table-column label="CP Min" prop="min_crude_protein_percent" width="90" align="center" />
      <el-table-column label="ME Pig" prop="min_me_pig_kcal_per_kg" width="90" align="center" />
      <el-table-column label="Lys SID" prop="min_lysine_sid_pig_g_kg" width="90" align="center" />

      <el-table-column label="來源" width="100" align="center">
        <template #default="scope">
           <el-tag v-if="scope.row.is_public" type="info">系統</el-tag>
           <el-tag v-else type="success">自訂</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="150" align="center" fixed="right">
        <template #default="scope">
            <template v-if="!scope.row.is_public">
                <el-button size="small" type="primary" link @click="openEditDialog(scope.row)">
                    <el-icon><Edit /></el-icon> 修改
                </el-button>
                <el-button size="small" type="danger" link @click="handleDelete(scope.row.id)">
                    <el-icon><Delete /></el-icon> 刪除
                </el-button>
            </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog 
        v-model="dialogVisible" 
        :title="isEditMode ? '修改營養標準' : '新增自訂營養標準'" 
        width="800px" 
        destroy-on-close
    >
      <el-form :model="form" label-position="top" :rules="rules" ref="formRef">
        
        <el-divider content-position="left">基本分類</el-divider>
        <el-row :gutter="20">
            <el-col :span="12">
                <el-form-item label="標準名稱" prop="name">
                    <el-input v-model="form.name" placeholder="例如：自訂肉豬生長 (夏季)" />
                </el-form-item>
            </el-col>
             <el-col :span="6">
                <el-form-item label="物種" prop="species">
                    <el-select v-model="form.species" placeholder="選擇物種" style="width: 100%" @change="handleSpeciesChange">
                        <el-option v-for="opt in SPECIES_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                </el-form-item>
            </el-col>
            <el-col :span="6">
                <el-form-item label="生長階段" prop="stage">
                    <el-select v-model="form.stage" placeholder="選擇階段" style="width: 100%" :disabled="!form.species">
                        <el-option v-for="opt in currentStageOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                </el-form-item>
            </el-col>
        </el-row>

        <el-divider content-position="left">營養需求 (最小值 Min)</el-divider>
        
        <el-row :gutter="20">
            <el-col :span="6"><el-form-item label="粗蛋白 (%)"><el-input-number v-model="form.min_crude_protein_percent" :min="0" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="粗纖維 (%) (Max)"><el-input-number v-model="form.max_crude_fiber_percent" :min="0" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="鈣 (%)"><el-input-number v-model="form.min_calcium_g_per_kg" :min="0" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="有效磷 (%)"><el-input-number v-model="form.min_available_phosphorus_g_per_kg" :min="0" style="width: 100%" /></el-form-item></el-col>
        </el-row>

        <el-divider content-position="left">總胺基酸 (Total)</el-divider>
        <el-row :gutter="20">
            <el-col :span="8"><el-form-item label="Total Lys (%)"><el-input-number v-model="form.min_lysine_total_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="Total Met (%)"><el-input-number v-model="form.min_methionine_total_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="Total M+C (%)"><el-input-number v-model="form.min_met_cys_total_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="Total Thr (%)"><el-input-number v-model="form.min_threonine_total_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="8"><el-form-item label="Total Trp (%)"><el-input-number v-model="form.min_tryptophan_total_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
        </el-row>
        

        <div v-if="form.species === 'SWINE' || form.species === 'OTHER' || !form.species">
            <el-divider content-position="left">豬隻能量與胺基酸 (SID)</el-divider>
            <el-row :gutter="20">
                <el-col :span="8"><el-form-item label="ME Pig (kcal)"><el-input-number v-model="form.min_me_pig_kcal_per_kg" :step="10" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Lys (%)"><el-input-number v-model="form.min_lysine_sid_pig_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Met (%)"><el-input-number v-model="form.min_methionine_sid_pig_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID M+C (%)"><el-input-number v-model="form.min_met_cys_sid_pig_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Thr (%)"><el-input-number v-model="form.min_threonine_sid_pig_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Trp (%)"><el-input-number v-model="form.min_tryptophan_sid_pig_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            </el-row>
        </div>

        
        <div v-if="form.species === 'POULTRY'">
            <el-divider content-position="left">家禽能量與胺基酸 (SID)</el-divider>
            <el-row :gutter="20">
                <el-col :span="8"><el-form-item label="AMEn Broiler (kcal)"><el-input-number v-model="form.min_me_broiler_kcal_per_kg" :step="10" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Lys (%)"><el-input-number v-model="form.min_lysine_sid_broiler_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Met (%)"><el-input-number v-model="form.min_methionine_sid_broiler_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID M+C (%)"><el-input-number v-model="form.min_met_cys_sid_broiler_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Thr (%)"><el-input-number v-model="form.min_min_threonine_sid_broiler_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
                <el-col :span="8"><el-form-item label="SID Trp (%)"><el-input-number v-model="form.min_tryptophan_sid_broiler_g_kg" :step="0.01" style="width: 100%" /></el-form-item></el-col>
            </el-row>
        </div>

      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEditMode ? '儲存修改' : '確認建立' }}
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import request from '@/api/request'
// 加入 Edit icon
import { Search, Plus, Delete, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// Data
const tableData = ref([])
const loading = ref(false)
const searchQuery = ref('')
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 新增：編輯模式狀態
const isEditMode = ref(false)
const editingId = ref(null)

// Options
const SPECIES_OPTIONS = [
    { label: '豬 (SWINE)', value: 'SWINE' },
    { label: '雞 (Poultry)', value: 'POULTRY' },
    { label: '反芻 (Ruminant)', value: 'RUMINANT' },
    { label: '水產 (Aqua)', value: 'AQUA' },
    { label: '其他', value: 'OTHER' },
]

const STAGE_MAP = {
    'SWINE': [
        { value: 'NURSERY', label: '保育期 (Nursery)' },
        { value: 'GROWER', label: '生長期 (Grower)' },
        { value: 'FINISHER', label: '肥育期 (Finisher)' },
        { value: 'GESTATION', label: '懷孕期 (Gestation)' },
        { value: 'LACTATION', label: '泌乳期 (Lactation)' }
    ],
    'POULTRY': [
        { value: 'BROILER_STARTER', label: '肉雞-前期' },
        { value: 'BROILER_GROWER', label: '肉雞-中期' },
        { value: 'BROILER_FINISHER', label: '肉雞-後期' },
        { value: 'LAYER_CHICK', label: '蛋雞-育雛' },
        { value: 'LAYER_PULLET', label: '蛋雞-中雞' },
        { value: 'LAYER_LAYING', label: '蛋雞-產蛋' }
    ],
    'RUMINANT': [
        { value: 'LACTATING_COW_HP', label: '高產乳牛' },
        { value: 'LACTATING_COW_LP', label: '低產乳牛' },
        { value: 'DRY_COW', label: '乾乳牛' },
        { value: 'BEEF_NURSERY', label: '肉牛(保育期)' },
        { value: 'BEEF_GROWER', label: '肉牛(生長期)' },
        { value: 'BEEF_FINISHER', label: '肉牛(肥育期)' },
        { value: 'HEIFER', label: '女牛' }
    ],
    'AQUA': [
        { value: 'CARNIVOROUS_FISH', label: '肉食性魚類' },
        { value: 'HERBIVOROUS_FISH', label: '草食性魚類' },
        { value: 'SHRIMP', label: '蝦類' }
    ],
    'OTHER': [
        { value: 'OTHER', label: '其他階段' }
    ]
}

const form = reactive({
    name: '', species: '', stage: '',
    min_crude_protein_percent: 0, max_crude_fiber_percent: 0,
    min_calcium_g_per_kg: 0, min_available_phosphorus_g_per_kg: 0,
    
    // Total AA
    min_lysine_total_g_kg: 0, min_methionine_total_g_kg: 0,
    min_met_cys_total_g_kg: 0, min_threonine_total_g_kg: 0,
    min_tryptophan_total_g_kg: 0,

    // Swine SID
    min_me_pig_kcal_per_kg: 0, 
    min_lysine_sid_pig_g_kg: 0, min_methionine_sid_pig_g_kg: 0,
    min_met_cys_sid_pig_g_kg: 0, min_threonine_sid_pig_g_kg: 0,
    min_tryptophan_sid_pig_g_kg: 0,
    
    // Poultry SID
    min_me_broiler_kcal_per_kg: 0,
    min_lysine_sid_broiler_g_kg: 0, min_methionine_sid_broiler_g_kg: 0,
    min_met_cys_sid_broiler_g_kg: 0, min_min_threonine_sid_broiler_g_kg: 0, // 注意：您原本程式碼 key 名稱似乎多了一個 min (min_min_threonine...) 請確認後端欄位
    min_tryptophan_sid_broiler_g_kg: 0
})

const rules = {
    name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
    species: [{ required: true, message: '請選擇物種', trigger: 'change' }],
    stage: [{ required: true, message: '請選擇階段', trigger: 'change' }]
}

// Computed
const currentStageOptions = computed(() => {
    return STAGE_MAP[form.species] || []
})

// Methods
const getSpeciesLabel = (val) => SPECIES_OPTIONS.find(o => o.value === val)?.label || val
const getStageLabel = (val) => {
    for (const key in STAGE_MAP) {
        const found = STAGE_MAP[key].find(s => s.value === val)
        if (found) return found.label
    }
    return val
}

const handleSpeciesChange = () => {
    form.stage = ''
}

// 重置表單的輔助函式
const resetForm = () => {
    form.name = ''
    form.species = ''
    form.stage = ''
    
    // 數值歸零
    form.min_crude_protein_percent = 0
    form.max_crude_fiber_percent = 0
    form.min_calcium_g_per_kg = 0
    form.min_available_phosphorus_g_per_kg = 0
    
    form.min_lysine_total_g_kg = 0
    form.min_methionine_total_g_kg = 0
    form.min_met_cys_total_g_kg = 0
    form.min_threonine_total_g_kg = 0
    form.min_tryptophan_total_g_kg = 0

    form.min_me_pig_kcal_per_kg = 0
    form.min_lysine_sid_pig_g_kg = 0
    form.min_methionine_sid_pig_g_kg = 0
    form.min_met_cys_sid_pig_g_kg = 0
    form.min_threonine_sid_pig_g_kg = 0
    form.min_tryptophan_sid_pig_g_kg = 0

    form.min_me_broiler_kcal_per_kg = 0
    form.min_lysine_sid_broiler_g_kg = 0
    form.min_methionine_sid_broiler_g_kg = 0
    form.min_met_cys_sid_broiler_g_kg = 0
    form.min_min_threonine_sid_broiler_g_kg = 0
    form.min_tryptophan_sid_broiler_g_kg = 0
}

const fetchStandards = async () => {
    loading.value = true
    try {
        const res = await request.get('standards/requirements/', {
            params: { q: searchQuery.value }
        })
        tableData.value = res.data.results || res.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

// 開啟「建立」對話框
const openCreateDialog = () => {
    isEditMode.value = false
    editingId.value = null
    resetForm() // 徹底清空
    dialogVisible.value = true
}

// 新增：開啟「編輯」對話框
const openEditDialog = (row) => {
    isEditMode.value = true
    editingId.value = row.id
    
    // 將 row 的資料複製到 form
    // 因為 row 可能包含額外欄位 (如 created_at)，我們用 assign 合併
    // 建議針對需要的欄位賦值，或者直接合併
    Object.assign(form, row)
    
    dialogVisible.value = true
}

const submitForm = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                if (isEditMode.value) {
                    // 修改模式：PUT
                    await request.put(`standards/requirements/${editingId.value}/`, form)
                    ElMessage.success('修改成功！')
                } else {
                    // 新增模式：POST
                    await request.post('standards/requirements/', form)
                    ElMessage.success('新增標準成功！')
                }
                
                dialogVisible.value = false
                fetchStandards() // 重新整理列表
            } catch (e) {
                ElMessage.error(isEditMode.value ? '修改失敗' : '新增失敗')
                console.error(e)
            } finally {
                submitting.value = false
            }
        }
    })
}

const handleDelete = async (id) => {
    ElMessageBox.confirm('確定刪除此標準？', '警告', { type: 'warning' }).then(async () => {
        try {
            await request.delete(`standards/requirements/${id}/`)
            ElMessage.success('刪除成功')
            fetchStandards()
        } catch (e) {
            ElMessage.error('刪除失敗')
        }
    })
}

onMounted(() => {
    fetchStandards()
})
</script>

<style scoped>
/* 這裡可以留空 */
</style>