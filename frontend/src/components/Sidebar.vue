<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { NButton } from "naive-ui";
import { useProjectStore } from "../stores/project";
import { useTranslation } from "../composables/useTranslation";

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["collapse-change"]);

const router = useRouter();
const route = useRoute();
const projectStore = useProjectStore();
const { t } = useTranslation();

const isCollapsed = ref(props.collapsed);
const currentProject = computed(() => projectStore.currentProject);

// 根據當前路由決定激活的菜單項
const activeMenuItem = computed(() => {
  const path = route.path;
  if (path.includes("/project")) return "project";
  if (path.includes("/design")) return "design-input";
  if (path.includes("/generate")) return "ai-generate";
  if (path.includes("/revise")) return "designer-revision";
  if (path.includes("/gallery")) return "gallery";
  return "project";
});

// 導航到指定頁面
const navigateTo = (key) => {
  // 獲取當前項目ID，默認使用'temp'作為臨時ID
  const projectId =
    currentProject.value?.id || route.params.projectId || "temp";

  switch (key) {
    case "design-input":
      router.push({ name: "design-input", params: { projectId } });
      break;
    case "ai-generate":
      router.push({ name: "ai-generate", params: { projectId } });
      break;
    case "designer-revision":
      // 對於設計師精修頁面，如果有圖像ID則使用，否則回到生成頁面
      if (route.params.imageId) {
        router.push({
          name: "designer-revision",
          params: {
            projectId,
            imageId: route.params.imageId,
          },
        });
      } else {
        // 如果沒有圖像ID，則導航到AI生成頁面
        router.push({ name: "ai-generate", params: { projectId } });
      }
      break;
    case "gallery":
      router.push({ name: "gallery", params: { projectId } }); // Updated this line
      break;
    case "project":
      router.push({ name: "project" });
      break;
    default:
      break;
  }
};

// 切換折疊狀態
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  emit("collapse-change", isCollapsed.value);
};

// 前往設置頁面
const goToSettings = () => {
  router.push({ name: "settings" });
};

function goToHomepage() {
  router.push("/");
}

// 在組件掛載時檢查當前項目
onMounted(() => {
  const id = route.params.projectId;
  if (id && id !== "temp") {
    projectStore.fetchProjectById(id);
  }
});
</script>
<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <NButton quaternary circle @click="toggleCollapse">
        <template #icon>
          <div class="icon-container">
            {{ isCollapsed ? "→" : "←" }}
          </div>
        </template>
      </NButton>
      <h2 class="sidebar-title" v-if="!isCollapsed && currentProject">
        {{ currentProject.name }}
      </h2>
    </div>

    <div class="workflow-steps">
      <div class="step-list">
        <!-- 步驟 1: 設計資料輸入 -->
        <div
          class="step-item"
          :class="{ active: activeMenuItem === 'design-input' }"
          @click="navigateTo('design-input')"
        >
          <div class="step-icon">📋</div>
          <div class="step-content" v-if="!isCollapsed">
            <div class="step-title">
              {{ t("step1") }}. {{ t("designInputTitle") }}
            </div>
            <div class="step-desc">{{ t("step1Desc") }}</div>
          </div>
        </div>

        <!-- 步驟 2: AI 生成設計 -->
        <div
          class="step-item"
          :class="{ active: activeMenuItem === 'ai-generate' }"
          @click="navigateTo('ai-generate')"
        >
          <div class="step-icon">🚀</div>
          <div class="step-content" v-if="!isCollapsed">
            <div class="step-title">
              {{ t("step2") }}. {{ t("aiGenerateTitle") }}
            </div>
            <div class="step-desc">{{ t("step2Desc") }}</div>
          </div>
        </div>

        <!-- 步驟 3: 設計師精修 -->
        <div
          class="step-item"
          :class="{ active: activeMenuItem === 'designer-revision' }"
          @click="navigateTo('designer-revision')"
        >
          <div class="step-icon">🎨</div>
          <div class="step-content" v-if="!isCollapsed">
            <div class="step-title">
              {{ t("step3") }}. {{ t("designerRevisionTitle") }}
            </div>
            <div class="step-desc">{{ t("step3Desc") }}</div>
          </div>
        </div>

        <!-- 步驟 4: 品牌設計資料庫 -->
        <div
          class="step-item"
          :class="{ active: activeMenuItem === 'gallery' }"
          @click="navigateTo('gallery')"
        >
          <div class="step-icon">📁</div>
          <div class="step-content" v-if="!isCollapsed">
            <div class="step-title">{{ t("galleryTitle") }}</div>
            <div class="step-desc">{{ t("galleryDescription") }}</div>
          </div>
        </div>

        <!-- 專案管理 -->
        <div
          class="step-item"
          :class="{ active: activeMenuItem === 'project' }"
          @click="navigateTo('project')"
        >
          <div class="step-icon">🏆</div>
          <div class="step-content" v-if="!isCollapsed">
            <div class="step-title">{{ t("projectTitle") }}</div>
            <div class="step-desc">{{ t("projectDescription") }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer" v-if="!isCollapsed">
      <NButton quaternary block @click="goToHomepage">
        <h3>{{ t("about") }}</h3>
      </NButton>

      <div class="user-actions">
        <NButton quaternary block @click="goToSettings">
          <template #icon>
            <div class="button-icon">⚙️</div>
          </template>
          {{ t("settings") }}
        </NButton>
      </div>
    </div>
  </div>
</template>

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

.step-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 8px;
}

.step-item {
  display: flex;
  align-items: center;
  padding: 12px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.step-item:hover {
  background-color: #f5f5f5;
}

.step-item.active {
  background-color: #ebf5ff;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  min-width: 28px;
  margin-right: 12px;
}

.step-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-desc {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* 深色模式適配 */
:root.dark .sidebar {
  background-color: #1e1e1e;
  border-right-color: #333;
}

:root.dark .sidebar-header,
:root.dark .sidebar-footer {
  border-color: #333;
}

:root.dark .step-item:hover {
  background-color: #2a2a2a;
}

:root.dark .step-item.active {
  background-color: #0c2a4a;
}

:root.dark .current-project h3 {
  color: #aaa;
}

:root.dark .current-project p {
  color: #ddd;
}

:root.dark .step-desc {
  color: #aaa;
}

/* 確保在小屏幕上側邊欄可以完全展示 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    box-shadow: none;
  }
}
</style>
