<template>
  <div class="nutrient-row">
    <div class="row-header">
      <span class="p-label">{{ label }}</span>
      <div class="p-values">
        <span class="p-current" :class="statusClass">
          {{ Number(current).toFixed(decimals) }} {{ unit }}
          <template v-if="hasTarget">
            <span v-if="isBelowMin"> ↓</span>
            <span v-if="isAboveMax"> ↑</span>
          </template>
        </span>
        <span class="p-target" v-if="hasTarget">
          / {{ Number(target).toFixed(decimals) }}
        </span>
      </div>
    </div>
    
    <div class="bar-container">
      <div 
        class="bar-fill" 
        :style="{ 
          width: fillPercentage + '%', 
          backgroundColor: barColor 
        }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  current: { type: Number, default: 0 },
  target: { type: [Number, String], default: null },
  unit: { type: String, default: '' },
  decimals: { type: Number, default: 2 },
  isMax: { type: Boolean, default: false },
  accentColor: { type: String, default: '#2563eb' }
})

const hasTarget = computed(() => {
  return props.target !== null && 
         props.target !== undefined && 
         props.target !== '' &&
         !isNaN(props.target) &&
         Number(props.target) > 0;
})

const isBelowMin = computed(() => {
  if (!hasTarget.value || props.isMax) return false;
  return props.current < props.target;
})

const isAboveMax = computed(() => {
  if (!hasTarget.value || !props.isMax) return false;
  return props.current > props.target;
})

const statusClass = computed(() => {
  if (!hasTarget.value) return 'status-ok';
  if (isBelowMin.value) return 'status-deficient';
  if (isAboveMax.value) return 'status-excess';
  return 'status-ok';
})

const fillPercentage = computed(() => {
  if (!hasTarget.value) {
    // 沒有目標時，顯示一個固定的視覺比例（例如 50%）
    return 50;
  }
  return Math.min((props.current / props.target) * 100, 100);
})

const barColor = computed(() => {
  if (!hasTarget.value) return '#cbd5e1';
  return props.accentColor;
})
</script>

<style scoped>
.nutrient-row {
  margin-bottom: 16px;
}

.row-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.p-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.p-values {
  font-size: 14px;
}

.p-current {
  font-weight: 700;
}

.status-ok {
  color: #1e293b;
}

.status-deficient {
  color: #dc2626;
}

.status-excess {
  color: #d97706;
}

.p-target {
  color: #94a3b8;
  margin-left: 4px;
  font-weight: 400;
}

.bar-container {
  height: 6px;
  background-color: #f1f5f9;
  border-radius: 4px;
  width: 100%;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease, background-color 0.3s ease;
}
</style>
