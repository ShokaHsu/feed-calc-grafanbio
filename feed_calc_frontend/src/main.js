import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './assets/main-layout.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router' 
import axios from 'axios' 


const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// 註冊所有圖示 (方便之後使用)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// ✨ [關鍵修復] 應用程式啟動時，檢查並恢復 Token
const token = localStorage.getItem('auth_token')
if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
}

app.use(ElementPlus)
app.use(router) // ✨ 關鍵：一定要有這行！
app.mount('#app')