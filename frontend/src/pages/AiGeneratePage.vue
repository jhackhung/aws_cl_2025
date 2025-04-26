<template>
  <div class="ai-generate-page">
    <NLayoutHeader class="page-header">
      <div class="header-content">
        <div class="header-left">
          <NButton @click="goBack" quaternary circle>
            <template #icon>
              <div class="icon-container">&#8592;</div>
            </template>
          </NButton>
          <h1>AI 生成結果</h1>
        </div>
        <div class="header-right">
          <NButton @click="regenerate" :loading="loading" :disabled="selectedImages.length === 0">
            重新生成選中項
          </NButton>
          <NButton type="primary" @click="saveAndContinue" :disabled="!hasSelectedImages">
            保存並繼續
          </NButton>
        </div>
      </div>
    </NLayoutHeader>
    
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
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NButton,
  NProgress,
  NGrid,
  NGridItem,
  NImage,
  NSpin,
  NCard,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NTag,
  NAlert,
  NEmpty,
  NIcon
} from "naive-ui";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();

// 頁面狀態
const loading = ref(false);
const projectId = computed(() => route.params.projectId);
const selectedImage = ref(null);
const showPromptModal = ref(false);
const editedPrompt = ref("");
const editedNegativePrompt = ref("");
const isEditingTags = ref(false);
const newTagName = ref("");
const selectedImages = ref([]);

// 獲取生成參數
const generationParams = computed(() => imageStore.generationParams);

// 獲取生成的圖像
const generatedImages = computed(() => {
  return imageStore.generatedImages.filter(
    (img) =>
      img.projectId === projectId.value ||
      (!img.projectId && projectId.value === "temp")
  );
});

// 生成進度文本
const generateProgressText = computed(() => {
  const progress = imageStore.generationProgress;

  if (progress < 25) {
    return "正在分析提示詞...";
  } else if (progress < 50) {
    return "正在生成圖像輪廓...";
  } else if (progress < 75) {
    return "正在添加細節...";
  } else if (progress < 100) {
    return "最終潤色中...";
  } else {
    return "生成完成！";
  }
});

// 初始載入數據
onMounted(() => {
  if (projectId.value && projectId.value !== "temp") {
    loading.value = true;
    projectStore
      .fetchProjectById(projectId.value)
      .finally(() => (loading.value = false));
  }

  // 如果沒有圖像，開始生成
  if (generatedImages.value.length === 0 && !imageStore.loading) {
    regenerateImages();
  }
});

// 選擇圖像
const selectImage = (image) => {
  selectedImage.value = image;
  imageStore.selectImage(image);
};

// 返回設計輸入頁面
const goBack = () => {
  router.push({
    name: "design-input",
    params: { projectId: projectId.value !== "temp" ? projectId.value : "" },
  });
};

// 重新生成圖像
const regenerateImages = async () => {
  try {
    await imageStore.generateImages({
      ...generationParams.value,
      projectId: projectId.value !== "temp" ? projectId.value : null,
    });
  } catch (error) {
    console.error("生成圖像失敗:", error);
  }
};

// 編輯提示詞
const editPrompt = () => {
  editedPrompt.value = generationParams.value.prompt;
  editedNegativePrompt.value = generationParams.value.negativePrompt;
  showPromptModal.value = true;
};

// 應用提示詞編輯
const applyPromptEdit = async () => {
  imageStore.setGenerationParams({
    prompt: editedPrompt.value,
    negativePrompt: editedNegativePrompt.value,
  });

  showPromptModal.value = false;
  await regenerateImages();
};

// 保存圖像到畫廊
const saveImageToGallery = async (image) => {
  if (!image) return;

  try {
    if (projectId.value && projectId.value !== "temp") {
      // 如果圖像還沒有關聯到項目，更新它
      if (!image.projectId) {
        await imageStore.saveImage(image.id, {
          projectId: projectId.value,
        });
      }

      // 更新項目中的圖像
      const currentProject = projectStore.currentProject;
      if (currentProject) {
        const images = currentProject.images || [];
        if (!images.some((img) => img.id === image.id)) {
          await projectStore.updateProject(projectId.value, {
            images: [...images, { id: image.id, url: image.url }],
          });
        }
      }
    }

    // 這裡可以添加更多保存到畫廊的邏輯
    console.log("圖像已保存到畫廊");
  } catch (error) {
    console.error("保存圖像失敗:", error);
  }
};

// 刪除圖像
const deleteImage = async (imageId) => {
  if (!imageId) return;

  try {
    await imageStore.deleteImage(imageId);

    // 如果刪除的是當前選中的圖像，清除選擇
    if (selectedImage.value && selectedImage.value.id === imageId) {
      selectedImage.value = null;
    }
  } catch (error) {
    console.error("刪除圖像失敗:", error);
  }
};

// 使用選中圖像的相同參數重新生成
const useAsSeed = async () => {
  if (!selectedImage.value) return;

  try {
    imageStore.setGenerationParams({
      seed: selectedImage.value.params.seed,
      strength: selectedImage.value.params.strength,
      steps: selectedImage.value.params.steps,
    });

    await regenerateImages();
  } catch (error) {
    console.error("使用種子生成失敗:", error);
  }
};

// 使用選中圖像作為參考圖像
const useAsReferenceImage = () => {
  if (!selectedImage.value) return;

  // 設置參考圖像
  imageStore.setReferenceImages([selectedImage.value.url]);

  // 返回設計輸入頁面
  goBack();
};

// 進入圖像編輯/修訂頁面
const goToRevision = () => {
  if (!selectedImage.value) return;

  router.push({
    name: "designer-revision",
    params: {
      projectId: projectId.value !== "temp" ? projectId.value : "temp",
      imageId: selectedImage.value.id,
    },
  });
};

// 添加標籤到圖像
const addTagToImage = async () => {
  if (!selectedImage.value || !newTagName.value.trim()) return;

  try {
    const updatedTags = [...(selectedImage.value.tags || [])];

    if (!updatedTags.includes(newTagName.value.trim())) {
      updatedTags.push(newTagName.value.trim());

      await imageStore.saveImage(selectedImage.value.id, {
        tags: updatedTags,
      });

      selectedImage.value = imageStore.getImageById(selectedImage.value.id);
    }

    newTagName.value = "";
    isEditingTags.value = false;
  } catch (error) {
    console.error("添加標籤失敗:", error);
  }
};

// 從圖像中移除標籤
const removeTagFromImage = async (tag) => {
  if (!selectedImage.value) return;

  try {
    const updatedTags = (selectedImage.value.tags || []).filter(
      (t) => t !== tag
    );

    await imageStore.saveImage(selectedImage.value.id, {
      tags: updatedTags,
    });

    selectedImage.value = imageStore.getImageById(selectedImage.value.id);
  } catch (error) {
    console.error("移除標籤失敗:", error);
  }
};

// 切換圖像選擇狀態
const toggleImageSelection = (index) => {
  if (selectedImages.value.includes(index)) {
    selectedImages.value = selectedImages.value.filter(i => i !== index);
  } else {
    selectedImages.value.push(index);
  }
};

// 重新生成選中項
const regenerate = () => {
  selectedImages.value.forEach(index => {
    const image = generatedImages.value[index];
    regenerateImages(image);
  });
};

// 保存並繼續
const saveAndContinue = () => {
  // 實現保存並繼續的邏輯
};
</script>

<style scoped>
.ai-generate-page {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.icon-container {
  font-size: 18px;
  line-height: 1;
}

.page-content {
  padding: 24px;
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
</style>
