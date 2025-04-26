<template>
  <div class="ai-generate-page">
    <AiGeneratePageHeader
      :loading="loading"
      :selectedImages="selectedImages"
      :hasSelectedImages="selectedImages.length > 0"
      @regenerate="regenerateSelected"
      @save-and-continue="saveAndContinue"
    />

    <NLayoutContent class="page-content">
      <div class="generation-info">
        <div class="prompt-display">
          <h3>提示詞</h3>
          <div class="prompt-input-container">
            <NInput
              v-model:value="editablePrompt"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              placeholder="輸入您的設計提示詞"
              @blur="updatePrompt"
              class="prompt-textarea"
            />
            <NButton
              class="optimize-button"
              type="primary"
              @click="optimizePrompt"
              title="優化提示詞"
            >
              <template #icon>
                <!-- <NIcon><MagicOutlined /></NIcon> -->
              </template>
              ★
            </NButton>
            <NButton
              class="generate-button"
              type="primary"
              @click="regenerateImages"
              title="生成圖片"
            >
              Generate
            </NButton>
          </div>
          <div
            class="selected-images-container"
            v-if="selectedImageIds.length > 0"
          >
            <div class="selected-count" @click="toggleSelectedImagesDropdown">
              你選擇了 {{ selectedImageIds.length }} 張圖片
              <NIcon class="dropdown-icon">{{
                showSelectedImagesDropdown ? "▲" : "▼"
              }}</NIcon>
            </div>
            <div
              class="selected-images-dropdown"
              v-if="showSelectedImagesDropdown"
            >
              <div
                v-for="id in selectedImageIds"
                :key="id"
                class="selected-image-item"
                @click="scrollToImage(id)"
              >
                圖片 ID: {{ id.substring(id.length - 6) }}
              </div>
            </div>
          </div>
          <div class="saved-count" v-if="savedImageIds.length > 0">
            你儲存了 {{ savedImageIds.length }} 張圖片
          </div>
          <NTag v-if="style" type="info">{{ style }}</NTag>
        </div>
        <NAlert title="提示" type="info" v-if="generatedImages.length">
          選擇您喜歡的設計結果，然後點擊「保存並繼續」進入設計師修訂階段
        </NAlert>
      </div>

      <NSpin
        :show="loading"
        description="AI 正在生成您的設計，這可能需要一些時間..."
      >
        <div v-if="generatedImages.length" class="images-section">
          <!-- 將生成的圖片按批次分組顯示 -->
          <div
            v-for="(batch, batchIndex) in imageBatches"
            :key="batchIndex"
            class="image-batch"
          >
            <!-- 批次標題和時間戳 -->
            <div class="generation-batch-title">
              <h4>生成於 {{ formatTimestamp(batch[0]?.createdAt) }}</h4>
            </div>
            <!-- 水平滑動容器 -->
            <div class="horizontal-scroll-container">
              <div class="images-row">
                <div
                  v-for="image in batch"
                  :key="image.id"
                  :class="[
                    'image-card',
                    { selected: selectedImageIds.includes(image.id) },
                    { highlighted: highlightedImageId === image.id },
                  ]"
                  @click="toggleImageSelection(image.id)"
                  class="image-card-container"
                  :data-image-id="image.id"
                >
                  <NImage
                    :src="image.url"
                    object-fit="cover"
                    :alt="'生成圖像'"
                    class="generated-image"
                    preview-disabled
                  />
                  <div class="image-overlay">
                    <div
                      class="selection-indicator"
                      v-if="selectedImageIds.includes(image.id)"
                    >
                      <NIcon size="24" class="check-icon">✓</NIcon>
                    </div>
                    <div class="image-actions">
                      <NButton
                        circle
                        quaternary
                        @click.stop="previewImage(image.url)"
                      >
                        <template #icon>👁️</template>
                      </NButton>
                      <NButton
                        circle
                        quaternary
                        @click.stop="downloadImage(image.url, image.id)"
                      >
                        <template #icon>↓</template>
                      </NButton>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <NEmpty
          v-else-if="!loading"
          description="尚未生成圖像，請先進行設計輸入"
        />
      </NSpin>
    </NLayoutContent>

    <!-- 圖像預覽對話框 -->
    <NModal
      v-model:show="showPreviewModal"
      preset="card"
      style="width: 80%; max-width: 1200px"
    >
      <template #header>
        <div class="preview-header">
          <h3>圖像預覽</h3>
        </div>
      </template>
      <div class="preview-content" v-if="previewImageUrl">
        <NImage
          :src="previewImageUrl"
          object-fit="contain"
          :alt="'預覽圖像'"
          class="preview-image"
        />
      </div>
    </NModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useProjectStore } from "../stores/project";
import { useImageStore } from "../stores/image";
import {
  NLayoutContent,
  NButton,
  NGrid,
  NGridItem,
  NImage,
  NSpin,
  NModal,
  NTag,
  NAlert,
  NEmpty,
  NIcon,
  NInput,
} from "naive-ui";
import { BulbOutlined } from "@vicons/antd";
import AiGeneratePageHeader from "../components/headers/AiGeneratePageHeader.vue";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();

// 頁面狀態
const loading = ref(false);
const projectId = computed(() => route.params.projectId);
const showPreviewModal = ref(false);
const previewImageUrl = ref("");
const selectedImages = ref([]);
const editablePrompt = ref("");

const updatePrompt = () => {
  imageStore.updateGenerationParams({ prompt: editablePrompt.value });
};

// 獲取生成參數
const generationParams = computed(() => imageStore.generationParams);
const prompt = computed(() => generationParams.value.prompt || "");
const style = computed(() => {
  const styleValue = generationParams.value.style;
  if (!styleValue) return "";

  const styleOptions = [
    { label: "現代簡約", value: "modern_minimalist" },
    { label: "復古懷舊", value: "retro_vintage" },
    { label: "自然有機", value: "natural_organic" },
    { label: "科技未來", value: "tech_futuristic" },
    { label: "工業風格", value: "industrial" },
    { label: "北歐風格", value: "scandinavian" },
    { label: "熱帶度假", value: "tropical_resort" },
  ];

  const found = styleOptions.find((option) => option.value === styleValue);
  return found ? found.label : styleValue;
});

// 獲取生成的圖像
const generatedImages = computed(() => imageStore.generatedImages);

// 按批次分組顯示圖像 - 根據創建時間的間隔分組
const imageBatches = computed(() => {
  if (!generatedImages.value.length) return [];

  // 創建批次數組
  const batches = [];
  let currentBatch = [];
  let lastTimestamp = null;

  // 對生成的圖像進行排序和分組
  generatedImages.value.forEach((image, index) => {
    const imageTimestamp = new Date(image.createdAt).getTime();

    // 如果是第一張圖片或時間接近上一張(同一批次)
    if (index === 0 || Math.abs(imageTimestamp - lastTimestamp) < 2000) {
      currentBatch.push(image);
    } else {
      // 開始新的批次
      batches.push([...currentBatch]);
      currentBatch = [image];
    }

    lastTimestamp = imageTimestamp;
  });

  // 添加最後一批
  if (currentBatch.length > 0) {
    batches.push(currentBatch);
  }

  return batches;
});

// 格式化時間戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
};

// 選中圖片ID數組
const selectedImageIds = ref([]);
const savedImageIds = ref([]);

// 監視選中的圖片ID更新選中圖片數組
selectedImages.value = computed(() => {
  return selectedImageIds.value
    .map((id) => {
      const index = generatedImages.value.findIndex((img) => img.id === id);
      return index !== -1 ? index : null;
    })
    .filter((index) => index !== null);
});

// 選中圖片下拉列表控制
const showSelectedImagesDropdown = ref(false);
const highlightedImageId = ref(null);

// 切換選中圖片下拉列表顯示狀態
const toggleSelectedImagesDropdown = () => {
  showSelectedImagesDropdown.value = !showSelectedImagesDropdown.value;
};

// 滾動到指定圖片並高亮顯示
const scrollToImage = (imageId) => {
  // 關閉下拉列表
  showSelectedImagesDropdown.value = false;

  // 設置高亮圖片ID
  highlightedImageId.value = imageId;

  // 延遲一下再滾動，確保DOM已更新
  setTimeout(() => {
    // 查找對應的圖片元素
    const imageElement = document.querySelector(`[data-image-id="${imageId}"]`);
    if (imageElement) {
      // 滾動到圖片位置
      imageElement.scrollIntoView({ behavior: "smooth", block: "center" });

      // 3秒後移除高亮效果
      setTimeout(() => {
        highlightedImageId.value = null;
      }, 3000);
    }
  }, 100);
};

// 初始載入數據
onMounted(() => {
  if (projectId.value && projectId.value !== "temp") {
    loading.value = true;
    projectStore
      .fetchProjectById(projectId.value)
      .finally(() => (loading.value = false));
  }

  // 初始化可編輯提示詞
  editablePrompt.value = prompt.value;

  if (generatedImages.value.length === 0 && !imageStore.loading) {
    regenerateImages();
  }
});

// 切換圖像選擇狀態
const toggleImageSelection = (id) => {
  if (selectedImageIds.value.includes(id)) {
    selectedImageIds.value = selectedImageIds.value.filter((i) => i !== id);
  } else {
    selectedImageIds.value.push(id);
  }
};

// 預覽圖像
const previewImage = (image) => {
  previewImageUrl.value = image;
  showPreviewModal.value = true;
};

// 下載圖像
const downloadImage = (imageUrl, id) => {
  const a = document.createElement("a");
  a.href = imageUrl;
  a.download = `generated-image-${id}.png`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

// 重新生成圖像
const regenerateImages = async () => {
  try {
    loading.value = true;
    await imageStore.generateImages({
      ...generationParams.value,
      projectId: projectId.value !== "temp" ? projectId.value : null,
    });
  } catch (error) {
    console.error("生成圖像失敗:", error);
  } finally {
    loading.value = false;
  }
};

// 重新生成選中項
const regenerateSelected = async () => {
  if (selectedImages.value.length === 0) return;

  try {
    loading.value = true;
    await imageStore.generateImages({
      ...generationParams.value,
      projectId: projectId.value !== "temp" ? projectId.value : null,
    });
    selectedImages.value = [];
  } catch (error) {
    console.error("重新生成失敗:", error);
  } finally {
    loading.value = false;
  }
};

// 保存並繼續
const saveAndContinue = () => {
  if (selectedImages.value.length === 0) return;
  const selectedImage = imageStore.generatedImages[selectedImages.value[0]];
  if (!selectedImage) return;
  router.push({
    name: "designer-revision",
    params: {
      projectId: projectId.value !== "temp" ? projectId.value : "temp",
      imageId: selectedImage.id,
    },
  });
};

// 優化提示詞
const optimizePrompt = async () => {
  if (!editablePrompt.value.trim()) {
    return;
  }

  try {
    loading.value = true;

    // 模擬API調用延遲
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // 簡單的優化邏輯示例
    const optimizedPrompt = `${editablePrompt.value.trim()} + 高質量、專業設計、細節豐富、協調的配色方案、均衡的構圖`;

    // 更新提示詞
    editablePrompt.value = optimizedPrompt;
    updatePrompt();

    // 在實際應用中，這裡可以調用後端API進行AI優化
  } catch (error) {
    console.error("優化提示詞失敗:", error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.ai-generate-page {
  min-height: 100vh; /* 改用最小高度而非固定高度 */
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative; /* 確保相對定位 */
  overflow-y: auto; /* 允許垂直滾動 */
}

.check-icon {
  color: white;
}

.image-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-content {
  display: flex;
  justify-content: center;
  min-height: 200px;
  max-height: 80vh;
  width: 100%;
}

.preview-image {
  max-height: 70vh;
  max-width: 100%;
  object-fit: contain;
}

.page-content {
  flex: 1;
  overflow-y: auto; /* 確保內容可滾動 */
  position: relative; /* 使用相對定位 */
  padding: 0 24px 24px 24px;
  width: 100%;
  box-sizing: border-box;
}

.generation-info {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.prompt-display {
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #2080f0;
  word-break: break-word;
}

.prompt-display h3 {
  margin-top: 0;
  margin-bottom: 8px;
}

.prompt-display p {
  margin: 0 0 8px 0;
  word-break: break-word;
}

.images-section {
  margin: 24px 0;
  width: 100%;
}

.generation-batch-title {
  margin-bottom: 16px;
}

.horizontal-scroll-container {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 16px; /* Space for scrollbar */
}

.images-row {
  display: flex;
  flex-direction: row;
  gap: 16px;
  min-width: min-content; /* Ensures the row doesn't wrap */
}

.image-card-container {
  flex: 0 0 auto;
  width: 300px; /* Fixed width for each card */
  height: 300px; /* Fixed height for consistent look */
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.image-card-container.selected {
  border-color: #2080f0;
  box-shadow: 0 0 0 2px rgba(32, 128, 240, 0.3);
}

.selection-indicator {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #2080f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prompt-input-container {
  display: flex;
  gap: 8px;
  width: 100%;
  margin-bottom: 8px;
}

.prompt-textarea {
  flex-grow: 1;
  text-align: left;
}

.optimize-button {
  height: auto;
  display: flex;
  align-items: center;
  align-self: stretch;
  white-space: nowrap;
}

.generate-button {
  height: auto;
  display: flex;
  align-items: center;
  align-self: stretch;
  white-space: nowrap;
  background-color: #18a058; /* Green color */
  color: white; /* Ensuring text is white for contrast */
  border-color: #18a058;
}

.generate-button:hover {
  background-color: #36ad6a; /* Slightly lighter green for hover state */
  border-color: #36ad6a;
}

.selected-count {
  margin-top: 8px;
  font-size: 0.9em;
  color: #2080f0;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  user-select: none;
}

.dropdown-icon {
  margin-left: 8px;
  font-size: 0.8em;
}

.selected-images-container {
  position: relative;
}

.selected-images-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-width: 240px;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.selected-image-item {
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.selected-image-item:hover {
  background-color: #f5f5f5;
  color: #2080f0;
}

.image-card-container.highlighted {
  border: 3px solid #ff4d4f;
  animation: glow 1.5s ease-in-out infinite alternate;
  box-shadow: 0 0 20px rgba(255, 77, 79, 0.7);
  z-index: 2;
}

@keyframes glow {
  from {
    box-shadow: 0 0 5px rgba(255, 77, 79, 0.7);
  }
  to {
    box-shadow: 0 0 20px rgba(255, 77, 79, 0.9), 0 0 30px rgba(255, 77, 79, 0.5);
  }
}

.saved-count {
  margin-top: 4px;
  font-size: 0.9em;
  color: #18a058; /* Green color to match the Generate button */
  font-weight: 500;
  text-align: left;
}

@media (max-width: 768px) {
  .page-content {
    padding: 0 16px 16px 16px;
  }

  .images-row {
    gap: 12px;
  }

  .image-card-container {
    width: 220px;
    height: 220px;
  }
}
</style>
