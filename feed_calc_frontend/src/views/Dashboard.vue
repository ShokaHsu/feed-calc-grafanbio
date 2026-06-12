<template>
  <div class="dashboard-container">
    <el-container class="layout-container">
      <el-header class="main-header">
        <div class="header-left">
          <div class="brand">
            <span class="brand-feed">Feed</span><span class="brand-calc">Calc</span>
          </div>
        </div>
        
        <div class="header-right">
          <template v-if="!isPersonalMode">
            <span class="user-greeting">Welcome!</span>
            <el-button type="danger" size="small" @click="handleLogout" plain>
              <el-icon style="margin-right: 5px"><SwitchButton /></el-icon>
              登出
            </el-button>
          </template>

          <template v-else>
            <el-tag type="primary" effect="light" round class="desktop-tag">
              <el-icon style="vertical-align: middle"><Monitor /></el-icon> 
              <span style="vertical-align: middle; margin-left: 4px;">個人單機版</span>
            </el-tag>
          </template>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <el-tabs 
          v-model="activeTab" 
          class="main-tabs"
        >
            <el-tab-pane label="配方計算機" name="calculator">
                <FormulaCalculator />
            </el-tab-pane>

            <el-tab-pane label="原料資料庫" name="ingredients">
                <IngredientList />
            </el-tab-pane>

            <el-tab-pane label="自訂營養標準" name="standards">
                <StandardList />
            </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { SwitchButton, Monitor } from '@element-plus/icons-vue'
import { isDesktopApp } from '@/utils/env'
import { useFormulaStore } from '../stores/useFormulaStore'

const FormulaCalculator = defineAsyncComponent(() => import('../components/FormulaCalculator.vue'))
const IngredientList = defineAsyncComponent(() => import('../components/IngredientList.vue'))
const StandardList = defineAsyncComponent(() => import('../components/StandardList.vue'))

const router = useRouter()
const formulaStore = useFormulaStore()
const activeTab = ref('calculator')
const isPersonalMode = ref(false)

onMounted(() => {
  isPersonalMode.value = isDesktopApp();
})

watch(activeTab, (tab) => {
  if (tab === 'calculator') {
    formulaStore.fetchStandards()
    formulaStore.fetchAllIngredients()
  }
})

const handleLogout = () => {
  ElMessageBox.confirm('確定要登出系統嗎?', '登出確認', {
      confirmButtonText: '登出',
      cancelButtonText: '取消',
      type: 'warning',
    })
    .then(() => {
      localStorage.removeItem('auth_token')
      ElMessage.success('已安全登出')
      router.push('/login')
    })
    .catch(() => {})
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-body);
  overflow: hidden;
}

.layout-container {
  height: 100%;
}

.main-header {
  background-color: #ffffff;
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 54px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  z-index: 100;
  flex-shrink: 0;
}

.brand {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brand-feed {
  color: #1e293b;
}

.brand-calc {
  color: #2563eb;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-greeting {
  font-size: 14px;
  color: var(--text-secondary);
}

.desktop-tag {
  font-weight: 600;
}

.main-content {
  padding: 0 !important;
  flex-grow: 1;
  overflow: hidden;
  position: relative;
}

.main-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background-color: #fff;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  height: 54px;
  line-height: 54px;
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s;
}

:deep(.el-tabs__item:hover) {
  color: #334155;
}

:deep(.el-tabs__item.is-active) {
  color: #2563eb;
  font-weight: 700;
}

:deep(.el-tabs__active-bar) {
  background-color: #2563eb;
  height: 2px;
}

:deep(.el-tabs__content) {
  flex-grow: 1;
  padding: 0 !important;
  overflow-y: auto;
  height: 0;
}
</style>
