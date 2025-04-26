import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import {
  create,
  NButton,
  NCard,
  NInput,
  NSelect,
  NGrid,
  NGridItem,
  NTag,
  NSlider,
  NUpload,
  NDropdown,
  NProgress,
  NModal,
  NColorPicker,
  NTabs,
  NTabPane,
  NDrawer,
  NSpace,
  NLayout,
  NLayoutHeader,
  NLayoutSider,
  NLayoutContent,
  NMenu,
  NImage,
  NEmpty,
  NSpin,
  NMessageProvider,
  NConfigProvider,
  NSwitch,
  NIcon,
  NForm,
  NFormItem,
  NRadioGroup,
  NRadio,
  NRadioButton,
  NDivider,
  NAlert,
} from "naive-ui";
import "./style.css";
import App from "./App.vue";
import routes from "./router";
import { useSettingsStore } from "./stores/settings";

// 創建 Naive UI 實例
const naive = create({
  components: [
    NButton,
    NCard,
    NInput,
    NSelect,
    NGrid,
    NGridItem,
    NTag,
    NSlider,
    NUpload,
    NDropdown,
    NProgress,
    NModal,
    NColorPicker,
    NTabs,
    NTabPane,
    NDrawer,
    NSpace,
    NLayout,
    NLayoutHeader,
    NLayoutSider,
    NLayoutContent,
    NMenu,
    NImage,
    NEmpty,
    NSpin,
    NMessageProvider,
    NConfigProvider,
    NSwitch, 
    NIcon,
    NForm,
    NFormItem,
    NRadioGroup,
    NRadio,
    NRadioButton,
    NDivider,
    NAlert,
  ],
});

// 創建路由
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 創建 Pinia 狀態管理
const pinia = createPinia();

// 創建 Vue 應用並掛載
const app = createApp(App);
app.use(pinia);
app.use(router);
app.use(naive);

// 初始化設定 (必須在掛載前調用，以確保首次渲染時已應用正確的主題)
const settingsStore = useSettingsStore();
settingsStore.initSettings();

app.mount("#app");
