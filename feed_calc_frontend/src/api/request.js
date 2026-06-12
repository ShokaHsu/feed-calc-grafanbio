// src/api/request.js
import axios from 'axios';
import { isDesktopApp } from '@/utils/env'; // 1. 引入剛剛的偵測函式
import { useUserStore } from '@/stores/user';

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 15000
});

// Request Interceptor (請求攔截器)
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();

    // === 核心修改邏輯開始 ===
    if (isDesktopApp()) {
      // 情況 A：單機版環境
      // 我們在 Header 帶入特殊標記，告訴後端 "我是單機版，請放行"
      // 這裡用 'Bearer standalone-admin' 當作暗號
      config.headers['Authorization'] = 'Bearer standalone-admin'; 
      
      // 或者也可以加一個自訂 Header 方便辨識
      config.headers['X-Client-Mode'] = 'desktop';
      
    } else {
      // 情況 B：雲端版/網頁版
      // 正常的 Token 流程
      if (userStore.token) {
        config.headers['Authorization'] = `Token ${userStore.token}`;
      }
    }
    // === 核心修改邏輯結束 ===

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor — redirect to login on expired/invalid token
service.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default service;