<template>
  <div class="design-input-page">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="header-left">
          <NButton @click="goBack" quaternary circle>
            <template #icon>
              <div class="icon-container">&#8592;</div>
            </template>
          </NButton>
          <h1>{{ project ? project.name : '新設計' }}</h1>
        </div>
        <div class="header-right">
          <NButton @click="clearForm">
            清空
          </NButton>
          <NButton type="primary" @click="startGeneration" :loading="loading" :disabled="!isFormValid">
            開始生成
          </NButton>
        </div>
      </div>
    </NLayoutHeader>
    
    <NLayoutContent class="page-content">
      <NSpin :show="loading">
        <NGrid cols="1 l:3" x-gap="24" y-gap="24">
          <NGridItem class="design-form-container" span="1 l:2">
            <NCard title="設計提示詞" class="design-form">
              <NForm
                ref="formRef"
                :model="form"
                :rules="rules"
                label-placement="left"
                label-width="auto"
                require-mark-placement="right-hanging"
              >
                <NFormItem label="提示詞" path="prompt" required>
                  <NInput
                    v-model:value="form.prompt"
                    type="textarea"
                    placeholder="描述你想要的設計，例如：現代簡約風格的客廳，採用白色和木質元素..."
                    :autosize="{ minRows: 5, maxRows: 10 }"
                  />
                </NFormItem>
                
                <NFormItem label="負面提示詞" path="negativePrompt">
                  <NInput
                    v-model:value="form.negativePrompt"
                    type="textarea"
                    placeholder="描述你不想出現在生成結果中的元素，例如：模糊, 畸形, 低質量..."
                    :autosize="{ minRows: 3, maxRows: 5 }"
                  />
                </NFormItem>
                
                <NFormItem label="風格" path="style">
                  <NSelect
                    v-model:value="form.style"
                    :options="styleOptions"
                    placeholder="選擇設計風格"
                    clearable
                  />
                </NFormItem>
                
                <NFormItem label="尺寸" path="size">
                  <NSelect
                    v-model:value="form.size"
                    :options="sizeOptions"
                    placeholder="選擇圖像尺寸"
                  />
                </NFormItem>
                
                <NFormItem label="生成數量" path="count">
                  <NSlider v-model:value="form.count" :min="1" :max="10" :step="1" />
                  <NInputNumber v-model:value="form.count" :min="1" :max="10" size="small" style="margin-left: 12px;"/>
                </NFormItem>
                
                <NFormItem label="提示詞引導強度" path="cfgScale">
                  <NTooltip trigger="hover" placement="top">
                    <template #trigger>
                      <NSlider v-model:value="form.cfgScale" :min="1" :max="20" :step="0.5" />
                    </template>
                    數值越高，AI 生成時會更嚴格地遵循提示詞
                  </NTooltip>
                </NFormItem>
                
                <NFormItem label="迭代步數" path="steps">
                  <NTooltip trigger="hover" placement="top">
                    <template #trigger>
                      <NSlider v-model:value="form.steps" :min="10" :max="150" :step="1" />
                    </template>
                    步數越多，生成結果越精細，但耗時也越長
                  </NTooltip>
                </NFormItem>
                
                <NFormItem label="隨機種子" path="seed">
                  <div class="seed-input">
                    <NInputNumber
                      v-model:value="form.seed"
                      :min="-1"
                      :max="2147483647"
                      style="width: 160px;"
                      :disabled="form.randomizeSeed"
                    />
                    <NCheckbox v-model:checked="form.randomizeSeed">隨機</NCheckbox>
                  </div>
                </NFormItem>
              </NForm>
            </NCard>
          </NGridItem>
          
          <NGridItem class="reference-container">
            <NCard title="參考圖像" class="reference-card">
              <div class="reference-content">
                <div v-if="referenceImages.length === 0" class="empty-reference">
                  <p>沒有參考圖像</p>
                  <NButton @click="openReferenceUpload">上傳參考圖像</NButton>
                </div>
                <div v-else class="reference-images">
                  <div v-for="(image, index) in referenceImages" :key="index" class="reference-image-wrapper">
                    <NImage
                      :src="image"
                      object-fit="contain"
                      width="100%"
                      :alt="'參考圖像 ' + (index + 1)"
                      class="reference-image"
                    />
                    <div class="reference-image-overlay">
                      <NButton circle quaternary type="error" @click="removeReferenceImage(index)" class="remove-button">
                        <template #icon>✕</template>
                      </NButton>
                    </div>
                  </div>
                  <div class="reference-actions">
                    <NButton @click="openReferenceUpload" :disabled="referenceImages.length >= 3">
                      {{ referenceImages.length >= 3 ? '最多 3 張參考圖' : '添加參考圖' }}
                    </NButton>
                    <NButton @click="clearReferenceImages" :disabled="referenceImages.length === 0">
                      清除所有
                    </NButton>
                  </div>
                </div>
                
                <div class="reference-strength" v-if="referenceImages.length > 0">
                  <span>參考強度：{{ form.referenceStrength }}%</span>
                  <NSlider v-model:value="form.referenceStrength" :min="0" :max="100" :step="5" />
                </div>
              </div>
            </NCard>
            
            <NCard title="自訂模型" class="model-card">
              <NSelect
                v-model:value="form.model"
                :options="modelOptions"
                placeholder="選擇生成模型"
              />
              <div class="model-description" v-if="selectedModelDescription">
                {{ selectedModelDescription }}
              </div>
            </NCard>
          </NGridItem>
        </NGrid>
      </NSpin>
    </NLayoutContent>
    
    <NModal v-model:show="showUploadModal" preset="card" title="上傳參考圖像" class="upload-modal">
      <div class="upload-area">
        <NUpload
          ref="uploadRef"
          accept="image/*"
          :default-upload="false"
          :max="1"
          :multiple="false"
          @change="handleUploadChange"
        >
          <div class="upload-trigger">
            <NButton>選擇圖像</NButton>
          </div>
        </NUpload>
        
        <div class="upload-preview" v-if="uploadFile">
          <NImage
            :src="uploadFileUrl"
            object-fit="contain"
            :alt="'預覽圖像'"
            style="max-height: 300px;"
          />
        </div>
      </div>
      
      <template #footer>
        <div class="modal-footer">
          <NButton @click="showUploadModal = false">取消</NButton>
          <NButton type="primary" :disabled="!uploadFile" @click="addReferenceImage">
            添加
          </NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.design-input-page {
  min-height: 100vh;
  width: 100%;
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

.header-right {
  display: flex;
  gap: 12px;
}

.icon-container {
  font-size: 18px;
  line-height: 1;
}

.page-content {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

.design-form-container {
  width: 100%;
}

.design-form {
  height: 100%;
}

.seed-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reference-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reference-card, .model-card {
  width: 100%;
}

.reference-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-reference {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
  color: #909399;
}

.reference-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reference-image-wrapper {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.reference-image {
  width: 100%;
  border-radius: 8px;
}

.reference-image-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
}

.remove-button {
  background-color: rgba(255, 255, 255, 0.7);
  color: #ff4d4f;
}

.reference-actions {
  display: flex;
  gap: 12px;
}

.reference-strength {
  margin-top: 16px;
}

.model-description {
  margin-top: 12px;
  font-size: 14px;
  color: #606266;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-trigger {
  display: flex;
  justify-content: center;
  padding: 24px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
