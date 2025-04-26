import { computed } from 'vue';
import { useSettingsStore } from '../stores/settings';
import { darkTheme, lightTheme } from 'naive-ui';

export function useTheme() {
  const settingsStore = useSettingsStore();
  
  const isDarkMode = computed(() => settingsStore.isDarkMode);
  
  const toggleTheme = () => {
    settingsStore.toggleTheme();
  };
  
  // 提供當前主題對象 (Naive UI 使用)
  const currentTheme = computed(() => {
    return isDarkMode.value ? darkTheme : lightTheme;
  });
  
  // 自定義主題覆蓋
  const themeOverrides = computed(() => ({
    common: {
      primaryColor: "#2080f0",
      primaryColorHover: "#4098fc",
      primaryColorPressed: "#1060c9",
      borderRadius: "6px",
    },
    Button: {
      textColor: isDarkMode.value ? "#fff" : undefined,
    },
    Card: {
      borderRadius: "8px",
    },
    Menu: {
      borderRadius: "6px",
    }
  }));
  
  return {
    isDarkMode,
    toggleTheme,
    currentTheme,
    themeOverrides,
    setDarkMode: settingsStore.setDarkMode
  };
}