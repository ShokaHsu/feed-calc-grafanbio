<template>
  <div v-if="isDesktopApp() && !backendReady" class="startup-screen">
    <div class="startup-content">
      <div class="loading-spinner"></div>
      <p class="startup-text">正在啟動服務...</p>
    </div>
  </div>
  <router-view v-else></router-view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { isDesktopApp } from '@/utils/env'
import request from '@/api/request'

const backendReady = ref(false)
let pollTimer = null

async function checkBackend() {
  try {
    await request.get('ingredients/', { params: { page_size: 1 }, timeout: 2000 })
    backendReady.value = true
    clearInterval(pollTimer)
    pollTimer = null
  } catch {
    // not ready yet — keep polling
  }
}

onMounted(() => {
  if (!isDesktopApp()) {
    backendReady.value = true
    return
  }
  checkBackend()
  pollTimer = setInterval(checkBackend, 1000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  background-color: #f5f7fa;
}

.startup-screen {
  position: fixed;
  inset: 0;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.startup-content {
  text-align: center;
  color: #909399;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

.startup-text {
  font-size: 14px;
  margin: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
