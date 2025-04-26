<template>
    <div class="template-detail-page">
      <NLayoutHeader class="page-header">
        <div class="header-content">
          <div class="header-left">
            <NButton @click="goBack" quaternary circle>
              <template #icon>
                <div class="icon-container">
                  <NIcon><ArrowLeftOutlined /></NIcon>
                </div>
              </template>
            </NButton>
            <h1>模板詳情</h1>
          </div>
          <div class="header-right">
            <NSpace>
              <NButton @click="editTemplate" v-if="isAdmin">
                <template #icon>
                  <div class="button-icon">
                    <NIcon><EditOutlined /></NIcon>
                  </div>
                </template>
                編輯模板
              </NButton>
              <NButton type="primary" @click="useTemplate">
                <template #icon>
                  <div class="button-icon">
                    <NIcon><CheckOutlined /></NIcon>
                  </div>
                </template>
                使用此模板
              </NButton>
            </NSpace>
          </div>
        </div>
      </NLayoutHeader>
  
      <NLayoutContent class="page-content">
        <NSpin :show="loading">
          <div class="content-wrapper" v-if="template">
            <NGrid cols="1 m:3" x-gap="24" y-gap="24">
              <NGridItem span="1 m:2">
                <div class="template-main">
                  <NCard class="template-info-card">
                    <div class="template-header">
                      <h2>{{ template.name }}</h2>
                      <div class="template-badges" v-if="template.featured || template.isNew">
                        <NTag type="primary" v-if="template.featured">精選</NTag>
                        <NTag type="success" v-if="template.isNew">新增</NTag>
                      </div>
                    </div>
                    
                    <p class="template-desc">{{ template.description }}</p>
                    
                    <div class="template-meta">
                      <div class="meta-item">
                        <span class="meta-label">類別</span>
                        <NTag>{{ getCategoryName(template.category) }}</NTag>
                      </div>
                      
                      <div class="meta-item">
                        <span class="meta-label">創建時間</span>
                        <span>{{ formatDate(template.createdAt) }}</span>
                      </div>
                      
                      <div class="meta-item">
                        <span class="meta-label">標籤</span>
                        <div class="tags-list">
                          <NTag 
                            v-for="tag in template.tags" 
                            :key="tag"
                            type="info"
                            size="small"
                          >
                            {{ tag }}
                          </NTag>
                        </div>
                      </div>
                    </div>
                  </NCard>
                  
                  <NCard title="設計參數" class="parameters-card">
                    <div class="parameter-list">
                      <div class="parameter-item" v-if="template.params?.style">
                        <span class="param-label">風格</span>
                        <span class="param-value">{{ getStyleName(template.params.style) }}</span>
                      </div>
                      
                      <div class="parameter-item" v-if="template.params?.size">
                        <span class="param-label">尺寸</span>
                        <span class="param-value">{{ template.params.size }}</span>
                      </div>
                      
                      <div class="parameter-item" v-if="template.params?.steps">
                        <span class="param-label">迭代步數</span>
                        <span class="param-value">{{ template.params.steps }}</span>
                      </div>
                      
                      <div class="parameter-item" v-if="template.params?.cfgScale">
                        <span class="param-label">引導強度</span>
                        <span class="param-value">{{ template.params.cfgScale }}</span>
                      </div>
                      
                      <div class="parameter-item" v-if="template.params?.prompt">
                        <div class="param-label">提示詞</div>
                        <div class="param-value prompt-text">{{ template.params.prompt }}</div>
                      </div>
                      
                      <div class="parameter-item" v-if="template.params?.negativePrompt">
                        <div class="param-label">負面提示詞</div>
                        <div class="param-value prompt-text">{{ template.params.negativePrompt }}</div>
                      </div>
                    </div>
                  </NCard>
                  
                  <NCard title="相關圖像" v-if="template.relatedImages?.length" class="related-images-card">
                    <NCarousel show-arrow autoplay class="carousel" v-model:current-index="currentSlideIndex">
                      <NCarouselItem 
                        v-for="(image, index) in template.relatedImages" 
                        :key="index"
                      >
                        <div class="carousel-item">
                          <NImage
                            :src="image.url"
                            object-fit="contain"
                            :alt="`相關圖像 ${index + 1}`"
                          />
                        </div>
                      </NCarouselItem>
                    </NCarousel>
                    
                    <div class="image-thumbnails">
                      <div 
                        v-for="(image, index) in template.relatedImages" 
                        :key="index"
                        class="image-thumbnail"
                        :class="{ active: currentSlideIndex === index }"
                        @click="currentSlideIndex = index"
                      >
                        <NImage
                          :src="image.url"
                          object-fit="cover"
                          :alt="`縮圖 ${index + 1}`"
                        />
                      </div>
                    </div>
                  </NCard>
                </div>
              </NGridItem>
              
              <NGridItem span="1">
                <div class="template-sidebar">
                  <NCard class="preview-card">
                    <div class="preview-image">
                      <NImage
                        :src="template.thumbnail"
                        object-fit="contain"
                        :alt="template.name"
                        class="template-thumbnail"
                      />
                    </div>
                    
                    <NButton block type="primary" @click="useTemplate" class="use-template-btn">
                      使用此模板
                    </NButton>
                  </NCard>
                  
                  <NCard title="相似模板" class="similar-templates-card">
                    <div v-if="similarTemplates.length" class="similar-templates">
                      <div 
                        v-for="item in similarTemplates" 
                        :key="item.id"
                        class="similar-template-item"
                        @click="viewTemplate(item.id)"
                      >
                        <div class="similar-template-thumb">
                          <NImage
                            :src="item.thumbnail"
                            object-fit="cover"
                            :alt="item.name"
                          />
                        </div>
                        <div class="similar-template-info">
                          <span class="similar-template-name">{{ item.name }}</span>
                          <div class="similar-template-tags">
                            <NTag 
                              v-for="tag in item.tags.slice(0, 1)" 
                              :key="tag"
                              size="small"
                              :bordered="false"
                            >
                              {{ tag }}
                            </NTag>
                          </div>
                        </div>
                      </div>
                    </div>
                    <NEmpty v-else description="沒有相似模板" />
                  </NCard>
                </div>
              </NGridItem>
            </NGrid>
          </div>
          
          <NResult
            v-else-if="!loading"
            status="404"
            title="模板未找到"
            description="您請求的模板不存在或已被刪除"
          >
            <template #footer>
              <NButton @click="goToTemplateLibrary">返回模板庫</NButton>
            </template>
          </NResult>
        </NSpin>
      </NLayoutContent>
      
      <!-- 編輯模板對話框 -->
      <NModal
        v-model:show="showEditModal"
        preset="card"
        title="編輯模板"
        style="width: 80%; max-width: 600px"
      >
        <NForm
          ref="editFormRef"
          :model="editForm"
          :rules="formRules"
          label-placement="left"
          label-width="100"
        >
          <NFormItem label="模板名稱" path="name" required>
            <NInput
              v-model:value="editForm.name"
              placeholder="請輸入模板名稱"
              clearable
            />
          </NFormItem>
          
          <NFormItem label="模板描述" path="description">
            <NInput
              v-model:value="editForm.description"
              type="textarea"
              placeholder="請輸入模板描述"
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </NFormItem>
          
          <NFormItem label="分類" path="category">
            <NSelect
              v-model:value="editForm.category"
              :options="categoryOptions"
              placeholder="選擇類別"
            />
          </NFormItem>
          
          <NFormItem label="標籤">
            <div v-if="isAddingTag" class="tag-input-area">
              <NInput
                v-model:value="newTagName"
                placeholder="輸入標籤名稱"
                @keydown.enter.prevent="addTagToTemplate"
              />
              <NButton type="primary" size="small" @click="addTagToTemplate">添加</NButton>
              <NButton size="small" @click="isAddingTag = false">取消</NButton>
            </div>
            <div v-else class="tags-area">
              <div class="tags-display">
                <NTag
                  v-for="tag in editForm.tags"
                  :key="tag"
                  type="info"
                  closable
                  @close="removeTagFromTemplate(tag)"
                >
                  {{ tag }}
                </NTag>
                <NButton
                  size="small"
                  class="add-tag-btn"
                  @click="isAddingTag = true"
                >
                  <NIcon class="tag-icon"><PlusOutlined /></NIcon>
                  添加標籤
                </NButton>
              </div>
            </div>
          </NFormItem>
          
          <NFormItem label="精選模板">
            <NSwitch v-model:value="editForm.featured" />
            <span class="setting-desc">設為精選模板（顯示在首頁）</span>
          </NFormItem>
        </NForm>
        
        <template #footer>
          <div class="modal-footer">
            <NButton @click="showEditModal = false">取消</NButton>
            <NButton type="error" @click="confirmDeleteTemplate" class="delete-btn">
              刪除模板
            </NButton>
            <NButton
              type="primary"
              :loading="saving"
              @click="saveTemplate"
            >
              保存
            </NButton>
          </div>
        </template>
      </NModal>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useTemplateStore } from '../stores/template';
  import { useMessage, useDialog } from 'naive-ui';
  import {
    NLayout,
    NLayoutHeader,
    NLayoutContent,
    NButton,
    NGrid,
    NGridItem,
    NSpin,
    NCard,
    NTag,
    NImage,
    NIcon,
    NSpace,
    NEmpty,
    NResult,
    NCarousel,
    NCarouselItem,
    NModal,
    NForm,
    NFormItem,
    NInput,
    NSelect,
    NSwitch,
  } from 'naive-ui';
  import {
    ArrowLeftOutlined,
    CheckOutlined,
    EditOutlined,
    PlusOutlined,
  } from '@vicons/antd';
  
  const route = useRoute();
  const router = useRouter();
  const templateStore = useTemplateStore();
  const message = useMessage();
  const dialog = useDialog();
  
  // 頁面狀態
  const loading = ref(false);
  const templateId = computed(() => route.params.id);
  const template = ref(null);
  const similarTemplates = ref([]);
  const currentSlideIndex = ref(0);
  const showEditModal = ref(false);
  const saving = ref(false);
  const isAddingTag = ref(false);
  const newTagName = ref('');
  const isAdmin = ref(true); // 模擬管理員權限，實際應從用戶權限中獲取
  
  // 編輯表單
  const editForm = ref({
    name: '',
    description: '',
    category: '',
    tags: [],
    featured: false
  });
  
  // 表單驗證規則
  const formRules = {
    name: {
      required: true,
      message: '模板名稱不能為空',
      trigger: ['blur', 'input']
    }
  };
  
  // 類別選項
  const categoryOptions = [
    { label: '平面設計', value: 'graphic' },
    { label: '室內設計', value: 'interior' },
    { label: '產品設計', value: 'product' },
    { label: '包裝設計', value: 'package' },
    { label: '品牌識別', value: 'branding' },
    { label: '網頁設計', value: 'web' },
    { label: '其他', value: 'other' }
  ];
  
  // 初始載入數據
  onMounted(async () => {
    if (!templateId.value) {
      return;
    }
  
    loading.value = true;
    try {
      // 載入模板庫
      await templateStore.fetchTemplates();
      
      // 獲取模板詳情
      const templateData = templateStore.getTemplateById(templateId.value);
      
      if (templateData) {
        template.value = templateData;
        
        // 找出相似模板（相同類別或有共同標籤的模板）
        findSimilarTemplates();
        
        // 初始化編輯表單
        editForm.value = {
          name: templateData.name,
          description: templateData.description || '',
          category: templateData.category || '',
          tags: [...(templateData.tags || [])],
          featured: templateData.featured || false
        };
      }
    } catch (error) {
      console.error('載入模板詳情失敗:', error);
      message.error('載入模板詳情失敗，請稍後再試');
    } finally {
      loading.value = false;
    }
  });
  
  // 獲取類別名稱
  const getCategoryName = (categoryValue) => {
    const category = categoryOptions.find(cat => cat.value === categoryValue);
    return category ? category.label : categoryValue || '未分類';
  };
  
  // 獲取風格名稱
  const getStyleName = (styleValue) => {
    if (!styleValue) return '未設定';
    
    const styleOptions = [
      { label: '現代簡約', value: 'modern_minimalist' },
      { label: '復古懷舊', value: 'retro_vintage' },
      { label: '自然有機', value: 'natural_organic' },
      { label: '科技未來', value: 'tech_futuristic' },
      { label: '工業風格', value: 'industrial' },
      { label: '北歐風格', value: 'scandinavian' },
      { label: '熱帶度假', value: 'tropical_resort' }
    ];
    
    const found = styleOptions.find((option) => option.value === styleValue);
    return found ? found.label : styleValue;
  };
  
  // 格式化日期
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  // 返回上一頁
  const goBack = () => {
    router.back();
  };
  
  // 前往模板庫
  const goToTemplateLibrary = () => {
    router.push({ name: 'templates' });
  };
  
  // 使用此模板
  const useTemplate = () => {
    if (!template.value) return;
    
    // 記錄最近使用
    templateStore.addRecentlyUsedTemplate(template.value.id);
    
    // 導航到設計輸入頁面，使用所選模板
    router.push({
      name: 'design-input',
      query: { templateId: template.value.id }
    });
    
    message.success(`已選擇模板：${template.value.name}`);
  };
  
  // 檢視模板詳情
  const viewTemplate = (id) => {
    router.push({
      name: 'template-detail',
      params: { id }
    });
  };
  
  // 編輯模板
  const editTemplate = () => {
    if (!isAdmin.value) {
      message.warning('您沒有編輯權限');
      return;
    }
    
    showEditModal.value = true;
  };
  
  // 添加標籤到模板
  const addTagToTemplate = () => {
    if (!newTagName.value.trim()) return;
    
    if (!editForm.value.tags.includes(newTagName.value.trim())) {
      editForm.value.tags.push(newTagName.value.trim());
    }
    
    newTagName.value = '';
    isAddingTag.value = false;
  };
  
  // 從模板移除標籤
  const removeTagFromTemplate = (tag) => {
    const index = editForm.value.tags.indexOf(tag);
    if (index !== -1) {
      editForm.value.tags.splice(index, 1);
    }
  };
  
  // 保存模板
  const saveTemplate = async () => {
    saving.value = true;
    try {
      // 更新模板
      await templateStore.updateTemplate(templateId.value, {
        name: editForm.value.name,
        description: editForm.value.description,
        category: editForm.value.category,
        tags: editForm.value.tags,
        featured: editForm.value.featured
      });
      
      // 更新當前頁面的模板數據
      template.value = templateStore.getTemplateById(templateId.value);
      
      message.success('模板已更新');
      showEditModal.value = false;
    } catch (error) {
      console.error('更新模板失敗:', error);
      message.error('更新模板失敗，請稍後再試');
    } finally {
      saving.value = false;
    }
  };
  
  // 確認刪除模板
  const confirmDeleteTemplate = () => {
    dialog.warning({
      title: '確認刪除',
      content: '確定要刪除此模板嗎？此操作無法撤銷。',
      positiveText: '確定刪除',
      negativeText: '取消',
      onPositiveClick: deleteTemplate
    });
  };
  
  // 刪除模板
  const deleteTemplate = async () => {
    saving.value = true;
    try {
      await templateStore.deleteTemplate(templateId.value);
      
      message.success('模板已刪除');
      router.push({ name: 'templates' });
    } catch (error) {
      console.error('刪除模板失敗:', error);
      message.error('刪除模板失敗，請稍後再試');
    } finally {
      saving.value = false;
    }
  };
  
  // 查找相似模板
  const findSimilarTemplates = () => {
    if (!template.value) return;
    
    // 獲取所有模板，除了當前模板
    const allTemplates = templateStore.templates.filter(t => t.id !== template.value.id);
    
    // 計算相似度分數
    const scoredTemplates = allTemplates.map(t => {
      let score = 0;
      
      // 相同類別加分
      if (t.category === template.value.category) {
        score += 3;
      }
      
      // 共同標籤加分
      if (t.tags && template.value.tags) {
        const commonTags = t.tags.filter(tag => template.value.tags.includes(tag));
        score += commonTags.length * 2;
      }
      
      return { ...t, similarityScore: score };
    });
    
    // 按相似度排序，取前5個
    similarTemplates.value = scoredTemplates
      .filter(t => t.similarityScore > 0)
      .sort((a, b) => b.similarityScore - a.similarityScore)
      .slice(0, 5);
  };
  </script>
  
  <style scoped>
.template-detail-page {
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-color, #f5f7fa);
}

.page-header {
  padding: 16px 24px;
  background-color: var(--card-bg-color, #fff);
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
  max-width: 1400px;
  margin: 0 auto;
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

.icon-container {
  font-size: 18px;
}

.button-icon {
  margin-right: 6px;
  display: flex;
  align-items: center;
}

.page-content {
  padding: 32px 0;
  width: 100%;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.template-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.template-info-card,
.parameters-card,
.related-images-card,
.preview-card,
.similar-templates-card {
  background-color: var(--card-bg-color, #fff);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.template-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.template-badges {
  display: flex;
  gap: 8px;
}

.template-desc {
  margin: 0 0 24px 0;
  font-size: 16px;
  line-height: 1.6;
  color: var(--secondary-text-color, #666);
}

.template-meta {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.meta-label {
  min-width: 80px;
  font-weight: 500;
  color: var(--secondary-text-color, #666);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.parameter-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--border-color, #eaeaea);
}

.parameter-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.param-label {
  font-weight: 500;
  color: var(--secondary-text-color, #666);
}

.prompt-text {
  white-space: pre-wrap;
  background-color: var(--bg-color, #f5f7fa);
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  line-height: 1.5;
}

.carousel {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.carousel-item {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-color, #f5f7fa);
}

.image-thumbnails {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.image-thumbnail {
  flex: 0 0 auto;
  width: 80px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.image-thumbnail:hover {
  border-color: var(--primary-color, #2080f0);
}

.image-thumbnail.active {
  border-color: var(--primary-color, #2080f0);
}

.template-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.preview-image {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
  background-color: var(--bg-color, #f5f7fa);
  border-radius: 8px;
  overflow: hidden;
  height: 250px;
}

.template-thumbnail {
  max-height: 250px;
  max-width: 100%;
  object-fit: contain;
}

.use-template-btn {
  margin-top: 16px;
}

.similar-templates {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.similar-template-item {
  display: flex;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.similar-template-item:hover {
  background-color: var(--bg-color, #f5f7fa);
}

.similar-template-thumb {
  flex: 0 0 auto;
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
}

.similar-template-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.similar-template-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-input-area {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.add-tag-btn {
  display: flex;
  align-items: center;
}

.tag-icon {
  margin-right: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.delete-btn {
  margin-right: auto;
}

.setting-desc {
  margin-left: 12px;
  font-size: 14px;
  color: var(--secondary-text-color, #666);
}

/* 深色模式適配 */
:root.dark .template-info-card,
:root.dark .parameters-card,
:root.dark .related-images-card,
:root.dark .preview-card,
:root.dark .similar-templates-card {
  background-color: var(--card-bg-color, #1f1f1f);
}

:root.dark .template-desc,
:root.dark .meta-label,
:root.dark .param-label,
:root.dark .setting-desc {
  color: var(--secondary-text-color, #aaa);
}

:root.dark .prompt-text {
  background-color: #2a2a2a;
}

:root.dark .similar-template-item:hover {
  background-color: #2a2a2a;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-left {
    width: 100%;
  }
  
  .header-right {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
  
  .content-wrapper {
    padding: 0 16px;
  }
  
  .carousel-item {
    height: 200px;
  }
}
</style>