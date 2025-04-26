<template>
  <div class="project-page">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <h1>專案管理</h1>
        <NButton type="primary" @click="showCreateModal = true">
          創建新專案
        </NButton>
      </div>
    </NLayoutHeader>

    <NLayoutContent class="page-content">
      <div class="filters-container">
        <h2>專案列表</h2>
        <TagSelector
          v-if="availableTags.length"
          :tags="availableTags"
          v-model:selected="selectedTags"
        />
      </div>

      <NSpin :show="loading">
        <div v-if="projects.length" class="projects-grid">
          <NGrid x-gap="16" y-gap="16" cols="1 s:2 m:3 l:4 xl:5 2xl:6">
            <NGridItem v-for="project in filteredProjects" :key="project.id">
              <ProjectCard
                :project="project"
                @click="openProject(project.id)"
              />
            </NGridItem>
          </NGrid>
        </div>
        <NEmpty v-else description="沒有專案，立即創建一個吧！" />
      </NSpin>
    </NLayoutContent>

    <!-- 創建專案對話框 -->
    <NModal
      v-model:show="showCreateModal"
      preset="card"
      title="創建新專案"
      size="huge"
    >
      <NForm>
        <NFormItem label="專案名稱" required>
          <NInput
            v-model:value="newProject.name"
            placeholder="請輸入專案名稱"
          />
        </NFormItem>

        <NFormItem label="專案描述">
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
            <NButton @click="addNewTag">添加</NButton>
            <NButton @click="isAddingTag = false">取消</NButton>
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
            </div>
            <NButton size="small" @click="isAddingTag = true"
              >+ 添加標籤</NButton
            >
          </div>
        </NFormItem>

        <NFormItem label="專案模板" v-if="templates.length">
          <NGrid x-gap="16" y-gap="16" cols="1 s:2 m:3">
            <NGridItem v-for="template in templates" :key="template.id">
              <NCard
                hoverable
                :class="{
                  'selected-template': selectedTemplate === template.id,
                }"
                @click="selectedTemplate = template.id"
              >
                <template #cover>
                  <NImage
                    :src="template.thumbnail"
                    object-fit="cover"
                    :alt="template.name"
                  />
                </template>
                <div class="template-info">
                  <h3>{{ template.name }}</h3>
                  <p>{{ template.description }}</p>
                </div>
              </NCard>
            </NGridItem>
          </NGrid>
        </NFormItem>
      </NForm>

      <template #footer>
        <div class="modal-footer">
          <NButton @click="showCreateModal = false">取消</NButton>
          <NButton
            type="primary"
            :disabled="!newProject.name"
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
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useProjectStore } from "../stores/project";
import {
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NButton,
  NGrid,
  NGridItem,
  NEmpty,
  NSpin,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NTag,
  NCard,
  NImage,
} from "naive-ui";
import ProjectCard from "../components/project/ProjectCard.vue";
import TagSelector from "../components/ui/TagSelector.vue";

const router = useRouter();
const projectStore = useProjectStore();

// 頁面狀態
const loading = ref(false);
const showCreateModal = ref(false);
const selectedTags = ref([]);
const isAddingTag = ref(false);
const newTagName = ref("");
const selectedTemplate = ref(null);

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

// 基於標籤篩選專案
const filteredProjects = computed(() => {
  if (!selectedTags.value.length) return projects.value;

  return projects.value.filter((project) =>
    project.tags?.some((tag) => selectedTags.value.includes(tag))
  );
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

// 創建專案
const createProject = async () => {
  if (!newProject.value.name) return;

  loading.value = true;
  try {
    const createdProject = await projectStore.createProject({
      ...newProject.value,
      templateId: selectedTemplate.value,
    });

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
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.project-page {
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

.page-content {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

.filters-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  padding: 0 16px;
}

.projects-grid {
  margin-bottom: 48px;
  width: 100%;
}

.tag-input-area {
  display: flex;
  gap: 8px;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.selected-template {
  border: 2px solid var(--primary-color);
}

.template-info {
  margin-top: 8px;
}

.template-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.template-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
