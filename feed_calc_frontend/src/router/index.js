import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import { isDesktopApp } from '@/utils/env'

const routes = [
    { path: '/login', name: 'Login', component: Login },
    { path: '/register', name: 'Register', component: Register },
    { path: '/', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } }, // 首頁需要登入
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守衛 (Navigation Guard): 沒登入就踢去 Login 頁面
router.beforeEach((to, from, next) => {
    const isPersonal = isDesktopApp()
    const token = localStorage.getItem('auth_token')
    // 1. 如果是個人版 (Desktop App)
    if (isPersonal) {
        // 不論去哪裡，如果想去 login 或 register，都強制轉去 dashboard
        if (to.path === '/login' || to.path === '/register') {
        return next('/')
        }
        // 其他頁面直接放行 (個人版不檢查 Token)
        return next()
    }

    // 2. 如果是雲端版 (Web App) - 這裡維持您原本的邏輯
    if (to.meta.requiresAuth && !token) {
        // 需要權限但沒 token -> 去登入
        return next('/login')
    } else if (token && (to.path === '/login' || to.path === '/register')) {
        // 有 token 但想去登入頁 -> 踢回首頁
        return next('/')
    }

    next()
})

export default router