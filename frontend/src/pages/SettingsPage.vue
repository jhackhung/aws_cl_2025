<template>
  <div class="settings-container">
    <h1 class="settings-title">{{ t("settings") }}</h1>

    <div class="settings-section">
      <h2>{{ t("languageSettings") }}</h2>
      <div class="setting-item">
        <span class="setting-label">{{ t("selectLanguage") }}</span>
        <NSelect
          v-model:value="currentLang"
          :options="languageOptions"
          @update:value="handleLanguageSelect"
          class="language-select"
        />
      </div>
    </div>

    <div class="settings-section">
      <h2>{{ t("themeSettings") }}</h2>
      <div class="setting-item">
        <span class="setting-label">{{ t("darkMode") }}</span>
        <NSpace align="center">
          <span>🌞</span>
          <NSwitch :value="isDarkMode" @update:value="toggleTheme" />
          <span>🌙</span>
        </NSpace>
      </div>
    </div>

    <div class="settings-section">
      <h2>{{ t("instructions") }}</h2>
      <div class="setting-item">
        <span class="setting-label">{{ t("Go To ") }}</span>
        <NButton type="primary" @click="goToHomepage">
          <template #icon>
            <n-icon><HomeIcon /></n-icon>
          </template>
          {{ t("homePage") }}
        </NButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from "vue";
import { NSelect, NSwitch, NSpace, NButton, NIcon } from "naive-ui";
import { useTranslation } from "../composables/useTranslation";
import { useTheme } from "../composables/useTheme";
import { useSettingsStore } from "../stores/settings";
import { useRouter } from "vue-router";

const router = useRouter();
const { t, currentLanguage } = useTranslation();
const { isDarkMode, toggleTheme } = useTheme();
const settingsStore = useSettingsStore();

const currentLang = computed({
  get: () => currentLanguage.value,
  set: (value) => settingsStore.setLanguage(value),
});

// Home icon component
const HomeIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      strokeWidth: "2",
      strokeLinecap: "round",
      strokeLinejoin: "round",
    },
    [
      h("path", { d: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" }),
      h("polyline", { points: "9 22 9 12 15 12 15 22" }),
    ]
  );

// 語言選項
const languageOptions = [
  {
    label: "中文",
    value: "zh-TW",
  },
  {
    label: "English",
    value: "en-US",
  },
];

// 處理語言選擇
function handleLanguageSelect(value) {
  settingsStore.setLanguage(value);
}

// 返回首頁
function goToHomepage() {
  router.push("/");
}
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-title {
  margin-bottom: 30px;
  font-size: 28px;
}

.settings-section {
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 8px;
  background-color: var(--card-bg-color, #fff);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.settings-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
  color: var(--primary-text-color, #333);
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.setting-label {
  min-width: 150px;
  font-size: 16px;
  color: var(--secondary-text-color, #555);
}

.language-select {
  width: 200px;
}

/* 深色模式樣式調整 */
:root.dark .settings-section {
  background-color: var(--card-bg-color, #252525);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

:root.dark .settings-section h2 {
  color: var(--primary-text-color, #e0e0e0);
}

:root.dark .setting-label {
  color: var(--secondary-text-color, #aaa);
}
</style>
