<template>
    <div class="template-integration">
      <div v-if="templateSelectVisible" class="template-select-section">
        <div class="section-header">
          <h2>從模板開始</h2>
          <NButton text @click="templateSelectVisible = false">
            隱藏 <NIcon><UpOutlined /></NIcon>
          </NButton>
        </div>
        
        <div v-if="recentTemplates.length" class="recent-templates-section">
          <h3 class="subsection-title">最近使用的模板</h3>
          <div class="recent-templates">
            <div 
              v-for="template in recentTemplates.slice(0, 5)" 
              :key="template.id"
              class="recent-template-item"
              @click="selectTemplate(template)"
            >
              <div class="template-thumb">
                <NImage
                  :src="template.thumbnail"
                  object-fit="cover"
                  fallback-src="/placeholder-image.png"
                  :alt="template.name"
                />
              </div>
              <div class="template-info">
                <span class="template-name">{{ template.name }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="featured-templates-section">
          <h3 class="subsection-title">
            推薦模板
            <NButton text size="small" @click="goToTemplateLibrary">
              瀏覽更多 <NIcon><RightOutlined /></NIcon>
            </NButton>
          </h3>
          <NGrid cols="1 s:2 m:3 l:4" x-gap="16" y-gap="16">
            <NGridItem v-for="template in featuredTemplates.slice(0, 4)" :key="template.id">
              <div 
                class="template-card" 
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
                  <h3 class="template-name">{{ template.name }}</h3>
                  <p class="template-desc">{{ template.description }}</p>
                </div>
              </div>
            </NGridItem>
          </NGrid>
        </div>
      </div>
      <div v-else class="template-collapsed">
        <NButton text @click="templateSelectVisible = true">
          從模板開始 <NIcon><DownOutlined /></NIcon>
        </NButton>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { useTemplateStore } from '../stores/template';
  import { useProjectStore } from '../stores/project';
  import {
    NButton,
    NGrid,
    NGridItem,
    NImage,
    NIcon
  } from 'naive-ui';
  import {
    UpOutlined,
    DownOutlined,
    RightOutlined
  } from '@vicons/antd';
  
  const props = defineProps({
    initialTemplateId: {
      type: String,
      default: null
    }
  });
  
  const emit = defineEmits(['template-selected', 'template-applied']);
  
  const router = useRouter();
  const route = useRoute();
  const templateStore = useTemplateStore();
  const projectStore = useProjectStore();
  
  const templateSelectVisible = ref(true);
  const loading = ref(false);
  
  // 獲取最近使用的模板
  const recentTemplates = computed(() => {
    return templateStore.getRecentlyUsedTemplates.value;
  });
  
  // 獲取精選模板
  const featuredTemplates = computed(() => {
    return templateStore.getFeaturedTemplates.value;
  });
  
  // 初始化
  onMounted(async () => {
    loading.value = true;
    try {
      // 加載模板資料
      await templateStore.fetchTemplates();
      
      // 如果提供了初始模板ID，自動選擇該模板
      if (props.initialTemplateId) {
        const template = templateStore.getTemplateById(props.initialTemplateId);
        if (template) {
          selectTemplate(template);
        }
      }
      
      // 從路由查詢參數中獲取模板ID
      const templateIdFromQuery = route.query.templateId;
      if (templateIdFromQuery) {
        const template = templateStore.getTemplateById(templateIdFromQuery);
        if (template) {
          selectTemplate(template);
        }
      }
    } catch (error) {
      console.error('載入模板失敗:', error);
    } finally {
      loading.value = false;
    }
  });
  
  // 監聽路由變化，檢查模板參數
  watch(() => route.query.templateId, (newTemplateId) => {
    if (newTemplateId) {
      const template = templateStore.getTemplateById(newTemplateId);
      if (template) {
        selectTemplate(template);
      }
    }
  });
  
  // 選擇模板
  const selectTemplate = (template) => {
    if (!template) return;
    
    // 發出模板選擇事件
    emit('template-selected', template);
    
    // 記錄最近使用
    templateStore.addRecentlyUsedTemplate(template.id);
    
    // 應用模板數據
    applyTemplate(template);
  };
  
  // 應用模板數據到當前設計
  const applyTemplate = (template) => {
    if (!template) return;
    
    // 從模板參數獲取設計參數
    const designParams = { ...template.params };
    
    // 發出模板應用事件，傳遞參數
    emit('template-applied', {
      templateId: template.id,
      templateName: template.name,
      designParams
    });
    
    // 隱藏模板選擇區域
    templateSelectVisible.value = false;
  };
  
  // 前往模板庫頁面
  const goToTemplateLibrary = () => {
    router.push({ name: 'templates' });
  };
  </script>
  
  <style scoped>
  .template-integration {
    margin-bottom: 24px;
  }
  
  .template-select-section {
    padding: 20px;
    background-color: var(--card-bg-color, #fff);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .section-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .subsection-title {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 500;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .recent-templates-section {
    margin-bottom: 24px;
  }
  
  .recent-templates {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 12px;
  }
  
  .recent-template-item {
    flex: 0 0 auto;
    width: 120px;
    border-radius: 8px;
    overflow: hidden;
    background-color: var(--card-bg-color, #fff);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .recent-template-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  .template-thumb {
    height: 80px;
    overflow: hidden;
  }
  
  .template-info {
    padding: 8px;
  }
  
  .template-name {
    font-size: 14px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
  }
  
  .template-card {
    border-radius: 8px;
    overflow: hidden;
    background-color: var(--card-bg-color, #fff);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .template-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  }
  
  .template-card.is-featured {
    box-shadow: 0 2px 12px rgba(24, 144, 255, 0.15);
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
  
  .template-desc {
    margin: 8px 0 0 0;
    font-size: 14px;
    color: var(--secondary-text-color, #666);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.4;
  }
  
  .template-collapsed {
    padding: 12px;
    background-color: var(--card-bg-color, #fff);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    text-align: center;
  }
  
  /* 深色模式適配 */
  :root.dark .template-select-section,
  :root.dark .template-collapsed,
  :root.dark .template-card,
  :root.dark .recent-template-item {
    background-color: var(--card-bg-color, #1e1e1e);
  }
  
  :root.dark .template-desc {
    color: var(--secondary-text-color, #aaa);
  }
  </style>