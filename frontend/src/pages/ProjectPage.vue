<template>
  <div class="project-page">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1>專案管理</h1>
          <p class="subtitle">管理您的設計專案</p>
        </div>
        <NButton type="primary" size="large" @click="showCreateModal = true">
          <template #icon>
            <div class="button-icon">
              <NIcon><PlusOutlined /></NIcon>
            </div>
          </template>
          創建新專案
        </NButton>
      </div>
    </NLayoutHeader>

    <NLayoutContent class="page-content">
      <div class="content-wrapper">
        <div class="filters-section">
          <div class="filter-header">
            <h2>專案列表</h2>
            <NInput
              v-model:value="searchQuery"
              placeholder="搜尋專案..."
              clearable
              class="search-input"
            >
              <template #prefix>
                <NIcon><SearchOutlined /></NIcon>
              </template>
            </NInput>
          </div>

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

            <div class="sort-container">
              <span class="filter-label">排序方式：</span>
              <NSelect
                v-model:value="sortOption"
                :options="sortOptions"
                size="medium"
                class="sort-select"
              />
            </div>
          </div>
        </div>

        <NSpin :show="loading" description="載入中..." size="large">
          <div v-if="projects.length" class="projects-container">
            <div class="projects-grid">
              <NGrid x-gap="24" y-gap="24" cols="1 s:2 m:2 l:3 xl:4">
                <NGridItem
                  v-for="project in displayedProjects"
                  :key="project.id"
                >
                  <ProjectCard
                    :project="project"
                    @click="openProject(project.id)"
                    class="project-card"
                  />
                </NGridItem>
              </NGrid>
            </div>

            <div v-if="totalPages > 1" class="pagination-container">
              <NPagination
                v-model:page="currentPage"
                :page-count="totalPages"
                :page-size="pageSize"
                :item-count="filteredProjects.length"
                show-size-picker
                :page-sizes="[8, 12, 16, 24]"
                @update:page-size="onPageSizeChange"
              />
            </div>
          </div>

          <NResult
            v-else-if="!loading"
            status="info"
            title="沒有找到專案"
            description="還沒有創建任何專案，立即開始創建吧！"
          >
            <template #footer>
              <NButton type="primary" @click="showCreateModal = true">
                創建第一個專案
              </NButton>
            </template>
          </NResult>
        </NSpin>
      </div>
    </NLayoutContent>

    <!-- 創建專案對話框 -->
    <NModal
      v-model:show="showCreateModal"
      preset="card"
      title="創建新專案"
      size="huge"
      :closable="true"
      style="max-width: 900px"
    >
      <div class="modal-content">
        <NForm
          ref="formRef"
          :model="newProject"
          :rules="formRules"
          label-placement="left"
          label-width="100"
        >
          <NFormItem label="專案名稱" path="name" required>
            <NInput
              v-model:value="newProject.name"
              placeholder="請輸入專案名稱"
              clearable
              autofocus
            />
          </NFormItem>

          <NFormItem label="專案描述" path="description">
            <NInput
              v-model:value="newProject.description"
              type="textarea"
              placeholder="請輸入專案描述"
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </NFormItem>

          <NFormItem label="標籤">
            <div v-if="isAddingTag" class="tag-input-area">
              <NInput
                v-model:value="newTagName"
                placeholder="輸入標籤名稱"
                @keydown.enter.prevent="addNewTag"
              />
              <NButton type="primary" size="small" @click="addNewTag"
                >添加</NButton
              >
              <NButton size="small" @click="isAddingTag = false">取消</NButton>
            </div>
            <div v-else class="tags-area">
              <div class="tags-display">
                <NTag
                  v-for="tag in newProject.tags"
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

          <NFormItem label="專案模板" v-if="templates.length">
            <NDivider>選擇一個模板開始</NDivider>
            <NRadioGroup
              v-model:value="selectedTemplate"
              class="template-radio-group"
            >
              <NGrid x-gap="16" y-gap="16" cols="1 s:2 m:3">
                <NGridItem v-for="template in templates" :key="template.id">
                  <div
                    class="template-card"
                    :class="{
                      'selected-template': selectedTemplate === template.id,
                    }"
                    @click="selectedTemplate = template.id"
                  >
                    <div class="template-image">
                      <NImage
                        :src="template.thumbnail"
                        object-fit="cover"
                        :preview-disabled="true"
                        fallback-src="/placeholder-image.png"
                        :alt="template.name"
                      />
                      <div class="template-overlay">
                        <NIcon
                          size="24"
                          v-if="selectedTemplate === template.id"
                        >
                          <CheckCircleFilled />
                        </NIcon>
                      </div>
                    </div>
                    <div class="template-info">
                      <h3>{{ template.name }}</h3>
                      <p>{{ template.description }}</p>
                    </div>
                  </div>
                </NGridItem>
              </NGrid>
            </NRadioGroup>
          </NFormItem>
        </NForm>
      </div>

      <template #footer>
        <div class="modal-footer">
          <NButton @click="showCreateModal = false">取消</NButton>
          <NButton
            type="primary"
            :disabled="!newProject.name"
            :loading="creatingProject"
            @click="createProject"
          >
            創建專案
          </NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import { useProjectStore } from "../stores/project";
import { useMessage } from "naive-ui";
import {
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NButton,
  NGrid,
  NGridItem,
  NSpin,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NTag,
  NImage,
  NIcon,
  NSelect,
  NPagination,
  NResult,
  NDivider,
  NRadioGroup,
} from "naive-ui";
import { PlusOutlined, SearchOutlined, CheckCircleFilled } from "@vicons/antd";
import ProjectCard from "../components/project/ProjectCard.vue";
import TagSelector from "../components/ui/TagSelector.vue";

const router = useRouter();
const projectStore = useProjectStore();
const message = useMessage();

// 頁面狀態
const loading = ref(false);
const showCreateModal = ref(false);
const selectedTags = ref([]);
const isAddingTag = ref(false);
const newTagName = ref("");
const selectedTemplate = ref(null);
const creatingProject = ref(false);
const searchQuery = ref("");
const sortOption = ref("newest");
const currentPage = ref(1);
const pageSize = ref(12);

// 表單規則
const formRef = ref(null);
const formRules = {
  name: {
    required: true,
    message: "專案名稱不能為空",
    trigger: ["blur", "input"],
  },
};

// 排序選項
const sortOptions = [
  { label: "最新創建", value: "newest" },
  { label: "最早創建", value: "oldest" },
  { label: "名稱 A-Z", value: "nameAsc" },
  { label: "名稱 Z-A", value: "nameDesc" },
];

// 新專案表單
const newProject = ref({
  name: "",
  description: "",
  tags: [],
});

// 計算所有可用的標籤
const availableTags = computed(() => {
  const tagsSet = new Set();
  projectStore.projects.forEach((project) => {
    project.tags?.forEach((tag) => tagsSet.add(tag));
  });
  return Array.from(tagsSet);
});

// 獲取專案列表
const projects = computed(() => projectStore.projects || []);

// 基於標籤和搜索篩選專案
const filteredProjects = computed(() => {
  let result = projects.value;

  // 標籤篩選
  if (selectedTags.value.length) {
    result = result.filter((project) =>
      project.tags?.some((tag) => selectedTags.value.includes(tag))
    );
  }

  // 搜索篩選
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (project) =>
        project.name.toLowerCase().includes(query) ||
        project.description?.toLowerCase().includes(query)
    );
  }

  // 排序
  return [...result].sort((a, b) => {
    switch (sortOption.value) {
      case "newest":
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
      case "oldest":
        return new Date(a.createdAt || 0) - new Date(b.createdAt || 0);
      case "nameAsc":
        return a.name.localeCompare(b.name);
      case "nameDesc":
        return b.name.localeCompare(a.name);
      default:
        return 0;
    }
  });
});

// 分頁
const totalPages = computed(() => {
  return Math.ceil(filteredProjects.value.length / pageSize.value);
});

const displayedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredProjects.value.slice(start, end);
});

// 獲取模板列表
const templates = computed(() => projectStore.templates || []);

// 初始載入專案和模板
onMounted(async () => {
  loading.value = true;
  try {
    await projectStore.fetchProjects();
    await projectStore.fetchTemplates();
  } catch (error) {
    console.error("載入項目失敗:", error);
    message.error("載入專案列表失敗，請稍後再試");
  } finally {
    loading.value = false;
  }
});

// 開啟專案頁面
const openProject = (id) => {
  router.push({ name: "design-input", params: { projectId: id } });
};

// 添加新標籤
const addNewTag = () => {
  if (!newTagName.value.trim()) return;

  if (!newProject.value.tags.includes(newTagName.value.trim())) {
    newProject.value.tags.push(newTagName.value.trim());
  }

  newTagName.value = "";
  isAddingTag.value = false;
};

// 移除標籤
const removeTag = (tag) => {
  const index = newProject.value.tags.indexOf(tag);
  if (index !== -1) {
    newProject.value.tags.splice(index, 1);
  }
};

// 分頁大小變更處理
const onPageSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置到第一頁
};

// 創建專案
const createProject = async () => {
  if (!newProject.value.name) return;

  creatingProject.value = true;
  try {
    const createdProject = await projectStore.createProject({
      ...newProject.value,
      templateId: selectedTemplate.value,
    });

    // 顯示成功消息
    message.success("專案創建成功");

    // 重置表單
    newProject.value = {
      name: "",
      description: "",
      tags: [],
    };
    selectedTemplate.value = null;
    showCreateModal.value = false;

    // 導航到新建專案的設計頁面
    if (createdProject.id) {
      router.push({
        name: "design-input",
        params: { projectId: createdProject.id },
      });
    }
  } catch (error) {
    console.error("創建專案失敗:", error);
    message.error("創建專案失敗，請稍後再試");
  } finally {
    creatingProject.value = false;
  }
};
</script>

<style scoped>
.project-page {
  min-height: 100vh;
  width: 100%;
  background-color: #f5f7fa;
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
}

.title-section {
  display: flex;
  flex-direction: column;
}

.title-section h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #666;
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

.filters-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.search-input {
  width: 240px;
}

.filter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.tags-container,
.sort-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.sort-select {
  width: 140px;
}

.projects-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.projects-grid {
  width: 100%;
  background-color: transparent;
}

.project-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.tag-input-area {
  display: flex;
  gap: 8px;
  align-items: center;
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

.template-radio-group {
  width: 100%;
}

.template-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.template-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.selected-template {
  border: 2px solid var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.template-image {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.template-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--primary-color);
}

.template-info {
  padding: 12px;
}

.template-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 500;
}

.template-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-content {
  padding: 8px 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input {
    width: 100%;
  }

  .filter-controls {
    flex-direction: column;
    align-items: flex-start;
  }

  .tags-container,
  .sort-container {
    width: 100%;
  }

  .sort-select {
    width: 100%;
  }
}
</style>
