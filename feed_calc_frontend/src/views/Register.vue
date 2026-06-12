<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>註冊新帳號</h2>
      </template>
      <el-form label-position="top" :model="form" status-icon>
        
        <el-form-item label="使用者名稱 (帳號)" prop="username">
          <el-input v-model="form.username" placeholder="請輸入帳號" />
        </el-form-item>

        <el-form-item label="電子郵件 (必填)" prop="email" :rules="[{ required: true, message: '請輸入 Email', trigger: 'blur' }]">
          <el-input v-model="form.email" placeholder="example@email.com" />
        </el-form-item>

        <el-form-item label="密碼" prop="password">
          <el-input v-model="form.password" type="password" placeholder="請輸入密碼" show-password />
        </el-form-item>

        <el-form-item label="確認密碼" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="請再次輸入密碼" show-password @keyup.enter="handleRegister" />
        </el-form-item>

        <el-button type="success" style="width: 100%" @click="handleRegister" :loading="loading">
          註冊並登入
        </el-button>
        
        <div style="margin-top: 15px; text-align: center;">
            <router-link to="/login" style="text-decoration: none; color: #409EFF;">
              已經有帳號了？返回登入
            </router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import request from '@/api/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
})

const handleRegister = async () => {
    // 1. 基礎前端驗證：確保帳號、Email、密碼都已填寫
    if (!form.username || !form.password || !form.email) {
        ElMessage.warning('請填寫完整欄位 (帳號、Email、密碼)')
        return
    }

    // 2. 驗證兩次密碼是否相同
    if (form.password !== form.confirmPassword) {
        ElMessage.error('兩次密碼輸入不一致')
        return
    }
    
    loading.value = true

    try {
        // 3. 呼叫後端註冊 API
        // 注意：我們明確傳送 username 和 email，確保後端能正確區分
        const res = await request.post('auth/register/', {
            username: form.username,
            email: form.email,
            password: form.password
        })

        const token = res.data.token
        userStore.setLoginInfo(token, res.data.username || form.username, res.data.user_id || '')

        ElMessage.success(`歡迎加入！ ${res.data.username}`)
        
        // 5. 跳轉回首頁 (Dashboard)
        router.push('/')
        
    } catch (e) {
        console.error("註冊錯誤:", e)
        
        // 6. 詳細錯誤處理 (顯示後端回傳的具體原因)
        if (e.response && e.response.data) {
            const errData = e.response.data

            // 優先檢查 Email 錯誤 (例如：已存在)
            if (errData.email) {
                // errData.email 是一個陣列，取第 0 個訊息
                ElMessage.error(`Email 錯誤：${errData.email[0]}`)
            } 
            // 檢查帳號錯誤 (例如：已存在)
            else if (errData.username) {
                ElMessage.error(`帳號錯誤：${errData.username[0]}`)
            } 
            // 檢查密碼錯誤 (例如：太短)
            else if (errData.password) {
                ElMessage.error(`密碼錯誤：${errData.password[0]}`)
            } 
            else {
                ElMessage.error('註冊失敗：請檢查輸入資料')
            }
        } else {
            ElMessage.error('伺服器連線錯誤，請稍後再試')
        }
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}
.register-card {
  width: 400px;
}
h2 {
    text-align: center;
    margin: 0;
    color: #303133;
}
</style>