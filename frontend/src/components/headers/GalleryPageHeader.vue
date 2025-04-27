<template>
  <div class="page-header-wrapper">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1>專案管理</h1>
          <NTag type="error" size="medium" class="step-tag">
            <template #icon>
              <div class="step-icon">4</div>
            </template>
            專案生成的歷程
          </NTag>
        </div>
        <div class="header-right">
          <NSpace>
            <NButton type="info" size="large" @click="saveAsTemplate">
              <template #icon>
                <NIcon>
                  <SaveOutlined />
                </NIcon>
              </template>
              儲存為模板
            </NButton>
            <NButton type="primary" size="large" @click="goToCreateImage">
              <template #icon>
                <div class="button-icon">
                  <NIcon>
                    <PlusOutlined />
                  </NIcon>
                </div>
              </template>
              創建新圖像
            </NButton>
          </NSpace>
        </div>
      </div>
    </NLayoutHeader>

    <div class="workflow-desc">
      <NAlert type="error" class="workflow-alert">
        <template #icon>
          <div class="info-icon">🏆</div>
        </template>
        <template #header>
          <div class="alert-header">第四步：專案管理歷程</div>
        </template>
        在此階段，您可以瀏覽此專案生成的過往圖片歷程。添加標籤、分類設計、創建模板，讓您的團隊可以更高效地進行未來專案。
      </NAlert>
    </div>
  </div>

  <!-- Add template dialog -->
  <NModal v-model:show="showTemplateDialog" preset="dialog" title="儲存為模板" positive-text="儲存" negative-text="取消"
    @positive-click="confirmSaveTemplate" @negative-click="cancelSaveTemplate">
    <NForm ref="formRef" :model="templateForm" :rules="templateRules">
      <NFormItem label="模板名稱" path="name">
        <NInput v-model:value="templateForm.name" placeholder="請輸入模板名稱" />
      </NFormItem>
      <NFormItem label="模板描述" path="description">
        <NInput v-model:value="templateForm.description" type="textarea" placeholder="請輸入模板描述" />
      </NFormItem>
    </NForm>
  </NModal>
</template>

<script setup>
import { ref } from 'vue';
import { NLayoutHeader, NButton, NTag, NAlert, NIcon, NSpace, NModal, NForm, NFormItem, NInput, useMessage } from "naive-ui";
import { PlusOutlined, SaveOutlined } from "@vicons/antd";
import { useRoute } from 'vue-router';

const route = useRoute();
const message = useMessage();
const emit = defineEmits(['go-to-create-image']);

// Get project ID from route params
const projectId = route.params.projectId;

// Template form state
const showTemplateDialog = ref(false);
const templateForm = ref({
  name: '',
  description: ''
});

const templateRules = {
  name: {
    required: true,
    message: '請輸入模板名稱',
    trigger: ['blur', 'input']
  }
};

// Modified saveAsTemplate to show dialog
const saveAsTemplate = () => {
  showTemplateDialog.value = true;
};

// Handle template save confirmation
const confirmSaveTemplate = async () => {
  try {
    const formData = new FormData();
    formData.append('projectId', projectId);
    formData.append('name', templateForm.value.name);
    formData.append('description', templateForm.value.description);

    const response = await fetch('https://ec2.sausagee.party/template/create', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`API返回錯誤狀態: ${response.status}`);
    }

    const data = await response.json();
    message.success('已成功將專案儲存為模板');
    showTemplateDialog.value = false;

    // Reset form
    templateForm.value = {
      name: '',
      description: ''
    };
  } catch (error) {
    console.error('儲存模板失敗:', error);
    message.error('儲存模板失敗，請稍後再試');
  }
};

// Handle template save cancellation
const cancelSaveTemplate = () => {
  showTemplateDialog.value = false;
  templateForm.value = {
    name: '',
    description: ''
  };
};

const goToCreateImage = () => {
  emit('go-to-create-image');
};
</script>

<style scoped>
.page-header-wrapper {
  margin-bottom: 24px;
  width: 97.5%;
  position: relative;
  z-index: 100;
}

.page-header {
  padding: 16px 24px;
  background-color: #fff !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
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

.button-icon {
  margin-right: 6px;
  display: flex;
  align-items: center;
}

.workflow-desc {
  margin-top: 16px;
  padding: 0 40px;
  width: 94%;
  position: relative;
  z-index: 50;
}

.workflow-alert {
  border-left: 4px solid #d03050;
  background-color: #fff !important;
}

.info-icon {
  font-size: 20px;
}

.alert-header {
  font-weight: 600;
}

/* 深色模式適配 */
:root.dark .page-header {
  background-color: #1e1e1e !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

:root.dark .workflow-alert {
  background-color: #1e1e1e !important;
}

/* Add style for save button */
.n-button.n-button--info-type {
  margin-right: 8px;
}

/* Add styles for template dialog */
:deep(.n-form-item) {
  margin-bottom: 24px;
}

:deep(.n-input) {
  width: 100%;
}

:deep(.n-modal) {
  max-width: 500px;
}
</style>
