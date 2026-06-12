<template>
  <div class="page-container">
    
    <div class="toolbar" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
      
      <div class="search-box" style="width: 550px; display: flex; align-items: center; gap: 10px;">
        <el-input
          v-model="searchQuery"
          placeholder="搜尋原料名稱..."
          class="input-with-select"
          clearable
          @clear="fetchIngredients"
          @keyup.enter="fetchIngredients"
          style="flex: 1;"
        >
          <template #prepend>
            <el-select 
              v-model="searchCategory" 
              placeholder="分類" 
              style="width: 110px"
              clearable
              @change="fetchIngredients"
            >
              <el-option label="所有" value="" />
              <el-option 
                v-for="opt in CATEGORY_OPTIONS" 
                :key="opt.value" 
                :label="opt.label" 
                :value="opt.value" 
              />
            </el-select>
          </template>
          <template #append>
            <el-button @click="fetchIngredients"><el-icon><Search /></el-icon></el-button>
          </template>
        </el-input>
        
        <el-checkbox v-model="filterCommonOnly" label="只看常用" border style="background: white;" @change="fetchIngredients" />
        
        <transition name="el-fade-in">
            <el-button 
                v-if="hasChanges"
                type="success" 
                @click="confirmSaveFavorites"
                class="save-fav-btn"
            >
                <el-icon style="margin-right: 5px"><CollectionTag /></el-icon> 儲存常用 ({{ changesCount }})
            </el-button>
        </transition>
      </div>

      <div class="action-box" style="display: flex; gap: 10px; align-items: center;">
        
        <el-popover placement="bottom" title="選擇顯示欄位" :width="300" trigger="click">
          <template #reference>
            <el-button type="warning" plain>
              <el-icon style="margin-right: 5px"><Operation /></el-icon> 顯示設定
            </el-button>
          </template>
          <el-checkbox-group v-model="visibleGroups" style="display: flex; flex-direction: column; gap: 5px;">
            <el-checkbox v-for="(config, key) in COLUMN_CONFIG" :key="key" :label="key">
              {{ config.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-popover>

        <el-button 
            type="danger" 
            plain
            @click="handleBatchDelete" 
            :disabled="selectedRows.length === 0"
        >
            <el-icon style="margin-right: 5px"><Delete /></el-icon> 刪除 ({{ selectedRows.length }})
        </el-button>

        <el-button type="primary" @click="openCreateDialog">
            <el-icon style="margin-right: 5px"><Plus /></el-icon> 新增原料
        </el-button>
      </div>
    </div>

    <el-table 
        :data="tableData" 
        border 
        style="width: 100%" 
        v-loading="loading" 
        stripe 
        height="650"
        @selection-change="handleSelectionChange"
        size="small"
    >
      <el-table-column type="selection" width="40" align="center" fixed="left" />
      
      <el-table-column label="常用" width="55" align="center" fixed="left">
        <template #default="scope">
            <div 
                @click="toggleLocalFavorite(scope.row.id)" 
                style="cursor: pointer; font-size: 18px; line-height: 1;"
                title="設為常用原料"
            >
                <el-icon v-if="isFavorite(scope.row.id)" color="#F7BA2A"><StarFilled /></el-icon>
                <el-icon v-else color="#DCDFE6"><Star /></el-icon>
            </div>
        </template>
      </el-table-column>

      <el-table-column prop="name" label="原料名稱" width="160" sortable fixed="left" show-overflow-tooltip />
      <el-table-column prop="category" label="分類" width="100" sortable show-overflow-tooltip>
         <template #default="scope">
            {{ getCategoryLabel(scope.row.category) }}
         </template>
      </el-table-column>
      <el-table-column prop="cost_per_kg_twd" label="成本($)" width="80" sortable align="right" fixed="left">
          <template #default="scope">
              <span style="color: #E6A23C; font-weight: bold;">{{ scope.row.cost_per_kg_twd }}</span>
          </template>
      </el-table-column>
      
      <el-table-column label="來源" width="70" align="center">
        <template #default="scope">
           <el-tag v-if="scope.row.is_public" type="info" size="small" effect="plain">系統</el-tag>
           <el-tag v-else type="success" size="small" effect="plain">自訂</el-tag>
        </template>
      </el-table-column>

      <template v-for="(group, key) in COLUMN_CONFIG" :key="key">
        <el-table-column :label="group.label" align="center" v-if="visibleGroups.includes(key)">
            <el-table-column 
                v-for="field in group.fields" 
                :key="field.prop"
                :prop="field.prop" 
                :label="field.label" 
                :width="field.width || 80" 
                align="center"
            >
                <template #default="scope">
                    <span :class="{'text-muted': !scope.row[field.prop]}">
                        {{ formatNumber(scope.row[field.prop]) }}
                    </span>
                </template>
            </el-table-column>
        </el-table-column>
      </template>

      <el-table-column label="操作" width="80" align="center" fixed="right">
        <template #default="scope">
            <el-button 
                v-if="canEdit(scope.row)" 
                size="small" 
                type="primary" 
                link 
                @click="openEditDialog(scope.row)"
            >
                <el-icon><Edit /></el-icon> 編輯
            </el-button>
            <el-tooltip v-else content="系統唯讀原料" placement="top">
                <el-icon color="#999"><Lock /></el-icon>
            </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
       <el-pagination 
         v-model:current-page="currentPage"
         v-model:page-size="pageSize"
         :page-sizes="[20, 50, 100, 200]"
         layout="total, sizes, prev, pager, next" 
         :total="totalCount" 
         @size-change="handleSizeChange"
         @current-change="handlePageChange"
       />
    </div>

    <el-dialog 
        v-model="dialogVisible" 
        :title="isEditMode ? '編輯原料' : '新增原料'" 
        width="90%" 
        top="5vh"
        destroy-on-close
        :close-on-click-modal="false"
    >
         <el-form :model="form" label-position="top" :rules="rules" ref="formRef" size="default">
          <el-tabs type="border-card" class="edit-tabs" v-model="activeTab">
              <el-tab-pane label="基本資料" name="basic">
                  <el-row :gutter="20">
                    <el-col :span="8"><el-form-item label="原料名稱" prop="name"><el-input v-model="form.name" /></el-form-item></el-col>
                    <el-col :span="8">
                      <el-form-item label="分類">
                        <el-select v-model="form.category" style="width: 100%">
                          <el-option v-for="opt in CATEGORY_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="成本 (TWD/kg)" prop="cost_per_kg_twd">
                        <el-input-number v-model="form.cost_per_kg_twd" :min="0" :step="0.1" style="width: 100%" controls-position="right" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="24" v-if="isSuperUser">
                        <el-divider content-position="left">管理員選項</el-divider>
                        <el-checkbox v-model="form.is_public">設為公用系統原料 (所有人都看得到但不可改)</el-checkbox>
                    </el-col>
                  </el-row>
              </el-tab-pane>

              <el-tab-pane v-for="(group, key) in COLUMN_CONFIG" :key="key" :label="group.label" :name="key">
                  <el-row :gutter="15">
                      <el-col :span="6" :xs="12" v-for="field in group.fields" :key="field.prop">
                          <el-form-item :label="field.label">
                              <el-input-number 
                                v-model="form[field.prop]" 
                                :min="0" 
                                style="width: 100%" 
                                :precision="field.precision || 2"
                                controls-position="right" 
                              />
                          </el-form-item>
                      </el-col>
                  </el-row>
              </el-tab-pane>

          </el-tabs>
        </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 12px; color: #999;">
                <el-icon><InfoFilled /></el-icon> 提示：未填寫數值將自動儲存為 0
            </div>
            <div>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitForm" :loading="submitting">儲存設定</el-button>
            </div>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import request from '@/api/request'
import { isDesktopApp } from '@/utils/env'
import { Search, Plus, Delete, Edit, Operation, Lock, InfoFilled, Star, StarFilled, CollectionTag } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePreferenceStore } from '@/stores/preferences'



// --- Preference Store & Logic ---
const prefStore = usePreferenceStore()
const pendingFavorites = ref([]) // Local draft of favorites

// 1. Check if ID is in local favorites
const isFavorite = (id) => {
    return pendingFavorites.value.includes(id)
}

// 2. Toggle local state (doesn't hit API)
const toggleLocalFavorite = (id) => {
    const index = pendingFavorites.value.indexOf(id)
    if (index === -1) {
        pendingFavorites.value.push(id)
    } else {
        pendingFavorites.value.splice(index, 1)
    }
}

// 3. Detect changes
const hasChanges = computed(() => {
    // Compare sets to ignore order
    const storeSet = new Set(prefStore.favoriteMaterialIds)
    const localSet = new Set(pendingFavorites.value)
    
    if (storeSet.size !== localSet.size) return true
    for (let id of localSet) {
        if (!storeSet.has(id)) return true
    }
    return false
})

const changesCount = computed(() => {
    // Calculate difference count simply
    return Math.abs(pendingFavorites.value.length - prefStore.favoriteMaterialIds.length) || '...'
})


// 4. Save to Backend
const confirmSaveFavorites = async () => {
    try {
        await ElMessageBox.confirm(
            `您更動了常用原料設定，確定要儲存嗎？`, 
            '儲存常用設定', 
            { confirmButtonText: '儲存', cancelButtonText: '取消', type: 'info' }
        )
        
        const success = await prefStore.saveBatchFavorites(pendingFavorites.value)
        if (success) {
            ElMessage.success('常用原料已更新')
            // Refresh logic if needed (e.g. if filtering by common)
            if (filterCommonOnly.value) {
                fetchIngredients()
            }
        } else {
            ElMessage.error('儲存失敗')
        }
    } catch (e) {
        // Cancelled
    }
}


// --- Rest of your existing logic (Configuration, State, etc.) ---
// (Copying your existing COLUMN_CONFIG here - omitted for brevity but assume it's same as provided)
const COLUMN_CONFIG = {
    proximate: {
        label: '五大營養 (%)',
        fields: [
            { prop: 'dm_percent', label: '乾物質 DM' },
            { prop: 'crude_protein_percent', label: '粗蛋白 CP' },
            { prop: 'crude_fiber_percent', label: '粗纖維 CF' },
            { prop: 'crude_fat_percent', label: '粗脂肪 EE' },
            { prop: 'ash_percent', label: '灰分 Ash' },
            { prop: 'starch_percent', label: '澱粉' },
            { prop: 'sugar_percent', label: '糖' },
            { prop: 'ndf_percent', label: 'NDF' },
            { prop: 'adf_percent', label: 'ADF' },
        ]
    },
    energy: {
        label: '能量 (kcal/kg)',
        fields: [
            { prop: 'de_pig_kcal_per_kg', label: '豬 DE', width: 90, precision: 0 },
            { prop: 'me_pig_kcal_per_kg', label: '豬 ME', width: 90, precision: 0 },
            { prop: 'ne_pig_growth_kcal_per_kg', label: '肉豬 NEg', width: 100, precision: 0 },
            { prop: 'ne_pig_sow_kcal_per_kg', label: '母豬 NEs', width: 100, precision: 0 },
            { prop: 'amen_broiler_kcal_per_kg', label: '肉雞 AMEn', width: 100, precision: 0 },
            { prop: 'amen_cockerel_kcal_per_kg', label: '蛋雞 AMEn', width: 100, precision: 0 },
            { prop: 'me_ruminant_kcal_per_kg', label: '反芻 ME', width: 90, precision: 0 },
        ]
    },
    total_aa: {
        label: '總胺基酸 (g/kg)',
        fields: [
            { prop: 'lysine_total_g_kg', label: 'Lys' },
            { prop: 'methionine_total_g_kg', label: 'Met' },
            { prop: 'met_cys_total_g_kg', label: 'M+C' },
            { prop: 'threonine_total_g_kg', label: 'Thr' },
            { prop: 'tryptophan_total_g_kg', label: 'Trp' },
            { prop: 'valine_total_g_kg', label: 'Val' },
            { prop: 'isoleucine_total_g_kg', label: 'Ile' },
            { prop: 'leucine_total_g_kg', label: 'Leu' },
            { prop: 'arginine_total_g_kg', label: 'Arg' },
            { prop: 'histidine_total_g_kg', label: 'His' },
            // ... 可視需求增加其他非必須胺基酸
        ]
    },
    sid_pig: {
        label: 'SID 豬胺基酸 (g/kg)',
        fields: [
            { prop: 'lysine_sid_pig_g_kg', label: 'SID Lys' },
            { prop: 'methionine_sid_pig_g_kg', label: 'SID Met' },
            { prop: 'met_cys_sid_pig_g_kg', label: 'SID M+C' },
            { prop: 'threonine_sid_pig_g_kg', label: 'SID Thr' },
            { prop: 'tryptophan_sid_pig_g_kg', label: 'SID Trp' },
            { prop: 'valine_sid_pig_g_kg', label: 'SID Val' },
            { prop: 'isoleucine_sid_pig_g_kg', label: 'SID Ile' },
            { prop: 'leucine_sid_pig_g_kg', label: 'SID Leu' },
        ]
    },
    sid_poultry: {
        label: 'SID 家禽胺基酸 (g/kg)',
        fields: [
            { prop: 'lysine_sid_poultry_g_kg', label: 'SID Lys' },
            { prop: 'methionine_sid_poultry_g_kg', label: 'SID Met' },
            { prop: 'met_cys_sid_poultry_g_kg', label: 'SID M+C' },
            { prop: 'threonine_sid_poultry_g_kg', label: 'SID Thr' },
            { prop: 'tryptophan_sid_poultry_g_kg', label: 'SID Trp' },
            { prop: 'valine_sid_poultry_g_kg', label: 'SID Val' },
        ]
    },
    minerals: {
        label: '礦物質 (g, mg/kg)',
        fields: [
            { prop: 'calcium_g_per_kg', label: '鈣 Ca (g)' },
            { prop: 'phosphorus_g_per_kg', label: '磷 P (g)' },
            { prop: 'available_phosphorus_g_per_kg', label: '有效磷 (g)' },
            { prop: 'sodium_g_per_kg', label: '鈉 Na (g)' },
            { prop: 'potassium_g_per_kg', label: '鉀 K (g)' },
            { prop: 'chloride_g_per_kg', label: '氯 Cl (g)' },
            { prop: 'iron_mg_per_kg', label: '鐵 Fe (mg)' },
            { prop: 'copper_mg_per_kg', label: '銅 Cu (mg)' },
            { prop: 'zinc_mg_per_kg', label: '鋅 Zn (mg)' },
        ]
    },
    vitamins: {
        label: '維生素/其他',
        fields: [
            { prop: 'vitamin_e_mg_kg', label: 'Vit E' },
            { prop: 'choline_mg_kg', label: '膽鹼' },
            { prop: 'linoleic_acid_g_kg', label: '亞麻油酸' },
        ]
    }
}

// Variables
const tableData = ref([])
const loading = ref(false)
const searchQuery = ref('')
const totalCount = ref(0)
const pageSize = ref(20)
const currentPage = ref(1)
const selectedRows = ref([])
const searchCategory = ref('')
const activeTab = ref('basic')
const visibleGroups = ref(['proximate', 'energy'])
const isSuperUser = ref(false) 
const dialogVisible = ref(false)
const submitting = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const filterCommonOnly = ref(false)

const CATEGORY_OPTIONS = [
  { label: "穀物 (Cereal)", value: "CEREAL" },
  { label: "油籽類 (Oil Seed)", value: "OIL_SEED" },
  { label: "豆類 (Legume)", value: "LEGUME" },
  { label: "蛋白質飼料 (Protein Feed)", value: "PROTEIN" },
  { label: "能量飼料 (Energy Feed)", value: "ENERGY" },
  { label: "油脂 (Oil/Fat)", value: "OIL_FAT" },
  { label: "塊根塊莖 (Tuber/Root)", value: "TUBER" },
  { label: "牧草 (Forages)", value: "FORAGE" },
  { label: "魚類/海洋 (Fish/Marine)", value: "FISH_MARINE" },
  { label: "陸生動物產品 (Animal)", value: "ANIMAL_TERRESTRIAL" },
  { label: "乳製品 (Dairy)", value: "DAIRY" },
  { label: "礦物質 (Mineral)", value: "MINERAL" },
  { label: "添加劑 (Additive)", value: "ADDITIVE" },
  { label: "胺基酸 (Amino Acid)", value: "AMINO_ACID" },
  { label: "其他 (Other)", value: "OTHER" }
]

const getInitialForm = () => {
    const f = {
        id: null,
        name: '',
        category: 'OTHER',
        cost_per_kg_twd: 0,
        is_common: false,
        is_public: false,
        share_with_org: false
    }
    Object.values(COLUMN_CONFIG).forEach(group => {
        group.fields.forEach(field => {
            f[field.prop] = 0
        })
    })
    return f
}

const form = reactive(getInitialForm())
const rules = {
  name: [{ required: true, message: '請輸入原料名稱', trigger: 'blur' }],
  cost_per_kg_twd: [{ required: true, message: '請輸入成本', trigger: 'blur' }]
}

// Helpers
const getCategoryLabel = (val) => {
    const found = CATEGORY_OPTIONS.find(c => c.value === val)
    return found ? found.label : val
}
const formatNumber = (val) => {
    if (val === undefined || val === null) return '-'
    return val
}
const canEdit = (row) => {
    if (isSuperUser.value) return true
    return !row.is_public
}

// API
const fetchIngredients = async () => {
    loading.value = true
    try {
        const res = await request.get('ingredients/', {
            params: {
                q: searchQuery.value,
                category: searchCategory.value,
                // Note: Backend might need to handle 'is_common' differently now that it's user-specific
                is_common: filterCommonOnly.value ? 'true' : undefined,
                page: currentPage.value,
                page_size: pageSize.value
            }
        })
        
        const responseData = res.data
        if (Array.isArray(responseData)) {
            tableData.value = responseData
            totalCount.value = responseData.length
        } else {
            tableData.value = responseData.results
            totalCount.value = responseData.count
        }
    } catch (e) {
        console.error(e)
        ElMessage.error('載入失敗')
    } finally {
        loading.value = false
    }
}

const fetchUserProfile = async () => {
    if (isDesktopApp()) {
        isSuperUser.value = true
        return
    }
    try {
        const res = await request.get('auth/users/me/')
        if (res.data.is_superuser) {
            isSuperUser.value = true
        }
    } catch (e) {}
}

const handleSelectionChange = (val) => { selectedRows.value = val }
const handleBatchDelete = async () => {
    if (selectedRows.value.length === 0) return;
    const hasSystemData = selectedRows.value.some(row => row.is_public);
    if (hasSystemData && !isSuperUser.value) {
        ElMessage.warning('選取項目中包含「系統原料」，您無法刪除系統原料。');
        return;
    }
    ElMessageBox.confirm(
        `確定要刪除選取的 ${selectedRows.value.length} 筆原料嗎？`, '刪除確認', { confirmButtonText: '刪除', cancelButtonText: '取消', type: 'warning' }
    ).then(async () => {
        try {
            const ids = selectedRows.value.map(row => row.id)
            await request.post('ingredients/bulk-delete/', { ids })
            ElMessage.success('刪除成功')
            fetchIngredients() 
            selectedRows.value = [] 
        } catch (e) {
            ElMessage.error('刪除失敗')
        }
    }).catch(() => {})
}
const openCreateDialog = () => {
    isEditMode.value = false
    editingId.value = null
    const init = getInitialForm()
    Object.keys(init).forEach(k => form[k] = init[k])
    dialogVisible.value = true
    activeTab.value = 'basic'
}
const openEditDialog = (row) => {
    isEditMode.value = true
    editingId.value = row.id
    Object.keys(form).forEach(key => {
        if (row[key] !== undefined) form[key] = row[key]
    })
    form.id = row.id 
    dialogVisible.value = true
    activeTab.value = 'basic'
}
const submitForm = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                const payload = { ...form }
                delete payload.id
                if (isEditMode.value) {
                    await request.patch(`ingredients/${editingId.value}/`, payload)
                    ElMessage.success('修改成功')
                } else {
                    await request.post('ingredients/', payload)
                    ElMessage.success('新增成功')
                }
                dialogVisible.value = false
                fetchIngredients() 
            } catch (e) {
                ElMessage.error('操作失敗')
            } finally {
                submitting.value = false
            }
        }
    })
}
const handlePageChange = (page) => { currentPage.value = page; fetchIngredients() }
const handleSizeChange = (size) => { pageSize.value = size; fetchIngredients() }

onMounted(async () => {
    fetchUserProfile()
    fetchIngredients()
    // ✨ [New] Load favorites from backend, then copy to local pending
    await prefStore.fetchFavorites()
    pendingFavorites.value = [...prefStore.favoriteMaterialIds]
})
</script>

<style scoped>
.text-muted {
    color: #ccc;
}
.edit-tabs > :deep(.el-tabs__content) {
    padding: 20px;
    height: 400px;
    overflow-y: auto; 
}
/* ✨ [New] Animation for Save Button */
.save-fav-btn {
    animation: bounceIn 0.5s;
}
@keyframes bounceIn {
    0% { transform: scale(0.9); opacity: 0; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); }
}
</style>