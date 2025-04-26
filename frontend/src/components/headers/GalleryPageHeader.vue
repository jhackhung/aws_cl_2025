<template>
  <div class="page-header-wrapper">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1>設計畫廊</h1>
          <NTag type="error" size="medium" class="step-tag">
            <template #icon>
              <div class="step-icon">4</div>
            </template>
            品牌設計資料庫
          </NTag>
        </div>
        <div class="header-right">
          <NButton type="primary" size="large" @click="goToCreateImage">
            <template #icon>
              <div class="button-icon">
                <NIcon><PlusOutlined /></NIcon>
              </div>
            </template>
            創建新圖像
          </NButton>
        </div>
      </div>
    </NLayoutHeader>

    <div class="workflow-desc">
      <NAlert type="error" class="workflow-alert">
        <template #icon>
          <div class="info-icon">🏆</div>
        </template>
        <template #header>
          <div class="alert-header">第四步：品牌設計資料庫</div>
        </template>
        在此階段，您可以瀏覽、組織和管理所有完成的設計。添加標籤、分類設計、創建模板，持續累積品牌設計知識，讓您的團隊可以更高效地進行未來專案。
      </NAlert>
    </div>
  </div>
</template>

<script setup>
import { NLayoutHeader, NButton, NTag, NAlert, NIcon } from "naive-ui";
import { PlusOutlined } from "@vicons/antd";

const emit = defineEmits(["go-to-create-image"]);

const goToCreateImage = () => {
  emit("go-to-create-image");
};
</script>

<style scoped>
.page-header-wrapper {
  margin-bottom: 24px;
  width: 100%;
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
  width: 100%;
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
</style>
