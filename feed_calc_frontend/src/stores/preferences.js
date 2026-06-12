import { defineStore } from 'pinia';
import request from '@/api/request'; 
import { ref } from 'vue';

export const usePreferenceStore = defineStore('preference', () => {
  // 狀態：儲存使用者喜歡的原料 ID 與養分顯示模式
  const favoriteMaterialIds = ref([]); // e.g., [101, 205]
  const nutrientDisplayMode = ref('basic'); // 'basic' | 'advanced'

  // 初始化載入
  async function fetchFavorites() {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const response = await request.get('user/preferences');
        if (response.data) {
          if (response.data.favorites) favoriteMaterialIds.value = response.data.favorites;
          if (response.data.nutrient_display_mode) nutrientDisplayMode.value = response.data.nutrient_display_mode;
        }
        return;
      } catch (error) {
        if (attempt === 2) console.error('無法載入使用者偏好', error);
        else await new Promise(r => setTimeout(r, 2000));
      }
    }
  }

  // 2. 批次儲存：接收一個 ID Array，一次性寫入後端
  async function saveBatchFavorites(newIds) {
    try {
      const response = await request.post('user/preferences', {
        favorites: newIds,
        nutrient_display_mode: nutrientDisplayMode.value
      });
      favoriteMaterialIds.value = newIds;
      return true;
    } catch (error) {
      console.error('儲存失敗', error);
      return false;
    }
  }

  // ✨ [新增] 儲存養分顯示模式
  async function saveNutrientMode(mode) {
    try {
      await request.post('user/preferences', {
        favorites: favoriteMaterialIds.value,
        nutrient_display_mode: mode
      });
      nutrientDisplayMode.value = mode;
      return true;
    } catch (error) {
      console.error('儲存顯示模式失敗', error);
      return false;
    }
  }

  return {
    favoriteMaterialIds,
    nutrientDisplayMode,
    fetchFavorites,
    saveBatchFavorites,
    saveNutrientMode
  };
});