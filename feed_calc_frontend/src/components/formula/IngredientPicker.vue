<template>
  <div class="ingredient-picker">
    <div style="display: flex; gap: 10px; align-items: center;">
        
        <el-select 
          v-model="selectedCategory" 
          placeholder="所有分類" 
          clearable 
          style="width: 140px;"
          @change="onCategoryChange"
          class="no-print"
        >
          <el-option 
              v-for="opt in CATEGORY_OPTIONS" 
              :key="opt.value" 
              :label="opt.label" 
              :value="opt.value" 
          />
        </el-select>

        <el-select 
          v-model="selectedIngredientId" 
          filterable 
          :placeholder="selectedCategory ? '請選擇原料' : '搜尋全部原料'" 
          style="width: 200px;" 
          @change="handleAddIngredient" 
          class="no-print"
          no-data-text="此分類無可用原料"
        >
          <el-option-group v-for="group in groupedIngredientOptions" :key="group.label" :label="group.label">
              <el-option v-for="item in group.options" :key="item.id" :label="item.name" :value="item.id" />
          </el-option-group>
        </el-select>
        
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { storeToRefs } from 'pinia'
import { useFormulaStore } from '../../stores/useFormulaStore'
import { ElMessage } from 'element-plus'

// 1. 連接 Store
const formulaStore = useFormulaStore()
const { addIngredient } = formulaStore
const { formulaItems } = storeToRefs(formulaStore) // 用來過濾已選原料

// 2. 接收外部資料
// 注意：allIngredients 很大，且不屬於配方計算的變動狀態，
// 建議維持由父層 (FormulaCalculatorPage) 傳入，或是建立另一個 useIngredientStore。
// 這裡我們先簡單處理：用 props 接收，保持元件單純。
const props = defineProps({
    allIngredients: { type: Array, default: () => [] }
})

// 3. 本地狀態
const selectedCategory = ref('')
const selectedIngredientId = ref(null)

// 4. 選項常數 (直接搬過來)
const CATEGORY_OPTIONS = [
  { label: "穀物 (Cereal)", value: "CEREAL" },
  { label: "油籽類 (Oil Seed)", value: "OIL_SEED" },
  { label: "豆類 (Legume)", value: "LEGUME" },
  { label: "蛋白質飼料 (Protein Feed)", value: "PROTEIN" },
  { label: "能量飼料 (Energy Feed)", value: "ENERGY" },
  { label: "油脂 (Oil/Fat)", value: "OIL_FAT" },
  { label: "塊根塊莖 (Tuber/Root)", value: "TUBER" },
  { label: "牧草 (Forages/roughages)", value: "FORAGE" },
  { label: "魚類/海洋 (Fish/Marine)", value: "FISH_MARINE" },
  { label: "陸生動物產品 (Animal products)", value: "ANIMAL_TERRESTRIAL" },
  { label: "乳製品 (Dairy products)", value: "DAIRY" },
  { label: "礦物質/維他命 (Mineral/Vitamins)", value: "MINERAL" },
  { label: "添加劑 (Additive)", value: "ADDITIVE" },
  { label: "合成氨基酸 (Amino acids)", value: "AMINO_ACID" },
  { label: "其他 (Other)", value: "OTHER" }
]

// 5. 篩選邏輯 (搬過來並稍作修改)
const filteredIngredientsByCategory = computed(() => {
    // 取得已在配方表中的 ID (Store 裡的)
    const usedIds = formulaItems.value.map(i => i.id)

    // 基礎過濾：排除已使用的原料
    let list = props.allIngredients.filter(i => !usedIds.includes(i.id))

    // 分類過濾
    if (selectedCategory.value) {
        list = list.filter(i => i.category === selectedCategory.value)
    }
    
    return list
})

const groupedIngredientOptions = computed(() => {
    const groups = {}
    filteredIngredientsByCategory.value.forEach(item => {
        const cat = item.category || 'Other'
        if(!groups[cat]) groups[cat] = []
        groups[cat].push(item)
    })
    return Object.keys(groups).sort().map(k => ({ label: k, options: groups[k] }))
})

const onCategoryChange = () => {
    selectedIngredientId.value = null
}

// 6. 加入邏輯
const handleAddIngredient = (id) => {
    // 從 props.allIngredients 找原料
    const ing = props.allIngredients.find(i => i.id === id); 
    
    if (ing) {
        const success = addIngredient(ing); // 呼叫 Store Action
        if (!success) ElMessage.warning('已存在'); 
    }
    selectedIngredientId.value = null; 
}
</script>