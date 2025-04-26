import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import naive from 'naive-ui'

import './style.css'
import App from './App.vue'
import routes from './router'
import { useSettingsStore } from './stores/settings'

// 建立 Vue 應用實例
const app = createApp(App)

// 設置路由
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 設置 Pinia 狀態管理
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(naive)

// 初始化應用設定
const settingsStore = useSettingsStore()
settingsStore.initSettings()

// 掛載應用
app.mount('#app')