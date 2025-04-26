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
            <h1>設計修訂</h1>
            <NTag type="warning" size="medium" class="step-tag">
              <template #icon>
                <div class="step-icon">3</div>
              </template>
              設計師精修
            </NTag>
          </div>
          <div class="header-right">
            <NButton @click="saveEdits">
              保存編輯
            </NButton>
            <NButton type="primary" @click="applyInpainting" :loading="inpaintingLoading">
              局部重生成
            </NButton>
          </div>
        </div>
      </NLayoutHeader>
      
      <div class="workflow-desc">
        <NAlert type="warning" class="workflow-alert">
          <template #icon>
            <div class="info-icon">🎨</div>
          </template>
          <template #header>
            <div class="alert-header">第三步：設計師精修</div>
          </template>
          在此階段，您可以手動細修 AI 生成的設計，為其添加創意微調。標記需要修改的區域，調整細節，確保設計符合您的精確要求和品牌標準。
        </NAlert>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  import { NLayoutHeader, NButton, NTag, NAlert } from 'naive-ui';
  
  const props = defineProps({
    inpaintingLoading: Boolean
  });
  
  const emit = defineEmits(['save-edits', 'apply-inpainting']);
  
  const router = useRouter();
  
  const goBack = () => {
    router.push({
      name: 'ai-generate',
      params: { 
        projectId: router.currentRoute.value.params.projectId || 'temp'
      }
    });
  };
  
  const saveEdits = () => {
    emit('save-edits');
  };
  
  const applyInpainting = () => {
    emit('apply-inpainting');
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
    border-left: 4px solid #f0a020;
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