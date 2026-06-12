import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('user', () => {
  // 1. 狀態 State
  // 嘗試從 localStorage 讀取 token，這樣重新整理後才不會登出
  const token = ref(localStorage.getItem('auth_token') || '');
  const username = ref(localStorage.getItem('username') || '');
  const userId = ref(localStorage.getItem('user_id') || '');

  // 2. 動作 Actions
  
  // 設定登入資訊 (Login 成功後呼叫)
  function setLoginInfo(newToken, newUsername, newUserId) {
    token.value = newToken;
    username.value = newUsername;
    userId.value = newUserId;

    // 同步寫入 localStorage
    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('username', newUsername);
    localStorage.setItem('user_id', newUserId);
  }

  // 登出清理 (Logout 呼叫)
  function logout() {
    token.value = '';
    username.value = '';
    userId.value = '';

    // 清除 localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
  }

  return {
    token,
    username,
    userId,
    setLoginInfo,
    logout
  };
});