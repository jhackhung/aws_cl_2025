<template>
    <div class="template-category-view">
      <div class="category-header">
        <h2 class="category-title">{{ categoryTitle }}</h2>
        <NButton size="small" text @click="viewAllCategory" v-if="templates.length > displayLimit">
          查看全部 <NIcon><ChevronRightOutlined /></NIcon>
        </NButton>
      </div>
      
      <NScrollbar x-scrollable style="padding-bottom: 12px;">
        <div class="category-templates">
          <div 
            v-for="template in displayedTemplates" 
            :key="template.id" 
            class="template-card"
            :class="{ 'is-featured': template.featured }"
            @click="$emit('select-template', template)"
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
              <div class="template-tags">
                <NTag 
                  v-for="tag in template.tags.slice(0, 2)" 
                  :key="tag" 
                  size="small"
                  :bordered="false"
                  class="template-tag"
                >
                  {{ tag }}
                </NTag>
                <span v-if="template.tags.length > 2" class="more-tags">+{{ template.tags.length - 2 }}</span>
              </div>
            </div>
            <div class="template-actions">
              <NButton text type="primary" @click.stop="$emit('use-template', template)">
                使用此模板
              </NButton>
            </div>
          </div>
        </div>
      </NScrollbar>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { NButton, NImage, NTag, NScrollbar, NIcon } from 'naive-ui';
  import { ChevronRightOutlined } from '@vicons/antd';
  
  const props = defineProps({
    categoryName: {
      type: String,
      required: true
    },
    categoryTitle: {
      type: String,
      required: true
    },
    templates: {
      type: Array,
      default: () => []
    },
    displayLimit: {
      type: Number,
      default: 5
    }
  });
  
  const emit = defineEmits(['view-all', 'select-template', 'use-template']);
  
  // 顯示有限數量的模板
  const displayedTemplates = computed(() => {
    return props.templates.slice(0, props.displayLimit);
  });
  
  // 查看此類別的所有模板
  const viewAllCategory = () => {
    emit('view-all', props.categoryName);
  };
  </script>
  
  <style scoped>
  .template-category-view {
    margin-bottom: 32px;
  }
  
  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .category-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }
  
  .category-templates {
    display: flex;
    gap: 16px;
    padding: 4px;
    min-width: min-content;
  }
  
  .template-card {
    position: relative;
    width: 260px;
    flex: 0 0 auto;
    border-radius: 8px;
    background-color: var(--card-bg-color, #fff);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    transition: all 0.3s ease;
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
  
  .template-info {
    padding: 12px;
  }
  
  .template-name {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .template-desc {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--secondary-text-color, #666);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.4;
    height: 40px;
  }
  
  .template-tags {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }
  
  .template-tag {
    margin-right: 0;
  }
  
  .more-tags {
    font-size: 12px;
    color: var(--secondary-text-color, #999);
  }
  
  .template-actions {
    padding: 0 12px 12px 12px;
    display: flex;
    justify-content: flex-end;
  }
  
  /* 深色模式適配 */
  :root.dark .template-card {
    background-color: var(--card-bg-color, #1e1e1e);
  }
  
  :root.dark .template-desc {
    color: var(--secondary-text-color, #aaa);
  }
  
  :root.dark .more-tags {
    color: var(--secondary-text-color, #999);
  }
  </style>