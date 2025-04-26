<script setup>
import { ref, watchEffect } from "vue";
import { useRouter } from "vue-router";
import {
  NConfigProvider,
  NMessageProvider,
  NLayout,
  NLayoutSider,
  NLayoutContent,
  NMenu,
  NIcon,
  NSwitch,
  NSpace,
  NDropdown,
  NButton,
} from "naive-ui";
import { h } from "vue";
import { useTranslation } from "./composables/useTranslation";
import { useTheme } from "./composables/useTheme";
import { useSettingsStore } from "./stores/settings";

const router = useRouter();
const collapsed = ref(false);
const activeKey = ref("project");
const { t, currentLanguage } = useTranslation();
const { isDarkMode, toggleTheme, themeOverrides } = useTheme();
const settingsStore = useSettingsStore();

// 側邊欄菜單選項
const menuOptions = ref([
  {
    label: () => t("project"),
    key: "project",
    icon: renderIcon("📁"),
  },
  {
    label: () => t("gallery"),
    key: "gallery",
    icon: renderIcon("🖼️"),
  },
  {
    label: () => t("designInput"),
    key: "design",
    icon: renderIcon("🖌️"),
    children: [
      {
        label: () => t("designInput"),
        key: "design-input",
        icon: renderIcon("✏️"),
      },
      {
        label: () => t("aiGenerate"),
        key: "ai-generate",
        icon: renderIcon("🤖"),
      },
    ],
  },
  {
    label: () => t("settings"),
    key: "settings",
    icon: renderIcon("⚙️"),
  },
]);

// 語言選項下拉菜單
const languageOptions = [
  {
    label: "中文",
    key: "zh-TW"
  },
  {
    label: "English",
    key: "en-US"
  }
];

// 渲染圖標
function renderIcon(text) {
  return () => h(NIcon, null, { default: () => text });
}

// 菜單選擇處理
function handleMenuSelect(key) {
  activeKey.value = key;

  switch (key) {
    case "project":
      router.push({ name: "home" });
      break;
    case "gallery":
      router.push({ name: "gallery" });
      break;
    case "design-input":
      router.push({ name: "design-input", params: { projectId: "" } });
      break;
    case "ai-generate":
      router.push({ name: "ai-generate", params: { projectId: "temp" } });
      break;
    case "settings":
      router.push({ name: "settings" });
      break;
  }
}

// 處理語言選擇
function handleLanguageSelect(key) {
  settingsStore.setLanguage(key);
}

// 初始化頁面主題
watchEffect(() => {
  const root = document.documentElement;
  if (isDarkMode.value) {
    root.classList.add('dark');
    root.classList.remove('light');
  } else {
    root.classList.add('light');
    root.classList.remove('dark');
  }
});
</script>

<template>
  <NConfigProvider :theme="isDarkMode ? 'dark' : null" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <div class="app-container" :class="{ 'dark-mode': isDarkMode }">
        <NLayout has-sider position="absolute">
          <NLayoutSider
            bordered
            collapse-mode="width"
            :collapsed-width="64"
            :width="240"
            :collapsed="collapsed"
            show-trigger
            @collapse="collapsed = true"
            @expand="collapsed = false"
            class="app-sider"
          >
            <div class="logo">
              <h2 v-if="!collapsed">AI {{ t('designInput') }}</h2>
              <h2 v-else>AI</h2>
            </div>
            <NMenu
              :collapsed="collapsed"
              :collapsed-width="64"
              :collapsed-icon-size="22"
              :options="menuOptions"
              :value="activeKey"
              @update:value="handleMenuSelect"
            />
          </NLayoutSider>

          <NLayoutContent class="main-content">
            <!-- 使用 router-view 作為內容容器 -->
            <router-view />
          </NLayoutContent>
        </NLayout>
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* 全局樣式 */
body {
  margin: 0;
  padding: 0;
  font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f5f7fa;
  overflow-x: hidden;
}

/* 深色模式樣式 */
.dark-mode {
  background-color: #111;
  color: #f5f5f7;
}

.app-container {
  width: 100%;
  min-height: 100vh;
  max-width: 100vw;
}

#app {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0;
}

/* 側邊欄樣式 */
.app-sider {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 999;
}

.logo {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 64px;
  padding: 0 16px;
  border-bottom: 1px solid #eee;
  overflow: hidden;
}

.logo h2 {
  margin: 0;
  color: #2080f0;
  white-space: nowrap;
  font-size: 20px;
}

/* 主內容區域 */
.main-content {
  padding-left: 64px;
  transition: padding-left 0.2s;
}

.main-content:has(+ .n-layout-sider:not(.n-layout-sider--collapsed)) {
  padding-left: 240px;
}

/* 使捲軸更美觀 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 全局覆蓋 Naive UI 的容器佈局 */
.n-layout-scroll-container {
  min-height: 100vh;
}

/* 讓按鈕更符合現代設計 */
.n-button {
  border-radius: 6px;
}

/* 深色模式 CSS 變數 */
:root.light {
  --background-color: #f5f7fa;
  --text-color: #2c3e50;
  --border-color: #eee;
}

:root.dark {
  --background-color: #111;
  --text-color: #f5f5f7;
  --border-color: #333;
}
</style>
