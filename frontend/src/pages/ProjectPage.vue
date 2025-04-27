<template>
  <div class="project-page">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1>設計畫廊</h1>
          <p class="subtitle">品牌設計資料庫</p>
        </div>
        <NButton type="primary" size="large" @click="showCreateModal = true">
          <template #icon>
            <div class="button-icon">
              <NIcon>
                <PlusOutlined />
              </NIcon>
            </div>
          </template>
          創建新專案
        </NButton>
      </div>
    </NLayoutHeader>

    <div class="template-showcase" v-if="templates.length">
      <NSpin :show="loading">
        <div class="showcase-header">
          <h2>推薦模板</h2>
          <NButton text @click="showAllTemplates = !showAllTemplates">
            {{ showAllTemplates ? "收起" : "查看全部" }}
            <template #icon>
              <NIcon>
                <component :is="showAllTemplates ? 'UpOutlined' : 'DownOutlined'"></component>
              </NIcon>
            </template>
          </NButton>
        </div>

        <div class="template-carousel">
          <div v-for="template in displayedTemplates" :key="template.id" class="template-item"
            @click="selectTemplateAndCreate(template)">
            <div class="template-preview">
              <NImage :src="template.thumbnail" object-fit="cover" :preview-disabled="true"
                fallback-src="/placeholder-image.png" :alt="template.name" />
              <div class="template-quick-actions">
                <NButton type="primary" size="small">快速使用</NButton>
              </div>
            </div>
            <div class="template-meta">
              <h3>{{ template.name }}</h3>
              <div class="template-tags">
                <NTag v-for="(tag, index) in template.tags" :key="index" size="small" :bordered="false"
                  :color="{ color: getTagColor(tag) }">
                  {{ tag }}
                </NTag>
              </div>
            </div>
          </div>
        </div>
      </NSpin>
    </div>

    <NLayoutContent class="page-content">
      <div class="content-wrapper">
        <div class="filters-section">
          <div class="filter-header">
            <h2>專案列表</h2>
            <NInput v-model:value="searchQuery" placeholder="搜尋專案..." clearable class="search-input">
              <template #prefix>
                <NIcon>
                  <SearchOutlined />
                </NIcon>
              </template>
            </NInput>
          </div>

          <div class="filter-controls">
            <div class="tags-container">
              <span class="filter-label">標籤篩選：</span>
              <TagSelector v-if="availableTags.length" :tags="availableTags" v-model:selected="selectedTags" />
              <span v-else class="no-tags">暫無標籤</span>
            </div>

            <div class="sort-container">
              <span class="filter-label">排序方式：</span>
              <NSelect v-model:value="sortOption" :options="sortOptions" size="medium" class="sort-select" />
            </div>
          </div>
        </div>

        <NSpin :show="loading" description="載入中..." size="large">
          <div v-if="projects.length" class="projects-container">
            <div class="projects-grid">
              <!-- Replacing NGrid with CSS Grid -->
              <div v-for="project in displayedProjects" :key="project.id" class="project-card"
                @click="openProject(project.id)">
                <ProjectCard :project="project" />
              </div>
            </div>

            <div v-if="totalPages > 1" class="pagination-container">
              <NPagination v-model:page="currentPage" :page-count="totalPages" :page-size="pageSize"
                :item-count="filteredProjects.length" show-size-picker :page-sizes="[8, 12, 16, 24]"
                @update:page-size="onPageSizeChange" />
            </div>
          </div>

          <NResult v-else-if="!loading" status="info" title="沒有找到專案" description="還沒有創建任何專案，立即開始創建吧！">
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
    <NModal v-model:show="showCreateModal" preset="card" title="創建新專案" size="huge" :closable="true"
      style="max-width: 900px">
      <div class="modal-content">
        <NForm ref="formRef" :model="newProject" :rules="formRules" label-placement="left" label-width="100">
          <NFormItem label="專案名稱" path="name" required>
            <NInput v-model:value="newProject.name" placeholder="請輸入專案名稱" clearable autofocus />
          </NFormItem>

          <NFormItem label="專案描述" path="description">
            <NInput v-model:value="newProject.description" type="textarea" placeholder="請輸入專案描述"
              :autosize="{ minRows: 3, maxRows: 5 }" />
          </NFormItem>

          <NFormItem label="標籤">
            <div v-if="isAddingTag" class="tag-input-area">
              <NInput v-model:value="newTagName" placeholder="輸入標籤名稱" @keydown.enter.prevent="addNewTag" />
              <NButton type="primary" size="small" @click="addNewTag">添加</NButton>
              <NButton size="small" @click="isAddingTag = false">取消</NButton>
            </div>
            <div v-else class="tags-area">
              <div class="tags-display">
                <NTag v-for="tag in newProject.tags" :key="tag" type="info" closable @close="removeTag(tag)">
                  {{ tag }}
                </NTag>
                <NButton size="small" class="add-tag-btn" @click="isAddingTag = true">
                  <NIcon class="tag-icon">
                    <PlusOutlined />
                  </NIcon>
                  添加標籤
                </NButton>
              </div>
            </div>
          </NFormItem>

          <NFormItem label="專案模板" v-if="templates.length">
            <div class="template-section">

              <NDivider>選擇一個模板開始</NDivider>
              <div>
                <NRadioGroup v-model:value="selectedTemplate" class="template-radio-group">
                  <NGrid x-gap="16" y-gap="16" cols="1 s:2 m:3" responsive="screen">
                    <NGridItem v-for="template in templates" :key="template.id">
                      <div class="template-card" :class="{ 'selected-template': selectedTemplate === template.id }"
                        @click="selectedTemplate = template.id">
                        <div class="template-image">
                          <NImage :src="template.thumbnail" object-fit="cover" :preview-disabled="true"
                            fallback-src="/placeholder-image.png" :alt="template.name" />
                          <div class="template-overlay">
                            <div class="template-check" v-if="selectedTemplate === template.id">
                              <NIcon size="24">
                                <CheckCircleFilled />
                              </NIcon>
                            </div>
                          </div>
                        </div>
                        <div class="template-info">
                          <h3 class="template-title">{{ template.name }}</h3>
                          <div class="template-tags">
                            <NTag v-for="(tag, index) in getTemplateTags(template)" :key="index" size="small"
                              :bordered="false" :color="{ color: getTagColor(tag) }">
                              {{ tag }}
                            </NTag>
                          </div>
                          <p class="template-description">{{ template.description }}</p>
                        </div>
                      </div>
                    </NGridItem>
                  </NGrid>
                </NRadioGroup>
              </div>
            </div>
          </NFormItem>
        </NForm>
      </div>

      <template #footer>
        <div class="modal-footer">
          <NButton @click="showCreateModal = false">取消</NButton>
          <NButton type="primary" :disabled="!newProject.name" :loading="creatingProject" @click="createProject">
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
import {
  PlusOutlined,
  SearchOutlined,
  CheckCircleFilled,
  DownOutlined,
  UpOutlined,
} from "@vicons/antd";
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

const showAllTemplates = ref(false);
const tagColors = [
  "#f50",
  "#2db7f5",
  "#87d068",
  "#108ee9",
  "#7265e6",
  "#00a2ae",
  "#ffbf00",
];

// Get a consistent color for a specific tag
const getTagColor = (tag) => {
  const hash = tag.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return tagColors[hash % tagColors.length] + "33"; // Adding 33 for transparency
};

// Get template tags
const getTemplateTags = (template) => {
  return template.tags || [];
};

// Displayed templates (limited or all based on toggle)
const displayedTemplates = computed(() => {
  return showAllTemplates.value ? templates.value : templates.value.slice(0, 4);
});

// Handle selecting a template and immediately open create project dialog
const selectTemplateAndCreate = (template) => {
  selectedTemplate.value = template.id;
  showCreateModal.value = true;
};
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

const createProject = async () => {
  if (!newProject.value.name) return;

  creatingProject.value = true;
  try {
    // 準備表單數據
    const formData = new FormData();
    formData.append("name", newProject.value.name);

    // 添加描述 (如果有)
    if (newProject.value.description) {
      formData.append("description", newProject.value.description);
    }

    // 添加標籤 (如果有)
    if (newProject.value.tags && newProject.value.tags.length > 0) {
      formData.append("tags", JSON.stringify(newProject.value.tags));
    }

    // 添加模板ID (如果有)
    if (selectedTemplate.value) {
      formData.append("templateId", selectedTemplate.value);
    }

    // 發送API請求
    const response = await fetch("https://ec2.sausagee.party/project/create", {
      method: "POST",
      body: formData,
      // credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`API返回錯誤狀態: ${response.status}`);
    }

    const data = await response.json();

    // 更新專案列表
    await fetchProjects();

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
    if (data.id) {
      router.push({
        name: "design-input",
        params: { projectId: data.id },
      });
    }
  } catch (error) {
    console.error("創建專案失敗:", error);
    message.error("創建專案失敗，請稍後再試");
  } finally {
    creatingProject.value = false;
  }
};

// 計算所有可用的標籤
const availableTags = computed(() => {
  const tagsSet = new Set();
  projects.value.forEach((project) => {
    project.tags?.forEach((tag) => tagsSet.add(tag));
  });
  return Array.from(tagsSet);
});

// 獲取專案列表
const projects = ref([]);

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
const templates = ref([]);
const error = ref(null);

// Add this function to fetch templates
const fetchTemplates = async () => {
  try {
    loading.value = true;
    // First get list of template IDs
    const response = await fetch('https://ec2.sausagee.party/templates');
    const data = await response.json();

    // Then fetch details for each template
    const templateDetails = await Promise.all(
      data.templates.map(async (id) => {
        const detailResponse = await fetch(`https://ec2.sausagee.party/template/${id}`);
        const template = await detailResponse.json();

        // Get thumbnail URL from first image if available
        const thumbnailUrl = `https://ec2.sausagee.party/thumb/${template.id}`;

        return {
          id: template.id,
          name: template.name,
          description: template.description || '',
          thumbnail: thumbnailUrl,
          tags: template.tags || [],
          parameters: template.parameters || {},
          createdAt: template.created,
          modifiedAt: template.modified
        };
      })
    );

    templates.value = templateDetails;
    error.value = null;
  } catch (err) {
    console.error('Error fetching templates:', err);
    error.value = 'Failed to load templates';
    message.error('載入模板失敗，請稍後再試');
  } finally {
    loading.value = false;
  }
};

// Add fetchProjects function
const fetchProjects = async () => {
  try {
    loading.value = true;
    // First get list of project IDs
    const response = await fetch('https://ec2.sausagee.party/projects');
    const data = await response.json();

    // Then fetch details for each project
    const projectDetails = await Promise.all(
      data.projects.map(async (id) => {
        const detailResponse = await fetch(`https://ec2.sausagee.party/project/${id}`);
        const project = await detailResponse.json();

        // Get thumbnail URL from first image if available
        const thumbnailUrl = `https://ec2.sausagee.party/thumb/${project.id}`;

        return {
          id: project.id,
          name: project.name,
          description: project.description || '',
          thumbnail: thumbnailUrl,
          tags: project.tags || [],
          images: project.images || [],
          readonly: project.readonly,
          createdAt: project.created,
          modifiedAt: project.modified
        };
      })
    );

    projects.value = projectDetails;
    error.value = null;
  } catch (err) {
    console.error('Error fetching projects:', err);
    error.value = 'Failed to load projects';
    message.error('載入專案失敗，請稍後再試');
  } finally {
    loading.value = false;
  }
};

// 初始載入專案和模板
onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([
      fetchProjects(),
      fetchTemplates()
    ]);
  } catch (error) {
    console.error('載入數據失敗:', error);
    message.error('載入數據失敗，請稍後再試');
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
// const createProject = async () => {
//   if (!newProject.value.name) return;

//   creatingProject.value = true;
//   try {
//     const createdProject = await projectStore.createProject({
//       ...newProject.value,
//       templateId: selectedTemplate.value,
//     });

//     // 顯示成功消息
//     message.success("專案創建成功");

//     // 重置表單
//     newProject.value = {
//       name: "",
//       description: "",
//       tags: [],
//     };
//     selectedTemplate.value = null;
//     showCreateModal.value = false;

//     // 導航到新建專案的設計頁面
//     if (createdProject.id) {
//       router.push({
//         name: "design-input",
//         params: { projectId: createdProject.id },
//       });
//     }
//   } catch (error) {
//     console.error("創建專案失敗:", error);
//     message.error("創建專案失敗，請稍後再試");
//   } finally {
//     creatingProject.value = false;
//   }
// };
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.project-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  flex-wrap: wrap;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
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
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.selected-template {
  border: 2px solid var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.template-image {
  position: relative;
  height: 140px;
  overflow: hidden;
  flex-shrink: 0;
}

.template-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: var(--primary-color);
}

.template-card:hover .template-overlay {
  opacity: 1;
}

.selected-template .template-overlay {
  opacity: 1;
  background: rgba(0, 0, 0, 0.06);
}

.template-check {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 8px;
}


.template-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.template-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  margin-top: auto;
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

/* Modal styling enhancements */
.enhanced-project-modal :deep(.n-card-header__main) {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #333;
}

.enhanced-project-modal :deep(.n-card) {
  border-radius: 12px;
  overflow: hidden;
}

.enhanced-project-modal :deep(.n-card-header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.create-project-header {
  margin-bottom: 24px;
}

.step-indicator {
  display: flex;
  align-items: center;
  width: 100%;
  margin: 16px 0;
}

.step {
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.step.active {
  opacity: 1;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
  color: #888;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background-color: var(--primary-color);
  color: white;
}

.step-label {
  font-weight: 500;
  color: #888;
  transition: all 0.3s ease;
}

.step.active .step-label {
  color: var(--primary-color);
}

.step-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(to right, var(--primary-color), #f0f0f0);
  margin: 0 10px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.section-divider {
  height: 1px;
  background-color: rgba(0, 0, 0, 0.06);
  margin-bottom: 18px;
}

.form-section {
  margin-bottom: 28px;
}

.enhanced-input {
  transition: all 0.3s ease;
}

.enhanced-input:hover {
  border-color: var(--primary-color);
}

.enhanced-tag {
  padding: 5px 10px;
  border-radius: 20px;
}

.tag-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.tag-btn {
  transition: all 0.2s ease;
}

.template-section {
  margin-top: 16px;
}

.template-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.template-card {
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.08);
}

.template-overlay {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.03);
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.template-card:hover .template-overlay {
  opacity: 1;
}

.selected-template .template-overlay {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

.template-check {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 8px;
}

.cancel-button,
.create-button {
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.create-button {
  padding: 8px 24px;
  font-size: 15px;
}

:root.dark .enhanced-project-modal :deep(.n-card-header__main) {
  color: #e0e0e0;
}

:root.dark .section-title {
  color: #e0e0e0;
}

:root.dark .step-number {
  background-color: #333;
  color: #aaa;
}

:root.dark .step-line {
  background: linear-gradient(to right, var(--primary-color), #333);
}

:root.dark .section-divider {
  background-color: rgba(255, 255, 255, 0.1);
}

:root.dark .template-overlay {
  background: rgba(255, 255, 255, 0.05);
}

:root.dark .selected-template .template-overlay {
  background: rgba(255, 255, 255, 0.1);
}

.template-showcase {
  background: #fff;
  padding: 24px;
  margin-bottom: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.showcase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px 16px;
}

.showcase-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.template-carousel {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 8px 16px 16px;
  scroll-behavior: smooth;
  max-width: 1400px;
  margin: 0 auto;
}

.template-carousel::-webkit-scrollbar {
  height: 6px;
}

.template-carousel::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.template-carousel::-webkit-scrollbar-track {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

.template-item {
  min-width: 250px;
  flex: 0 0 auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.template-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.template-preview {
  position: relative;
  height: 140px;
  overflow: hidden;
}

.template-preview :deep(.n-image) {
  height: 100%;
  /* Make NImage component fill container height */
}

.template-preview :deep(.n-image img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* Ensure image covers the area */
  object-position: center;
  /* Center the image */
}

/* Add these new styles for better image handling */
.template-preview :deep(.n-image-preview-container) {
  height: 100%;
}

.template-preview :deep(.n-image-wrapper) {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-quick-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
  display: flex;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.template-item:hover .template-quick-actions {
  opacity: 1;
  transform: translateY(0);
}

.template-meta {
  padding: 12px;
}

.template-meta h3 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.template-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Dark mode support */
:root.dark .template-showcase {
  background: #1f1f1f;
}
</style>
