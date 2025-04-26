import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import { createPinia } from "pinia";
import naive from "naive-ui";

import "./style.css";
import App from "./App.vue";
import routes from "./router";
import { useSettingsStore } from "./stores/settings";
import { useI18n, createI18n } from "vue-i18n";
import translations from "./locales/translations.js"; // 添加此行

// 建立 Vue 應用實例
const app = createApp(App);

// 設置路由
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return {
      top: 0,
      behavior: "smooth",
    };
  },
});

// 檢查localStorage中是否有保存的語言設置
const savedLocale = localStorage.getItem("locale") || "zh-TW";

// 建立 i18n 實例
const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: savedLocale, // 使用保存的語言設置或預設值
  messages: translations, // 使用導入的翻譯對象
});

// 設置 Pinia 狀態管理
const pinia = createPinia();
app.use(pinia);
app.use(router);
app.use(naive);
app.use(i18n);

// 初始化應用設定
const settingsStore = useSettingsStore();
settingsStore.initSettings();

// 掛載應用
app.mount("#app");
