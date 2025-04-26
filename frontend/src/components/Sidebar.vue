<template>
    <div class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <NButton quaternary circle @click="toggleCollapse">
          <template #icon>
            <div class="icon-container">
              {{ isCollapsed ? '→' : '←' }}
            </div>
          </template>
        </NButton>
        <h2 class="sidebar-title" v-if="!isCollapsed">設計流程</h2>
      </div>
  
      <div class="workflow-steps">
        <NMenu
          :value="activeMenuItem"
          :collapsed="isCollapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
          @update:value="handleMenuClick"
        />
      </div>
  
      <div class="sidebar-footer" v-if="!isCollapsed">
        <div class="current-project" v-if="currentProject">
          <h3>當前專案</h3>
          <p>{{ currentProject.name }}</p>
        </div>
        
        <div class="user-actions">
          <NButton quaternary block @click="goToSettings">
            <template #icon>
              <div class="button-icon">⚙️</div>
            </template>
            {{ t('settings') }}
          </NButton>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, h } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { NMenu, NButton } from 'naive-ui';
  import { useProjectStore } from '../stores/project';
  import { useTranslation } from '../composables/useTranslation';
  
  const props = defineProps({
    collapsed: {
      type: Boolean,
      default: false
    }
  });
  
  const emit = defineEmits(['collapse-change']);
  
  const router = useRouter();
  const route = useRoute();
  const projectStore = useProjectStore();
  const { t } = useTranslation();
  
  const isCollapsed = ref(props.collapsed);
  const currentProject = computed(() => projectStore.currentProject);
  
  // 根據當前路由決定激活的菜單項
  const activeMenuItem = computed(() => {
    const path = route.path;
    if (path.includes('/project')) return 'project';
    if (path.includes('/design')) return 'design-input';
    if (path.includes('/generate')) return 'ai-generate';
    if (path.includes('/revise')) return 'designer-revision';
    if (path.includes('/gallery')) return 'gallery';
    return 'project';
  });
  
  // 菜單選項
  const menuOptions = computed(() => {
    const projectId = route.params.projectId || 'temp';
    
    return [
      {
        label: () => h('div', { class: 'menu-label-container' }, [
          h('div', { class: 'menu-label' }, '1. 設計資料輸入'),
          h('div', { class: 'menu-tooltip' }, '收集設計參數與構想')
        ]),
        key: 'design-input',
        icon: () => h('div', { class: 'menu-icon' }, '📋'),
        disabled: !currentProject.value && projectId === 'temp'
      },
      {
        label: () => h('div', { class: 'menu-label-container' }, [
          h('div', { class: 'menu-label' }, '2. AI 生成設計'),
          h('div', { class: 'menu-tooltip' }, '快速生成多樣且符合品牌風格的概念圖')
        ]),
        key: 'ai-generate',
        icon: () => h('div', { class: 'menu-icon' }, '🚀'),
        disabled: !currentProject.value && projectId === 'temp'
      },
      {
        label: () => h('div', { class: 'menu-label-container' }, [
          h('div', { class: 'menu-label' }, '3. 設計師精修'),
          h('div', { class: 'menu-tooltip' }, '手動細修與創意微調')
        ]),
        key: 'designer-revision',
        icon: () => h('div', { class: 'menu-icon' }, '🎨'),
        disabled: true // 需要有選定的圖像才能啟用
      },
      {
        label: () => h('div', { class: 'menu-label-container' }, [
          h('div', { class: 'menu-label' }, '4. 品牌設計資料庫'),
          h('div', { class: 'menu-tooltip' }, '儲存、製作模板，持續累積品牌設計知識')
        ]),
        key: 'gallery',
        icon: () => h('div', { class: 'menu-icon' }, '🏆'),
      },
      {
        label: () => h('div', { class: 'menu-label-container' }, [
          h('div', { class: 'menu-label' }, '專案管理'),
          h('div', { class: 'menu-tooltip' }, '管理您的設計專案')
        ]),
        key: 'project',
        icon: () => h('div', { class: 'menu-icon' }, '📁'),
      }
    ];
  });
  
  // 處理菜單點擊
  const handleMenuClick = (key) => {
    const projectId = currentProject.value?.id || route.params.projectId || 'temp';
    
    switch (key) {
      case 'design-input':
        router.push({ name: 'design-input', params: { projectId } });
        break;
      case 'ai-generate':
        router.push({ name: 'ai-generate', params: { projectId } });
        break;
      case 'designer-revision':
        // 只有在有選定圖像時才跳轉
        if (route.params.imageId) {
          router.push({ 
            name: 'designer-revision', 
            params: { 
              projectId, 
              imageId: route.params.imageId 
            } 
          });
        }
        break;
      case 'gallery':
        router.push({ name: 'gallery' });
        break;
      case 'project':
        router.push({ name: 'project' });
        break;
      default:
        break;
    }
  };
  
  // 切換折疊狀態
  const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value;
    emit('collapse-change', isCollapsed.value);
  };
  
  // 前往設置頁面
  const goToSettings = () => {
    router.push({ name: 'settings' });
  };
  
  // 在組件掛載時檢查當前項目
  onMounted(() => {
    const id = route.params.projectId;
    if (id && id !== 'temp') {
      projectStore.fetchProjectById(id);
    }
  });
  </script>
  
  <style scoped>
  .sidebar {
    height: 100vh;
    background-color: #fff;
    border-right: 1px solid #eaeaea;
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    width: 250px;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  
  .sidebar.collapsed {
    width: 64px;
  }
  
  .sidebar-header {
    padding: 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #eaeaea;
  }
  
  .sidebar-title {
    margin: 0 0 0 12px;
    font-size: 18px;
    font-weight: 600;
  }
  
  .workflow-steps {
    flex: 1;
    overflow-y: auto;
    padding-top: 8px;
  }
  
  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid #eaeaea;
  }
  
  .current-project {
    margin-bottom: 16px;
  }
  
  .current-project h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #666;
  }
  
  .current-project p {
    margin: 0;
    font-weight: 500;
    color: #333;
  }
  
  .user-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
  }
  
  .button-icon {
    margin-right: 8px;
  }
  
  .menu-icon {
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .menu-label-container {
    display: flex;
    flex-direction: column;
  }
  
  .menu-label {
    font-size: 14px;
    font-weight: 500;
  }
  
  .menu-tooltip {
    font-size: 12px;
    color: #666;
    margin-top: 2px;
  }
  
  /* 深色模式適配 */
  :root.dark .sidebar {
    background-color: #1e1e1e;
    border-right-color: #333;
  }
  
  :root.dark .sidebar-header,
  :root.dark .sidebar-footer {
    border-color: #333;
  }
  
  :root.dark .current-project h3 {
    color: #aaa;
  }
  
  :root.dark .current-project p {
    color: #ddd;
  }
  
  :root.dark .menu-tooltip {
    color: #aaa;
  }
  </style>