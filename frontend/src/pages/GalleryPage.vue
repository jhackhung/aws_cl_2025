<template>
  <div class="gallery-page">
    <GalleryPageHeader @go-to-create-image="goToCreateImage" />

    <NLayoutContent class="page-content">
      <div class="content-wrapper">
        <div class="filters-section">
          <div class="filter-header">
            <h2>圖像列表</h2>
            <NInput
              v-model:value="searchQuery"
              placeholder="搜尋圖像..."
              clearable
              class="search-input"
            >
              <template #prefix>
                <NIcon><SearchOutlined /></NIcon>
              </template>
            </NInput>
          </div>

          <div class="filter-controls">
            <div class="project-container">
              <span class="filter-label">專案篩選：</span>
              <NSelect
                v-model:value="filterProject"
                :options="projectOptions"
                placeholder="選擇專案"
                clearable
                class="filter-select"
              />
            </div>

            <div class="tags-container">
              <span class="filter-label">標籤篩選：</span>
              <TagSelector
                v-if="availableTags.length"
                :tags="availableTags"
                v-model:selected="selectedTags"
              />
              <span v-else class="no-tags">暫無標籤</span>
            </div>
          </div>
        </div>

        <NSpin :show="loading" description="載入中..." size="large">
          <div v-if="filteredImages.length" class="gallery-container">
            <div class="gallery-grid">
              <NGrid x-gap="24" y-gap="24" cols="1 s:2 m:3 l:4 xl:5 2xl:6">
                <NGridItem v-for="image in filteredImages" :key="image.id">
                  <div class="gallery-item">
                    <NImage
                      :src="image.url"
                      object-fit="cover"
                      :alt="'設計圖像'"
                      lazy
                      class="gallery-image"
                    />
                    <div class="image-overlay">
                      <div class="image-info">
                        <h3 v-if="image.projectName">
                          {{ truncateText(image.projectName, 20) }}
                        </h3>
                        <div class="image-tags">
                          <NTag
                            v-for="tag in image.tags"
                            :key="tag"
                            size="small"
                            :bordered="false"
                            type="info"
                          >
                            {{ tag }}
                          </NTag>
                        </div>
                      </div>
                      <div class="image-actions">
                        <NButton
                          circle
                          secondary
                          @click.stop="viewDetail(image)"
                          title="查看詳情"
                        >
                          <template #icon>
                            <NIcon><EyeOutlined /></NIcon>
                          </template>
                        </NButton>
                        <NButton
                          circle
                          secondary
                          @click.stop="useAsReference(image)"
                          title="用作參考"
                        >
                          <template #icon>
                            <NIcon><SyncOutlined /></NIcon>
                          </template>
                        </NButton>
                        <NButton
                          circle
                          secondary
                          type="error"
                          @click.stop="deleteImage(image.id)"
                          title="刪除"
                        >
                          <template #icon>
                            <NIcon><DeleteOutlined /></NIcon>
                          </template>
                        </NButton>
                      </div>
                    </div>
                  </div>
                </NGridItem>
              </NGrid>
            </div>

            <div v-if="totalPages > 1" class="pagination-container">
              <NPagination
                v-model:page="currentPage"
                :page-count="totalPages"
                :page-size="pageSize"
                :item-count="filteredImages.length"
                show-size-picker
                :page-sizes="[12, 24, 36, 60]"
                @update:page-size="onPageSizeChange"
              />
            </div>
          </div>

          <NEmpty v-else description="沒有找到符合條件的圖像" />
        </NSpin>
      </div>
    </NLayoutContent>

    <!-- 圖像詳情對話框 -->
    <NModal
      v-model:show="showDetailModal"
      preset="card"
      title="圖像詳情"
      style="width: 90%; max-width: 1200px"
    >
      <div class="image-detail-content" v-if="selectedImage">
        <NGrid cols="1 m:2" x-gap="24" y-gap="24">
          <NGridItem>
            <div class="image-preview-container">
              <NImage
                :src="selectedImage.url"
                object-fit="contain"
                :alt="'選中的圖像'"
                class="detail-image"
              />
            </div>
          </NGridItem>
          <NGridItem>
            <div class="image-details">
              <h3>生成參數</h3>
              <div class="parameter-item">
                <span class="param-label">提示詞</span>
                <p class="param-value prompt-text">
                  {{ selectedImage.prompt || "無提示詞" }}
                </p>
              </div>

              <div class="parameter-item" v-if="selectedImage.params?.strength">
                <span class="param-label">強度</span>
                <span class="param-value">{{
                  selectedImage.params.strength
                }}</span>
              </div>

              <div class="parameter-item" v-if="selectedImage.params?.steps">
                <span class="param-label">步數</span>
                <span class="param-value">{{
                  selectedImage.params.steps
                }}</span>
              </div>

              <div class="parameter-item" v-if="selectedImage.params?.seed">
                <span class="param-label">種子</span>
                <span class="param-value">{{ selectedImage.params.seed }}</span>
              </div>

              <div class="parameter-item" v-if="selectedImage.params?.size">
                <span class="param-label">尺寸</span>
                <span class="param-value">{{ selectedImage.params.size }}</span>
              </div>

              <div class="parameter-item">
                <span class="param-label">創建時間</span>
                <span class="param-value">{{
                  formatDate(selectedImage.createdAt)
                }}</span>
              </div>

              <div class="parameter-item" v-if="selectedImage.projectName">
                <span class="param-label">所屬專案</span>
                <span class="param-value">{{ selectedImage.projectName }}</span>
              </div>

              <div class="image-tags-section">
                <h3>標籤</h3>
                <div v-if="isEditingTags" class="tag-input-area">
                  <NInput
                    v-model:value="newTagName"
                    placeholder="輸入標籤名稱"
                    @keydown.enter.prevent="addTagToImage"
                  />
                  <NButton type="primary" size="small" @click="addTagToImage"
                    >添加</NButton
                  >
                  <NButton size="small" @click="isEditingTags = false"
                    >取消</NButton
                  >
                </div>
                <div v-else class="tags-area">
                  <div class="tags-display">
                    <NTag
                      v-for="tag in selectedImage.tags"
                      :key="tag"
                      type="info"
                      closable
                      @close="removeTagFromImage(tag)"
                    >
                      {{ tag }}
                    </NTag>
                  </div>
                  <NButton
                    size="small"
                    class="add-tag-btn"
                    @click="isEditingTags = true"
                  >
                    <NIcon class="tag-icon"><PlusOutlined /></NIcon>
                    添加標籤
                  </NButton>
                </div>
              </div>
            </div>
          </NGridItem>
        </NGrid>
      </div>
      <template #footer>
        <div class="modal-footer">
          <NButton @click="showDetailModal = false">關閉</NButton>
          <NButton type="primary" @click="useAsReference(selectedImage)"
            >用作參考圖像</NButton
          >
          <NButton type="primary" @click="goToRevise(selectedImage)"
            >編輯圖像</NButton
          >
        </div>
      </template>
    </NModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useProjectStore } from "../stores/project";
import { useImageStore } from "../stores/image";
import { useMessage } from "naive-ui";
import {
  NLayoutContent,
  NButton,
  NGrid,
  NGridItem,
  NImage,
  NSpin,
  NEmpty,
  NModal,
  NSelect,
  NTag,
  NInput,
  NIcon,
  NPagination,
} from "naive-ui";
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  SyncOutlined,
  DeleteOutlined,
} from "@vicons/antd";
import TagSelector from "../components/ui/TagSelector.vue";
import GalleryPageHeader from "../components/headers/GalleryPageHeader.vue";

const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();
const message = useMessage();

// 頁面狀態
const loading = ref(false);
const showDetailModal = ref(false);
const selectedImage = ref(null);
const filterProject = ref(null);
const selectedTags = ref([]);
const isEditingTags = ref(false);
const newTagName = ref("");
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(24);

// 監聽篩選器變化，重置分頁
watch([filterProject, selectedTags, searchQuery], () => {
  currentPage.value = 1;
});

// 初始加載數據
onMounted(async () => {
  loading.value = true;
  try {
    // 加載項目
    await projectStore.fetchProjects();

    // 加載所有圖像 (在實際應用中可能需要分頁)
    // 為了演示，這裡我們使用已生成的圖像
    if (imageStore.generatedImages.length === 0) {
      // 模擬一些圖像數據
      imageStore.generatedImages = [
        {
          id: "sample-1",
          url: "https://picsum.photos/800/600?random=1",
          projectId: "1",
          prompt: "現代風格的智能手錶設計，藍色表帶，金屬邊框",
          tags: ["手錶", "科技", "藍色"],
          createdAt: new Date().toISOString(),
          params: {
            strength: 75,
            steps: 30,
            seed: 123456,
            size: "1024x1024",
          },
        },
        {
          id: "sample-2",
          url: "https://picsum.photos/800/600?random=2",
          projectId: "2",
          prompt: "未來感十足的客廳傢俱設計，白色和木質風格",
          tags: ["傢俱", "客廳", "未來"],
          createdAt: new Date().toISOString(),
          params: {
            strength: 80,
            steps: 35,
            seed: 234567,
            size: "1280x768",
          },
        },
        {
          id: "sample-3",
          url: "https://picsum.photos/800/600?random=3",
          projectId: "3",
          prompt: "夏季促銷活動海報，明亮的黃色和藍色主題",
          tags: ["海報", "夏季", "促銷"],
          createdAt: new Date().toISOString(),
          params: {
            strength: 70,
            steps: 25,
            seed: 345678,
            size: "768x1280",
          },
        },
      ];
    }
  } catch (error) {
    console.error("加載畫廊數據失敗:", error);
    message.error("加載圖像失敗，請稍後再試");
  } finally {
    loading.value = false;
  }
});

// 獲取所有可用項目選項
const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

// 獲取所有可用標籤
const availableTags = computed(() => {
  const tagsSet = new Set();

  // 從所有圖像中收集標籤
  imageStore.generatedImages.forEach((image) => {
    image.tags?.forEach((tag) => tagsSet.add(tag));
  });

  return Array.from(tagsSet);
});

// 根據篩選條件過濾圖像
const allFilteredImages = computed(() => {
  let images = imageStore.generatedImages;

  // 添加項目名稱到圖像
  images = images.map((image) => {
    const project = projectStore.getProjectById(image.projectId);
    return {
      ...image,
      projectName: project?.name,
    };
  });

  // 搜索篩選
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    images = images.filter(
      (image) =>
        image.projectName?.toLowerCase().includes(query) ||
        image.prompt?.toLowerCase().includes(query) ||
        image.tags?.some((tag) => tag.toLowerCase().includes(query))
    );
  }

  // 按項目篩選
  if (filterProject.value) {
    images = images.filter((image) => image.projectId === filterProject.value);
  }

  // 按標籤篩選
  if (selectedTags.value.length > 0) {
    images = images.filter((image) =>
      selectedTags.value.every((tag) => image.tags?.includes(tag))
    );
  }

  return images;
});

// 分頁
const totalPages = computed(() => {
  return Math.ceil(allFilteredImages.value.length / pageSize.value);
});

const filteredImages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return allFilteredImages.value.slice(start, end);
});

// 截斷文本
const truncateText = (text, maxLength) => {
  if (!text) return "";
  return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-TW", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 分頁大小變更處理
const onPageSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置到第一頁
};

// 查看圖像詳情
const viewDetail = (image) => {
  selectedImage.value = image;
  showDetailModal.value = true;
};

// 使用圖像作為參考
const useAsReference = (image) => {
  if (!image) return;

  // 設置參考圖像
  imageStore.setReferenceImages([image.url]);
  message.success("已將圖像設為參考");

  // 導航到設計輸入頁面
  router.push({
    name: "design-input",
    params: { projectId: "" },
  });
};

// 刪除圖像
const deleteImage = async (imageId) => {
  if (!imageId) return;

  if (!confirm("確定要刪除這張圖像嗎？此操作無法復原。")) return;

  loading.value = true;
  try {
    await imageStore.deleteImage(imageId);
    message.success("圖像已成功刪除");

    // 如果刪除的是當前選中的圖像，關閉詳情對話框
    if (selectedImage.value && selectedImage.value.id === imageId) {
      showDetailModal.value = false;
      selectedImage.value = null;
    }
  } catch (error) {
    console.error("刪除圖像失敗:", error);
    message.error("刪除圖像失敗，請稍後再試");
  } finally {
    loading.value = false;
  }
};

// 添加標籤
const addTagToImage = async () => {
  if (!selectedImage.value || !newTagName.value.trim()) return;

  try {
    const updatedTags = [...(selectedImage.value.tags || [])];

    if (!updatedTags.includes(newTagName.value.trim())) {
      updatedTags.push(newTagName.value.trim());

      await imageStore.saveImage(selectedImage.value.id, {
        tags: updatedTags,
      });

      // 更新選中的圖像
      selectedImage.value = imageStore.getImageById(selectedImage.value.id);
      message.success("標籤已添加");
    }

    newTagName.value = "";
    isEditingTags.value = false;
  } catch (error) {
    console.error("添加標籤失敗:", error);
    message.error("添加標籤失敗，請稍後再試");
  }
};

// 移除標籤
const removeTagFromImage = async (tag) => {
  if (!selectedImage.value) return;

  try {
    const updatedTags = (selectedImage.value.tags || []).filter(
      (t) => t !== tag
    );

    await imageStore.saveImage(selectedImage.value.id, {
      tags: updatedTags,
    });

    // 更新選中的圖像
    selectedImage.value = imageStore.getImageById(selectedImage.value.id);
    message.success("標籤已移除");
  } catch (error) {
    console.error("移除標籤失敗:", error);
    message.error("移除標籤失敗，請稍後再試");
  }
};

// 進入編輯頁面
const goToRevise = (image) => {
  if (!image) return;

  router.push({
    name: "designer-revision",
    params: {
      projectId: image.projectId || "temp",
      imageId: image.id,
    },
  });

  // 關閉詳情對話框
  showDetailModal.value = false;
};

// 前往創建新圖像頁面
const goToCreateImage = () => {
  router.push({ name: "design-input", params: { projectId: "" } });
};
</script>

<style scoped>
.gallery-page {
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-color, #f5f7fa);
}

.page-content {
  padding: 0 24px 24px 24px;
  width: 100%;
  box-sizing: border-box;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
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

.project-container,
.tags-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.filter-select {
  width: 200px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  width: 100%;
}

.gallery-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  aspect-ratio: 1/1;
  background-color: #f0f0f0;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.gallery-item:hover .image-overlay {
  opacity: 1;
}

.image-info {
  flex: 1;
}

.image-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.image-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.image-actions {
  display: flex;
  gap: 8px;
  margin-right: 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.image-detail-content {
  max-height: 80vh;
  overflow-y: auto;
}

.image-preview-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f0f0;
}

.detail-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.image-details {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.parameter-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  margin-right: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.param-label {
  font-weight: 500;
  margin-right: 12px;
  flex-shrink: 0;
  color: #666;
}

.prompt-text {
  word-break: break-word;
  margin: 0;
}

.image-tags-section {
  margin-top: auto;
  padding-top: 16px;
}

.tag-input-area {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
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

@media (max-width: 768px) {
  .page-content {
    padding: 0 16px 16px 16px;
  }

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
    width: 100%;
    gap: 12px;
  }

  .project-container,
  .tags-container {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-select {
    width: 100%;
  }

  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  .image-info h3 {
    font-size: 14px;
  }

  .image-actions {
    margin-right: 0;
  }

  .image-preview-container {
    height: auto;
  }

  .detail-image {
    max-height: 300px;
  }

  .tag-input-area {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
