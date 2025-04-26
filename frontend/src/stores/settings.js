import { defineStore } from 'pinia';

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    language: localStorage.getItem('language') || 'zh-TW', // 預設使用中文
    darkMode: localStorage.getItem('darkMode') === 'true' || false, // 預設使用淺色模式
  }),
  
  getters: {
    currentLanguage: (state) => state.language,
    isDarkMode: (state) => state.darkMode,
  },
  
  actions: {
    // 切換語言設定
    setLanguage(lang) {
      this.language = lang;
      localStorage.setItem('language', lang);
    },
    
    // 切換深色/淺色模式
    toggleTheme() {
      this.darkMode = !this.darkMode;
      localStorage.setItem('darkMode', this.darkMode.toString());
      // 更新 document 的 class 以便 CSS 變數能生效
      if (this.darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
    
    // 直接設定深色模式狀態
    setDarkMode(isDark) {
      this.darkMode = isDark;
      localStorage.setItem('darkMode', isDark.toString());
      // 更新 document 的 class 以便 CSS 變數能生效
      if (this.darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
    
    // 初始化設定
    initSettings() {
      // 應用存儲的主題設定
      if (this.darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      
      // 如果系統偏好是深色模式但用戶沒有設定過，則自動套用深色模式
      if (localStorage.getItem('darkMode') === null && 
          window.matchMedia && 
          window.matchMedia('(prefers-color-scheme: dark)').matches) {
        this.setDarkMode(true);
      }
    }
  }
});