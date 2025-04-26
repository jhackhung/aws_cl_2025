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
          <p>{{ prompt }}</p>
          <NTag v-if="style" type="info">{{ style }}</NTag>
        </div>
        <NAlert title="提示" type="info" v-if="generatedImages.length">
          選擇您喜歡的設計結果，然後點擊「保存並繼續」進入設計師修訂階段
        </NAlert>
      </div>
      
      <NSpin :show="loading" description="AI 正在生成您的設計，這可能需要一些時間...">
        <div v-if="generatedImages.length" class="images-grid">
          <NGrid cols="1 s:2 m:3 l:4 xl:5 2xl:6" x-gap="16" y-gap="16">
            <NGridItem v-for="(image, index) in generatedImages" :key="index">
              <div 
                :class="['image-card', { 'selected': selectedImages.includes(index) }]"
                @click="toggleImageSelection(index)"
              >
                <NImage
                  :src="image"
                  object-fit="cover"
                  :alt="'生成圖像 ' + (index + 1)"
                  class="generated-image"
                  preview-disabled
                />
                <div class="image-overlay">
                  <div class="selection-indicator">
                    <NIcon size="24" class="check-icon" v-if="selectedImages.includes(index)">✓</NIcon>
                  </div>
                  <div class="image-actions">
                    <NButton circle quaternary @click.stop="previewImage(image)">
                      <template #icon>👁️</template>
                    </NButton>
                    <NButton circle quaternary @click.stop="downloadImage(image, index)">
                      <template #icon>↓</template>
                    </NButton>
                  </div>
                </div>
              </div>
            </NGridItem>
          </NGrid>
        </div>
        <NEmpty v-else-if="!loading" description="尚未生成圖像，請先進行設計輸入" />
      </NSpin>
    </NLayoutContent>
    
    <!-- 圖像預覽對話框 -->
    <NModal v-model:show="showPreviewModal" preset="card" style="width: 80%; max-width: 1200px;">
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
  NIcon
} from "naive-ui";
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
  
  const found = styleOptions.find(option => option.value === styleValue);
  return found ? found.label : styleValue;
});

// 獲取生成的圖像
const generatedImages = computed(() => imageStore.generatedImages.map(img => img.url));

// 初始載入數據
onMounted(() => {
  if (projectId.value && projectId.value !== "temp") {
    loading.value = true;
    projectStore.fetchProjectById(projectId.value).finally(() => (loading.value = false));
  }

  if (generatedImages.value.length === 0 && !imageStore.loading) {
    regenerateImages();
  }
});

// 切換圖像選擇狀態
const toggleImageSelection = (index) => {
  if (selectedImages.value.includes(index)) {
    selectedImages.value = selectedImages.value.filter(i => i !== index);
  } else {
    selectedImages.value.push(index);
  }
};

// 預覽圖像
const previewImage = (image) => {
  previewImageUrl.value = image;
  showPreviewModal.value = true;
};

// 下載圖像
const downloadImage = (imageUrl, index) => {
  const a = document.createElement('a');
  a.href = imageUrl;
  a.download = `generated-image-${index + 1}.png`;
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
      imageId: selectedImage.id
    }
  });
};
</script>

<style scoped>
.ai-generate-page {
  min-height: 100vh;
  width: 100%;
  background-color: #f5f7fa;
}

.check-icon {
  color: white;
}

.image-actions {
  display: flex;
  gap: 8px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-content {
  display: flex;
  justify-content: center;
  min-height: 200px;
  max-height: 80vh;
}

.preview-image {
  max-height: 70vh;
  object-fit: contain;
}

.page-content {
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
}

.prompt-display h3 {
  margin-top: 0;
  margin-bottom: 8px;
}

.prompt-display p {
  margin: 0 0 8px 0;
  word-break: break-word;
}

.images-grid {
  width: 100%;
}

.image-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 3px solid transparent;
}

.image-card.selected {
  border-color: #2080f0;
}

.generated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 16px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  display: flex;
  justify-content: space-between;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.selection-indicator {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2080f0;
  color: white;
}
</style>