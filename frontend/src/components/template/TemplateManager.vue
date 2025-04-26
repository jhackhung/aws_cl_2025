<template>
    <div class="template-manager">
      <NCard title="模板庫" class="template-card">
        <template #header-extra>
          <NButton @click="showSaveTemplateModal = true" v-if="currentProject">
            <template #icon>
              <div class="button-icon">
                <NIcon><SaveOutlined /></NIcon>
              </div>
            </template>
            保存為模板
          </NButton>
        </template>
        
        <div class="filter-section">
          <NInput
            v-model:value="searchQuery"
            placeholder="搜尋模板..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <NIcon><SearchOutlined /></NIcon>
            </template>
          </NInput>
          
          <div class="filter-controls">
            <div class="tags-container">
              <span class="filter-label">標籤篩選：</span>
              <TagSelector
                v-if="availableTags.length"
                :tags="availableTags"
                v-model:selected="selectedTags"
              />
              <span v-else class="no-tags">暫無標籤</span>
            </div>
            
            <div class="category-container">
              <span class="filter-label">分類：</span>
              <NSelect
                v-model:value="selectedCategory"
                :options="categoryOptions"
                placeholder="選擇類別"
                clearable
                class="category-select"
              />
            </div>
          </div>
        </div>
        
        <NSpin :show="loading">
          <div v-if="filteredTemplates.length" class="templates-grid">
            <NGrid cols="1 s:2 m:3 l:4" x-gap="16" y-gap="16">
              <NGridItem v-for="template in filteredTemplates" :key="template.id">
                <div 
                  class="template-item" 
                  :class="{ 'is-featured': template.featured }"
                  @click="selectTemplate(template)"
                >
                  <div class="template-thumbnail">
                    <NImage
                      :src="template.thumbnail"
                      object-fit="cover"
                      fallback-src="/placeholder-image.png"
                      :alt="template.name"
                    />
                    <div class="template-badges" v-if="template.featured || template.isNew">
                      <span class="badge featured" v-if="template.featured">精選</span>
                      <span class="badge new" v-if="template.isNew">新增</span>
                    </div>
                  </div>
                  <div class="template-info">
                    <h3>{{ template.name }}</h3>
                    <p>{{ template.description }}</p>
                    <div class="template-meta">
                      <div class="template-tags">
                        <NTag 
                          v-for="tag in template.tags.slice(0, 2)" 
                          :key="tag" 
                          size="small"
                          :bordered="false"
                        >
                          {{ tag }}
                        </NTag>
                        <span v-if="template.tags.length > 2" class="more-tags">+{{ template.tags.length - 2 }}</span>
                      </div>
                      <span class="template-date">{{ formatDate(template.createdAt) }}</span>
                    </div>
                  </div>
                </div>
              </NGridItem>
            </NGrid>
            
            <div v-if="totalPages > 1" class="pagination-container">
              <NPagination
                v-model:page="currentPage"
                :page-count="totalPages"
                :page-size="pageSize"
                :item-count="filteredTemplates.length"
                show-size-picker
                :page-sizes="[8, 12, 20, 32]"
                @update:page-size="onPageSizeChange"
              />
            </div>
          </div>
          
          <NEmpty v-else description="沒有找到符合條件的模板" />
        </NSpin>
      </NCard>
      
      <!-- 模板詳情對話框 -->
      <NModal
        v-model:show="showTemplateDetailModal"
        preset="card"
        title="模板詳情"
        style="width: 90%; max-width: 1200px"
      >
        <div class="template-detail-content" v-if="selectedTemplateDetail">
          <NGrid cols="1 m:2" x-gap="24" y-gap="24">
            <NGridItem>
              <div class="template-preview-container">
                <NImage
                  :src="selectedTemplateDetail.thumbnail"
                  object-fit="contain"
                  :alt="selectedTemplateDetail.name"
                  class="detail-image"
                />
              </div>
            </NGridItem>
            <NGridItem>
              <div class="template-details">
                <h2>{{ selectedTemplateDetail.name }}</h2>
                <p class="template-description">{{ selectedTemplateDetail.description }}</p>
                
                <div class="detail-section">
                  <h3>設計參數</h3>
                  <div class="parameter-list">
                    <div class="parameter-item" v-if="selectedTemplateDetail.params?.style">
                      <span class="param-label">風格</span>
                      <span class="param-value">{{ getStyleName(selectedTemplateDetail.params.style) }}</span>
                    </div>
                    
                    <div class="parameter-item" v-if="selectedTemplateDetail.params?.size">
                      <span class="param-label">尺寸</span>
                      <span class="param-value">{{ selectedTemplateDetail.params.size }}</span>
                    </div>
                    
                    <div class="parameter-item" v-if="selectedTemplateDetail.params?.prompt">
                      <span class="param-label">提示詞</span>
                      <p class="param-value prompt-text">{{ selectedTemplateDetail.params.prompt }}</p>
                    </div>
                  </div>
                </div>
                
                <div class="detail-section">
                  <h3>標籤</h3>
                  <div class="tags-list">
                    <NTag
                      v-for="tag in selectedTemplateDetail.tags"
                      :key="tag"
                      type="info"
                      class="detail-tag"
                    >
                      {{ tag }}
                    </NTag>
                  </div>
                </div>
                
                <div class="detail-section">
                  <h3>相關圖像</h3>
                  <div class="related-images" v-if="selectedTemplateDetail.relatedImages?.length">
                    <NCarousel show-arrow autoplay>
                      <NCarouselItem 
                        v-for="(image, index) in selectedTemplateDetail.relatedImages" 
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
                  </div>
                  <NEmpty v-else description="沒有相關圖像" />
                </div>
              </div>
            </NGridItem>
          </NGrid>
        </div>
        
        <template #footer>
          <div class="modal-footer">
            <NButton @click="showTemplateDetailModal = false">關閉</NButton>
            <NButton type="primary" @click="useTemplate">使用此模板</NButton>
          </div>
        </template>
      </NModal>
      
      <!-- 保存為模板對話框 -->
      <NModal
        v-model:show="showSaveTemplateModal"
        preset="card"
        title="保存為模板"
        style="width: 80%; max-width: 600px"
      >
        <NForm
          ref="saveTemplateFormRef"
          :model="newTemplate"
          :rules="templateFormRules"
          label-placement="left"
          label-width="100"
        >
          <NFormItem label="模板名稱" path="name" required>
            <NInput
              v-model:value="newTemplate.name"
              placeholder="請輸入模板名稱"
              clearable
            />
          </NFormItem>
          
          <NFormItem label="模板描述" path="description">
            <NInput
              v-model:value="newTemplate.description"
              type="textarea"
              placeholder="請輸入模板描述"
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </NFormItem>
          
          <NFormItem label="分類" path="category">
            <NSelect
              v-model:value="newTemplate.category"
              :options="categoryOptions"
              placeholder="選擇類別"
            />
          </NFormItem>
          
          <NFormItem label="標籤">
            <div v-if="isAddingTag" class="tag-input-area">
              <NInput
                v-model:value="newTagName"
                placeholder="輸入標籤名稱"
                @keydown.enter.prevent="addNewTag"
              />
              <NButton type="primary" size="small" @click="addNewTag">添加</NButton>
              <NButton size="small" @click="isAddingTag = false">取消</NButton>
            </div>
            <div v-else class="tags-area">
              <div class="tags-display">
                <NTag
                  v-for="tag in newTemplate.tags"
                  :key="tag"
                  type="info"
                  closable
                  @close="removeTag(tag)"
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
          
          <NFormItem label="包含圖像">
            <NSwitch v-model:value="newTemplate.includeImages" />
            <span class="setting-desc">包含此專案的生成圖像作為模板參考</span>
          </NFormItem>
          
          <NFormItem label="縮圖">
            <NUpload
              ref="uploadRef"
              accept="image/*"
              :default-upload="false"
              :max="1"
              :multiple="false"
              @change="handleUploadChange"
            >
              <NButton>選擇縮圖</NButton>
            </NUpload>
            <div class="thumbnail-preview" v-if="uploadFileUrl">
              <NImage
                :src="uploadFileUrl"
                object-fit="contain"
                :alt="'縮圖預覽'"
                style="max-height: 150px"
              />
            </div>
          </NFormItem>
        </NForm>
        
        <template #footer>
          <div class="modal-footer">
            <NButton @click="showSaveTemplateModal = false">取消</NButton>
            <NButton
              type="primary"
              :disabled="!newTemplate.name"
              :loading="savingTemplate"
              @click="saveAsTemplate"
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
  import { useRouter } from 'vue-router';
  import { useProjectStore } from '../stores/project';
  import { useImageStore } from '../stores/image';
  import { useTemplateStore } from '../stores/template';
  import { useMessage } from 'naive-ui';
  import {
    NCard,
    NButton,
    NGrid,
    NGridItem,
    NImage,
    NSpin,
    NEmpty,
    NModal,
    NForm,
    NFormItem,
    NInput,
    NTag,
    NIcon,
    NSelect,
    NPagination,
    NSwitch,
    NUpload,
    NCarousel,
    NCarouselItem
  } from 'naive-ui';
  import {
    PlusOutlined,
    SearchOutlined,
    SaveOutlined
  } from '@vicons/antd';
  import TagSelector from '../components/ui/TagSelector.vue';
  
  const router = useRouter();
  const projectStore = useProjectStore();
  const imageStore = useImageStore();
  const templateStore = useTemplateStore();
  const message = useMessage();
  
  // 頁面狀態
  const loading = ref(false);
  const searchQuery = ref('');
  const selectedTags = ref([]);
  const selectedCategory = ref(null);
  const currentPage = ref(1);
  const pageSize = ref(12);
  const showTemplateDetailModal = ref(false);
  const showSaveTemplateModal = ref(false);
  const selectedTemplateDetail = ref(null);
  const savingTemplate = ref(false);
  const isAddingTag = ref(false);
  const newTagName = ref('');
  const saveTemplateFormRef = ref(null);
  const uploadRef = ref(null);
  const uploadFile = ref(null);
  const uploadFileUrl = ref('');
  
  // 当前项目
  const currentProject = computed(() => projectStore.currentProject);
  
  // 新模板数据
  const newTemplate = ref({
    name: '',
    description: '',
    category: '',
    tags: [],
    includeImages: true,
    thumbnail: null
  });
  
  // 模板表单验证规则
  const templateFormRules = {
    name: {
      required: true,
      message: '模板名稱不能為空',
      trigger: ['blur', 'input']
    }
  };
  
  // 类别选项
  const categoryOptions = [
    { label: '平面設計', value: 'graphic' },
    { label: '室內設計', value: 'interior' },
    { label: '產品設計', value: 'product' },
    { label: '包裝設計', value: 'package' },
    { label: '品牌識別', value: 'branding' },
    { label: '網頁設計', value: 'web' },
    { label: '其他', value: 'other' }
  ];
  
  // 计算所有可用的标签
  const availableTags = computed(() => {
    const tagsSet = new Set();
    templateStore.templates.forEach((template) => {
      template.tags?.forEach((tag) => tagsSet.add(tag));
    });
    return Array.from(tagsSet);
  });
  
  // 根据筛选条件过滤模板
  const filteredTemplates = computed(() => {
    let templates = templateStore.templates;
    
    // 搜索筛选
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase();
      templates = templates.filter(
        (template) =>
          template.name.toLowerCase().includes(query) ||
          template.description?.toLowerCase().includes(query) ||
          template.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }
    
    // 分类筛选
    if (selectedCategory.value) {
      templates = templates.filter((template) => template.category === selectedCategory.value);
    }
    
    // 标签筛选
    if (selectedTags.value.length > 0) {
      templates = templates.filter((template) =>
        selectedTags.value.every((tag) => template.tags?.includes(tag))
      );
    }
    
    // 排序 - 先显示精选，然后按创建时间降序
    return [...templates].sort((a, b) => {
      if (a.featured && !b.featured) return -1;
      if (!a.featured && b.featured) return 1;
      return new Date(b.createdAt) - new Date(a.createdAt);
    });
  });
  
  // 分页
  const totalPages = computed(() => {
    return Math.ceil(filteredTemplates.value.length / pageSize.value);
  });
  
  const displayedTemplates = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredTemplates.value.slice(start, end);
  });
  
  // 初始加载数据
  onMounted(async () => {
    loading.value = true;
    try {
      await templateStore.fetchTemplates();
    } catch (error) {
      console.error('載入模板失敗:', error);
      message.error('載入模板列表失敗，請稍後再試');
    } finally {
      loading.value = false;
    }
  });
  
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
  
  // 获取风格名称
  const getStyleName = (styleValue) => {
    if (!styleValue) return '';
    
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
  
  // 分页大小变更处理
  const onPageSizeChange = (size) => {
    pageSize.value = size;
    currentPage.value = 1; // 重置到第一页
  };
  
  // 选择模板
  const selectTemplate = (template) => {
    selectedTemplateDetail.value = template;
    showTemplateDetailModal.value = true;
  };
  
  // 使用选定的模板
  const useTemplate = () => {
    if (!selectedTemplateDetail.value) return;
    
    // 导航到设计输入页面，使用所选模板
    router.push({
      name: 'design-input',
      params: {},
      query: { templateId: selectedTemplateDetail.value.id }
    });
    
    showTemplateDetailModal.value = false;
  };
  
  // 处理上传变化
  const handleUploadChange = (options) => {
    const { file } = options;
    uploadFile.value = file;
    
    // 获取文件 URL
    if (file.file) {
      uploadFileUrl.value = URL.createObjectURL(file.file);
    }
  };
  
  // 添加新标签
  const addNewTag = () => {
    if (!newTagName.value.trim()) return;
    
    if (!newTemplate.value.tags.includes(newTagName.value.trim())) {
      newTemplate.value.tags.push(newTagName.value.trim());
    }
    
    newTagName.value = '';
    isAddingTag.value = false;
  };
  
  // 移除标签
  const removeTag = (tag) => {
    const index = newTemplate.value.tags.indexOf(tag);
    if (index !== -1) {
      newTemplate.value.tags.splice(index, 1);
    }
  };
  
  // 保存为模板
  const saveAsTemplate = async () => {
    if (!newTemplate.value.name || !currentProject.value) return;
    
    savingTemplate.value = true;
    try {
      // 准备模板数据
      const templateData = {
        name: newTemplate.value.name,
        description: newTemplate.value.description,
        category: newTemplate.value.category,
        tags: newTemplate.value.tags,
        projectId: currentProject.value.id,
        params: currentProject.value.designParams || {},
        thumbnail: uploadFileUrl.value || (currentProject.value.thumbnail || '')
      };
      
      // 如果包含图像，添加相关图像
      if (newTemplate.value.includeImages) {
        templateData.relatedImages = imageStore.getImagesByProject(currentProject.value.id);
      }
      
      // 保存模板
      const savedTemplate = await templateStore.createTemplate(templateData);
      
      // 显示成功消息
      message.success('模板保存成功');
      
      // 重置表单
      newTemplate.value = {
        name: '',
        description: '',
        category: '',
        tags: [],
        includeImages: true,
        thumbnail: null
      };
      uploadFileUrl.value = '';
      showSaveTemplateModal.value = false;
    } catch (error) {
      console.error('保存模板失敗:', error);
      message.error('保存模板失敗，請稍後再試');
    } finally {
      savingTemplate.value = false;
    }
  };
  </script>
  
  <style scoped>
  .template-manager {
    width: 100%;
  }
  
  .template-card {
    margin-bottom: 24px;
  }
  
  .filter-section {
    margin-bottom: 20px;
  }
  
  .search-input {
    width: 100%;
    max-width: 300px;
    margin-bottom: 16px;
  }
  
  .filter-controls {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .filter-label {
    font-size: 14px;
    color: var(--secondary-text-color, #666);
    margin-right: 8px;
  }
  
  .templates-grid {
    margin-top: 20px;
  }
  
  .template-item {
    border-radius: 8px;
    overflow: hidden;
    background-color: var(--card-bg-color, #fff);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  
  .template-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  }
  
  .template-item.is-featured {
    box-shadow: 0 2px 12px rgba(24, 144, 255, 0.2);
  }
  
  .template-thumbnail {
    position: relative;
    height: 160px;
    overflow: hidden;
  }
  
  .template-badges {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    color: white;
  }
  
  .badge.featured {
    background-color: #1890ff;
  }
  
  .badge.new {
    background-color: #52c41a;
  }
  
  .template-info {
    padding: 12px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .template-info h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .template-info p {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--secondary-text-color, #666);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.4;
    flex: 1;
  }
  
  .template-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--secondary-text-color, #999);
    margin-top: auto;
  }
  
  .template-tags {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }
  
  .more-tags {
    font-size: 12px;
    color: var(--secondary-text-color, #999);
  }
  
  .pagination-container {
    margin-top: 24px;
    display: flex;
    justify-content: center;
  }
  
  .template-detail-content {
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .template-preview-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: var(--bg-color, #f5f7fa);
    border-radius: 8px;
    overflow: hidden;
  }
  
  .detail-image {
    max-width: 100%;
    max-height: 400px;
    object-fit: contain;
  }
  
  .template-details {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .template-details h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
  }
  
  .template-description {
    margin-bottom: 16px;
    font-size: 16px;
    color: var(--secondary-text-color, #666);
    line-height: 1.5;
  }
  
  .detail-section {
    margin-bottom: 24px;
  }
  
  .detail-section h3 {
    margin: 0 0 12px 0;
    font-size: 18px;
    font-weight: 500;
    color: var(--text-color, #333);
  }
  
  .parameter-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .parameter-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 8px;
    border-bottom: 1px dashed var(--border-color, #eaeaea);
  }
  
  .param-label {
    min-width: 80px;
    font-weight: 500;
    color: var(--secondary-text-color, #666);
  }
  
  .param-value {
    flex: 1;
  }
  
  .prompt-text {
    margin: 0;
    white-space: pre-wrap;
  }
  
  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .detail-tag {
    margin-right: 0;
  }
  
  .related-images {
    border-radius: 8px;
    overflow: hidden;
  }
  
  .carousel-item {
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: var(--bg-color, #f5f7fa);
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  .button-icon {
    margin-right: 4px;
    display: flex;
    align-items: center;
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
  
  .thumbnail-preview {
    margin-top: 12px;
    display: flex;
    justify-content: center;
  }
  
  .setting-desc {
    margin-left: 12px;
    font-size: 14px;
    color: var(--secondary-text-color, #666);
  }
  
  /* 响应式布局 */
  @media (max-width: 768px) {
    .filter-controls {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .category-container, .tags-container {
      width: 100%;
    }
    
    .search-input {
      width: 100%;
      max-width: none;
    }
    
    .template-thumbnail {
      height: 120px;
    }
  }
  </style>