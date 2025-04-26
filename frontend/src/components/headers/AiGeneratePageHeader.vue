<template>
    <div class="page-header-wrapper">
      <NLayoutHeader class="page-header">
        <div class="header-content">
          <div class="header-left">
            <NButton @click="goBack" quaternary circle>
              <template #icon>
                <div class="icon-container">&#8592;</div>
              </template>
            </NButton>
            <h1>AI 生成結果</h1>
            <NTag type="success" size="medium" class="step-tag">
              <template #icon>
                <div class="step-icon">2</div>
              </template>
              AI 生成設計
            </NTag>
          </div>
          <div class="header-right">
            <NButton @click="regenerate" :loading="loading" :disabled="selectedImages.length === 0">
              重新生成選中項
            </NButton>
            <NButton type="primary" @click="saveAndContinue" :disabled="!hasSelectedImages">
              保存並繼續
            </NButton>
          </div>
        </div>
      </NLayoutHeader>
      
      <div class="workflow-desc">
        <NAlert type="success" class="workflow-alert">
          <template #icon>
            <div class="info-icon">🚀</div>
          </template>
          <template #header>
            <div class="alert-header">第二步：AI 生成設計</div>
          </template>
          在此階段，AI 會基於您提供的參數和構想快速生成多個概念設計。您可以選擇喜歡的設計並進行後續編輯，或調整參數重新生成。
        </NAlert>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  import { NLayoutHeader, NButton, NTag, NAlert } from 'naive-ui';
  
  const props = defineProps({
    loading: Boolean,
    selectedImages: {
      type: Array,
      default: () => []
    },
    hasSelectedImages: Boolean
  });
  
  const emit = defineEmits(['regenerate', 'save-and-continue']);
  
  const router = useRouter();
  
  const goBack = () => {
    router.push({ 
      name: 'design-input',
      params: { projectId: router.currentRoute.value.params.projectId || 'temp' }
    });
  };
  
  const regenerate = () => {
    emit('regenerate');
  };
  
  const saveAndContinue = () => {
    emit('save-and-continue');
  };
  </script>
  
  <style scoped>
  .page-header-wrapper {
    margin-bottom: 24px;
  }
  
  .page-header {
    padding: 16px 24px;
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
    width: 100%;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0 16px;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .header-left h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
  }
  
  .step-tag {
    font-weight: 500;
    display: flex;
    align-items: center;
  }
  
  .step-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: currentColor;
    color: white;
    font-weight: bold;
    margin-right: 4px;
  }
  
  .header-right {
    display: flex;
    gap: 12px;
  }
  
  .icon-container {
    font-size: 18px;
    line-height: 1;
  }
  
  .workflow-desc {
    margin-top: 16px;
    padding: 0 40px;
  }
  
  .workflow-alert {
    border-left: 4px solid #18a058;
  }
  
  .info-icon {
    font-size: 20px;
  }
  
  .alert-header {
    font-weight: 600;
  }
  
  /* 深色模式適配 */
  :root.dark .page-header {
    background-color: #1e1e1e;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
  </style>