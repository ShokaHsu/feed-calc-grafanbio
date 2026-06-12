<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>會員登入</h2>
      </template>
      <el-form label-position="top">
        <el-form-item label="電子郵件">
          <el-input v-model="username" placeholder="Username" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="password" type="password" placeholder="Password" show-password @keyup.enter="handleLogin"/>
        </el-form-item>
        <el-button type="primary" style="width: 100%" @click="handleLogin" :loading="loading">登入</el-button>
        
        <div style="margin-top: 10px; text-align: center;">
            <router-link to="/register">還沒有帳號？點此註冊</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { isDesktopApp } from '@/utils/env'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

onMounted(() => {
    if (isDesktopApp()) {
        console.log('偵測到個人版環境，跳過登入頁面')
        router.replace('/')
    }
})

const handleLogin = async () => {
    if(!username.value || !password.value) {
        ElMessage.warning('請輸入帳號密碼')
        return
    }

    loading.value = true
    try {
        const res = await request.post('auth/login/', {
            username: username.value,
            password: password.value
        })

        const token = res.data.token
        userStore.setLoginInfo(token, res.data.username || username.value, res.data.user_id || '')

        ElMessage.success('登入成功')
        router.push('/')

    } catch (e) {
        console.error(e)
        ElMessage.error('登入失敗，請檢查帳號密碼')
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
.login-card { width: 400px; }
</style>