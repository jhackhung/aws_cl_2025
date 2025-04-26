import { computed } from 'vue';
import { useSettingsStore } from '../stores/settings';
import translations, { supportedLanguages } from '../locales';

export function useTranslation() {
  const settingsStore = useSettingsStore();
  
  const currentLanguage = computed(() => settingsStore.language);
  
  const setLanguage = (lang) => {
    if (Object.keys(translations).includes(lang)) {
      settingsStore.setLanguage(lang);
    }
  };
  
  // 獲取翻譯文本
  const t = (key) => {
    const lang = currentLanguage.value;
    // 如果找不到目前語言的翻譯，回傳 key 本身
    return translations[lang]?.[key] || translations['zh-TW']?.[key] || key;
  };
  
  return {
    t,
    currentLanguage,
    setLanguage,
    supportedLanguages
  };
}