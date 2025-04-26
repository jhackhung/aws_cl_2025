<template>
  <n-config-provider :theme="currentTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <AppLayout />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { NConfigProvider, NMessageProvider } from 'naive-ui';
import { useTheme } from './composables/useTheme';
import AppLayout from './components/AppLayout.vue';

const { currentTheme, themeOverrides } = useTheme();
</script>

<style>
/* 全局樣式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

:root {
  --primary-color: #2080f0;
  --primary-color-hover: #4098fc;
  --primary-color-pressed: #1060c9;
  --text-color: #333;
  --secondary-text-color: #666;
  --bg-color: #f5f7fa;
  --card-bg-color: #fff;
  --border-color: #eaeaea;
}

:root.dark {
  --text-color: #e0e0e0;
  --secondary-text-color: #aaa;
  --bg-color: #121212;
  --card-bg-color: #1f1f1f;
  --border-color: #333;
}

body {
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* 避免藍色選擇高亮色 */
:focus {
  outline: none;
}

/* 改進滾動條樣式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

:root.dark ::-webkit-scrollbar-thumb {
  background: #555;
}

::-webkit-scrollbar-thumb:hover {
  background: #aaa;
}

:root.dark ::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style>