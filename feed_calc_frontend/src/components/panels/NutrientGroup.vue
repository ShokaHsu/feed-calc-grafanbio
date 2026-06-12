<template>
  <div class="nutrient-group" :class="{ 'is-collapsed': collapsed }">
    <div class="group-header" @click="toggleCollapse">
      <div class="header-left">
        <div class="accent-bar" :style="{ backgroundColor: color }"></div>
        <span class="group-name" :style="{ color: color }">{{ name }}</span>
      </div>
      <div class="header-right">
        <el-tag v-if="status === 'ok'" type="success" size="small" effect="light" round class="status-badge">✓ 達標</el-tag>
        <el-tag v-else-if="status === 'deficient'" type="danger" size="small" effect="light" round class="status-badge">⚠ {{ count }} 不足</el-tag>
        <el-tag v-else-if="status === 'excess'" type="warning" size="small" effect="light" round class="status-badge">⚠ {{ count }} 超標</el-tag>
        
        <span v-if="collapsed && mode === 'basic' && name !== '能量與概略養分' && name !== '胺基酸'" class="hint-text">
          進階模式顯示 ›
        </span>
        
        <el-icon class="chevron-icon"><ArrowDown v-if="!collapsed" /><ArrowRight v-else /></el-icon>
      </div>
    </div>
    
    <el-collapse-transition>
      <div v-show="!collapsed" class="group-content">
        <slot></slot>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ArrowDown, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  name: String,
  color: String,
  status: { type: String, default: 'ok' },
  count: { type: Number, default: 0 },
  initialCollapsed: { type: Boolean, default: false },
  mode: String
})

const collapsed = ref(props.initialCollapsed)

watch(() => props.initialCollapsed, (val) => {
  collapsed.value = val
})

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}
</script>

<style scoped>
.nutrient-group {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.group-header:hover {
  background-color: #f8fafc;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.accent-bar {
  width: 3px;
  height: 16px;
  border-radius: 2px;
}

.group-name {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  font-weight: 700;
  font-size: 11px;
}

.hint-text {
  font-size: 11px;
  color: #94a3b8;
}

.chevron-icon {
  font-size: 14px;
  color: #94a3b8;
}

.group-content {
  padding: 8px 16px 16px 16px;
}
</style>