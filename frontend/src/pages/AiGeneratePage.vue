<template>
  <div class="ai-generate-page">
    <AiGeneratePageHeader
      :loading="loading"
      :selectedImages="savedImageIds"
      :hasSelectedImages="savedImageIds.length > 0"
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
            <!-- <NButton
              class="save-button"
              type="primary"
              @click="saveImages"
              :disabled="savedImageIds.length === 0"
              title="保存圖片"
            >
              Save ({{ savedImageIds.length }})
            </NButton> -->
          </div>

          <!-- Images status bars -->
          <div class="image-status-container">
            <div
              class="status-block selected-status-block"
              v-if="selectedImageIds.length > 0"
              @click="toggleSelectedImagesDropdown"
            >
              你選擇了 {{ selectedImageIds.length }} 張圖片 (
              選擇加入下一次圖片生成 )
              <NIcon class="dropdown-icon">{{
                showSelectedImagesDropdown ? "▲" : "▼"
              }}</NIcon>

              <div
                class="status-dropdown selected-images-dropdown"
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

            <div
              class="status-block saved-status-block"
              v-if="savedImageIds.length > 0"
              @click="toggleSavedImagesDropdown"
            >
              你儲存了 {{ savedImageIds.length }} 張圖片 ( 加入至個人品牌資料庫
              )
              <NIcon class="dropdown-icon">{{
                showSavedImagesDropdown ? "▲" : "▼"
              }}</NIcon>

              <div
                class="status-dropdown saved-images-dropdown"
                v-if="showSavedImagesDropdown"
              >
                <div
                  v-for="id in savedImageIds"
                  :key="id"
                  class="saved-image-item"
                  @click="scrollToImage(id)"
                >
                  圖片 ID: {{ id.substring(id.length - 6) }}
                </div>
              </div>
            </div>
          </div>

          <NTag v-if="style" type="info">{{ style }}</NTag>
        </div>

        <!-- 顯示進度條或提示訊息，根據載入狀態 -->
        <div v-if="loading" class="progress-container">
          <NProgress
            type="line"
            :percentage="generationProgress"
            :indicator-placement="'inside'"
            :height="12"
            processing
          />
          <div class="progress-text">
            {{ generationProgress >= 100 ? "處理完成" : "正在生成圖片中..." }}
            {{ generationProgress.toFixed(0) }}%
          </div>
        </div>
        <NAlert title="提示" type="info" v-else-if="generatedImages.length">
          選擇您喜歡的設計結果，然後點擊「保存並繼續」進入設計師修訂階段
        </NAlert>
      </div>

      <!-- 圖片部分，不再包在NSpin中 -->
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
                  object-fit="contain"
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
                  <div class="bottom-right-actions">
                    <NButton
                      circle
                      quaternary
                      @click.stop="previewImage(image.url)"
                      class="action-button"
                    >
                      <template #icon>👁️</template>
                    </NButton>
                    <NButton
                      circle
                      quaternary
                      @click.stop="toggleSaveImage(image.id)"
                      :class="[
                        'action-button',
                        { saved: savedImageIds.includes(image.id) },
                      ]"
                    >
                      <template #icon>💾</template>
                    </NButton>
                    <div
                      class="save-indicator"
                      v-if="savedImageIds.includes(image.id)"
                    >
                      <NIcon size="24" class="save-icon">✓</NIcon>
                    </div>
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
import { ref, computed, onMounted, onUnmounted } from "vue";
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
  useMessage,
} from "naive-ui";
import { BulbOutlined } from "@vicons/antd";
import AiGeneratePageHeader from "../components/headers/AiGeneratePageHeader.vue";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();
const message = (window.$message = useMessage());

const loading = ref(false);
const projectId = computed(() => route.params.projectId);
const showPreviewModal = ref(false);
const previewImageUrl = ref("");
const selectedImages = ref([]);
const editablePrompt = ref("");

// 添加進度條相關的狀態
const generationProgress = ref(0);
const progressTimer = ref(null);

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
const showSavedImagesDropdown = ref(false);
const highlightedImageId = ref(null);

// 切換選中圖片下拉列表顯示狀態
const toggleSelectedImagesDropdown = () => {
  showSelectedImagesDropdown.value = !showSelectedImagesDropdown.value;
};

const toggleSavedImagesDropdown = () => {
  showSavedImagesDropdown.value = !showSavedImagesDropdown.value;
};

// 滾動到指定圖片並高亮顯示
const scrollToImage = (imageId) => {
  // 關閉下拉列表
  showSelectedImagesDropdown.value = false;
  showSavedImagesDropdown.value = false;

  // 設置高亮圖片ID
  highlightedImageId.value = imageId;

  // 延遲一下再滾动，確保DOM已更新
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
onMounted(async () => {
  if (projectId.value && projectId.value !== "temp") {
    loading.value = true;
    projectStore
      .fetchProjectById(projectId.value)
      .finally(() => (loading.value = false));
  }

  // 初始化可編輯提示詞
  editablePrompt.value = prompt.value;

  // 查找 taskId （從路由參數或state）
  const taskId =
    route.query.taskId ||
    route.params.taskId ||
    (route.state && route.state.taskId) ||
    (route.fullPath &&
      route.fullPath.includes("taskId=") &&
      route.fullPath.split("taskId=")[1].split("&")[0]);

  console.log("Task ID from previous page:", taskId);

  if (taskId) {
    await fetchImagesFromTaskId(taskId);
  } else {
    console.log("No taskId found, showing default or empty state");
  }
});

const fetchImagesFromTaskId = async (taskId) => {
  if (!taskId) return;

  try {
    loading.value = true;
    console.log("Fetching images for task:", taskId);

    // 重置進度條並開始進度動畫
    generationProgress.value = 0;
    startProgressAnimation();

    // 訪問 API 端點獲取任務結果
    const response = await fetch(
      `https://ec2.sausagee.party/img/result/${taskId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API returned status ${response.status}`);
    }

    const data = await response.json();
    console.log("Task result:", data);

    // 檢查任務狀態
    if (data.status === "done" && data.urls && data.urls.length > 0) {
      // 設置進度為100%
      generationProgress.value = 100;
      clearProgressAnimation();

      // 構建圖像物件並添加到生成的圖像集合中
      const newImages = data.urls.map((url, index) => {
        // 從 URL 中獲取圖像 ID
        const id =
          url.split("/").pop().split(".")[0] || `task-${taskId}-${index}`;

        return {
          id,
          url: url.startsWith("http")
            ? url
            : `https://ec2.sausagee.party${url}`,
          prompt: editablePrompt.value,
          projectId: projectId.value !== "temp" ? projectId.value : null,
          parameters: {
            ...generationParams.value,
            taskId: taskId,
          },
          createdAt: new Date().toISOString(),
        };
      });

      // 添加到 image store 取代原有的 dummy data
      if (typeof imageStore.addGeneratedImages === "function") {
        // 如果 store 有 addGeneratedImages 方法
        imageStore.addGeneratedImages(newImages);
      } else {
        // 否則直接更新 generatedImages
        imageStore.generatedImages = [
          ...newImages,
          ...imageStore.generatedImages,
        ];
      }

      console.log(`成功載入 ${newImages.length} 張生成的圖像`);
    } else if (data.status === "queued" || data.status === "processing") {
      // 如果任務仍在進行中，設置輪詢 - 不顯示message提示
      console.log("圖像生成任務正在進行中，請稍候...");

      // 增加進度顯示
      generationProgress.value = Math.min(generationProgress.value + 5, 90);

      // 繼續輪詢
      setTimeout(() => fetchImagesFromTaskId(taskId), 1500);
    } else {
      // 任務失敗或其他狀態
      clearProgressAnimation();
      message.error(`圖像生成任務狀態: ${data.status}`);
    }
  } catch (error) {
    console.error("Fetching images failed:", error);
    message.error("獲取生成的圖像失敗: " + error.message);
    clearProgressAnimation();
  } finally {
    if (generationProgress.value >= 100) {
      loading.value = false;
      clearProgressAnimation();
    }
  }
};

// 啟動進度條動畫
const startProgressAnimation = () => {
  // 清除可能存在的計時器
  clearProgressAnimation();

  // 設置初始進度
  generationProgress.value = 0;

  // 計算每秒大約應增加的進度 (95% / 20秒 ≈ 4.75%/秒)
  const baseIncrement = 4.75;

  // 設置新的計時器，使用隨機增量模擬進度
  progressTimer.value = setInterval(() => {
    // 根據當前進度決定增量策略
    let increment;

    if (generationProgress.value < 60) {
      // 前60%進度：較大的隨機增量，進展較快
      increment = (Math.random() * 0.8 + 0.6) * baseIncrement; // 0.6~1.4倍基本增量
    } else if (generationProgress.value < 85) {
      // 60%-85%進度：中等隨機增量
      increment = (Math.random() * 0.6 + 0.4) * baseIncrement; // 0.4~1.0倍基本增量
    } else if (generationProgress.value < 95) {
      // 85%-95%進度：較小的隨機增量
      increment = (Math.random() * 0.4 + 0.2) * baseIncrement; // 0.2~0.6倍基本增量
    } else {
      // 95%以上：極慢增長
      increment = (Math.random() * 0.1 + 0.05) * baseIncrement; // 0.05~0.15倍基本增量
    }

    // 增加進度
    generationProgress.value += increment;

    // 處理邊界情況
    if (generationProgress.value >= 99.5) {
      generationProgress.value = 99.5;
      clearProgressAnimation();
    }

    // 如果API返回完成，則立即設為100%
    if (generationProgress.value >= 100) {
      generationProgress.value = 100;
      clearProgressAnimation();
    }
  }, 1000); // 每秒更新一次
};

// 清除進度条計時器
const clearProgressAnimation = () => {
  if (progressTimer.value) {
    clearInterval(progressTimer.value);
    progressTimer.value = null;
  }
};

// 在API成功返回後設置為100%
const completeProgress = () => {
  generationProgress.value = 100;
  clearProgressAnimation();
};

// 組件卸載時清理計時器
onUnmounted(() => {
  clearProgressAnimation();
});

// 切換圖像選擇狀態
const toggleImageSelection = (id) => {
  if (selectedImageIds.value.includes(id)) {
    selectedImageIds.value = selectedImageIds.value.filter((i) => i !== id);
  } else {
    selectedImageIds.value.push(id);
  }
};

// 切換圖像儲存狀態
const toggleSaveImage = (id) => {
  if (savedImageIds.value.includes(id)) {
    savedImageIds.value = savedImageIds.value.filter((i) => i !== id);
  } else {
    savedImageIds.value.push(id);
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
  // 檢查是否有提示詞
  if (!editablePrompt.value.trim()) {
    message.warning("請先輸入提示詞");
    return;
  }

  try {
    loading.value = true;
    // 重置進度條
    generationProgress.value = 0;
    // 開始進度條動畫
    startProgressAnimation();

    // 創建表單數據
    const formData = new FormData();
    formData.append("batch_count", generationParams.value.batchCount || 4);
    formData.append("text", editablePrompt.value);
    formData.append("cfg_scale", generationParams.value.cfgScale || 7.5);

    // 如果有種子值且不是隨機種子(-1)，則添加
    if (generationParams.value.seed && generationParams.value.seed !== -1) {
      formData.append("seed", generationParams.value.seed);
    }

    // 如果有選中的圖片，先儲存這些圖片並獲取真正的ID
    const savedImageRefs = [];

    // 處理選中的圖片作為參考圖像
    if (selectedImageIds.value.length > 0) {
      for (const selectedId of selectedImageIds.value) {
        // 找到對應的圖片對象
        const selectedImage = generatedImages.value.find(
          (img) => img.id === selectedId
        );
        if (selectedImage) {
          try {
            // 呼叫 /img/save API 儲存圖片
            const saveResponse = await fetch(
              "https://ec2.sausagee.party/img/save",
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  url: selectedImage.url,
                  prompt: selectedImage.prompt || editablePrompt.value,
                  parameters: selectedImage.parameters || {},
                }),
              }
            );

            if (saveResponse.ok) {
              const savedData = await saveResponse.json();
              // 把返回的ID加入參考圖片清單
              if (savedData && savedData.id) {
                savedImageRefs.push(savedData.id);
                console.log(`已儲存參考圖片 ID: ${savedData.id}`);
              }
            } else {
              console.error(`儲存圖片失敗: ${saveResponse.status}`);
            }
          } catch (saveError) {
            console.error("儲存參考圖片時發生錯誤:", saveError);
          }
        }
      }
    }

    // 處理儲存後的圖片ID作為參考圖像
    if (savedImageRefs.length > 0) {
      // 將儲存的圖片ID數組轉換為JSON字符串
      formData.append("imgs", JSON.stringify(savedImageRefs));

      // 添加相似度強度參數 (默認為0.5)
      formData.append(
        "similarityStrength",
        generationParams.value.similarityStrength || 0.5
      );
    }

    // 添加尺寸參數與其他參數 - 作為單獨的字段，不是JSON
    const height = generationParams.value.height || 1024;
    const width = generationParams.value.width || 1024;
    const steps = generationParams.value.steps || 30;

    // 直接添加參數，不將其整合為JSON字符串
    formData.append("parameters[width]", width);
    formData.append("parameters[height]", height);
    formData.append("parameters[steps]", steps);

    // 如果有風格，添加風格參數
    if (generationParams.value.style) {
      formData.append("parameters[style]", generationParams.value.style);
    }
    // 發送請求到 API 端點
    const response = await fetch("https://ec2.sausagee.party/img/generate", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("生成圖像失敗:", response.status, errorText);
      throw new Error(`API 錯誤: ${response.status}`);
    }

    const data = await response.json();

    // 檢查回應中是否包含任務 ID
    if (!data.id) {
      throw new Error("API 返回的數據中缺少任務 ID");
    }

    const taskId = data.id;
    console.log("生成任務已啟動，任務 ID:", taskId);

    // 保存生成參數到 store (更新當前使用的參數)
    imageStore.updateGenerationParams({
      prompt: editablePrompt.value,
      style: generationParams.value.style,
      size: generationParams.value.size,
      steps: generationParams.value.steps || 30,
      cfgScale: generationParams.value.cfgScale || 7.5,
      seed: generationParams.value.seed || -1,
      batchCount: generationParams.value.batchCount || 4,
      taskId: taskId,
    });

    // 使用已有的 fetchImagesFromTaskId 函數來輪詢結果
    await fetchImagesFromTaskId(taskId);

    // 清除選中的圖片 (只留下那些已被保存的)
    selectedImageIds.value = selectedImageIds.value.filter((id) =>
      savedImageIds.value.includes(id)
    );

    message.success("圖像生成成功");
  } catch (error) {
    console.error("生成圖像失敗:", error);
    message.error("生成圖像失敗: " + (error.message || "未知錯誤"));
    clearProgressAnimation();
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

const saveImages = () => {
  if (savedImageIds.value.length === 0) {
    // 如果沒有已儲存的圖片，顯示提示並返回
    window.$message.warning("請先選擇並儲存至少一張圖片");
    return;
  }

  try {
  } catch (error) {
    console.error("保存圖片失敗:", error);
  } finally {
    // 清空選擇的圖片ID
    selectedImageIds.value = [];
  }
};

// 保存並繼續
const saveAndContinue = async () => {
  if (savedImageIds.value.length === 0) {
    message.warning("請先儲存至少一張圖片");
    return;
  }

  try {
    loading.value = true;
    // 獲取儲存的第一張圖片
    const imageId = savedImageIds.value[0];
    const savedImage = generatedImages.value.find((img) => img.id === imageId);

    if (!savedImage) {
      message.error("找不到已儲存的圖片，請重新儲存");
      return;
    }

    console.log("準備保存圖片:", savedImage);

    // 創建要發送的JSON數據，而不是FormData
    const requestData = {
      projectId: projectId.value !== "temp" ? projectId.value : "temp",
      url: savedImage.url, // 直接傳URL而不是檔案本身
      prompt: savedImage.prompt || editablePrompt.value,
    };

    // 添加參數如果有的話
    if (savedImage.parameters) {
      requestData.parameters = savedImage.parameters;
    }

    console.log("發送的JSON數據:", requestData);

    // 發送JSON格式請求
    const response = await fetch("https://ec2.sausagee.party/img/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      console.error("保存圖片失敗狀態碼:", response.status);
      const errorText = await response.text();
      console.error("保存圖片失敗回應:", errorText);
      throw new Error(`保存圖片失敗: ${response.status}`);
    }

    // 獲取服務器返回的數據，包含真實 ID
    const serverResponse = await response.json();
    console.log("服務器回應:", serverResponse);

    const realImageId = serverResponse.id || savedImage.id;
    console.log("服務器保存的圖片 ID:", realImageId);

    // 將完整的圖片對象更新為包含服務器返回的 ID
    const finalImage = {
      ...savedImage,
      id: realImageId,
      serverSaved: true,
    };

    // 將圖片數據保存到 store 或 localStorage
    if (typeof imageStore.selectedImage !== "undefined") {
      imageStore.selectedImage = finalImage;
    }

    // 無論如何都保存到 localStorage 作為備份
    localStorage.setItem("selectedImage", JSON.stringify(finalImage));

    // 導航到設計師修訂頁面，使用真實的圖片 ID
    router.push({
      name: "designer-revision",
      params: {
        projectId: projectId.value !== "temp" ? projectId.value : "temp",
        imageId: realImageId,
      },
      state: {
        selectedImage: finalImage,
      },
    });

    message.success("圖片已保存，正在進入設計修訂頁面");
  } catch (error) {
    console.error("導航到設計師修訂頁面失敗:", error);
    message.error("導航失敗: " + (error.message || "未知錯誤"));
  } finally {
    loading.value = false;
  }
};

// 優化提示詞
const optimizePrompt = async () => {
  if (!editablePrompt.value.trim()) {
    return;
  }

  try {
    loading.value = true;

    const response = await fetch("https://ec2.sausagee.party/txt/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        text: editablePrompt.value, // 正確使用 editablePrompt.value
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("優化提示詞失敗:", response.status, errorText);
      throw new Error(`API錯誤: ${response.status}`);
    }

    // 解析 JSON 回應
    const data = await response.json();

    if (data && data.text) {
      // 直接設置 editablePrompt.value
      editablePrompt.value = data.text;
      console.log("提示詞已優化:", data.text);
      // 更新全局提示詞
      updatePrompt();
      // 顯示成功提示
      message.success("提示詞優化成功");
    } else {
      console.warn("API返回了未預期的數據格式:", data);
      message.warning("優化提示詞時獲得未預期的回應格式");
    }
  } catch (error) {
    console.error("優化提示詞失敗:", error);
    message.error("優化提示詞失敗: " + (error.message || "未知錯誤"));
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

.generated-image {
  width: 100%;
  height: 100%;
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
  background-color: #f5f5f5; /* Add a background color to show around the image */
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-card-container.selected {
  border-color: #2080f0;
  box-shadow: 0 0 0 2px rgba(32, 128, 240, 0.3);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.3) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.image-card-container:hover .image-overlay {
  opacity: 1;
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

.save-button {
  height: auto;
  display: flex;
  align-items: center;
  align-self: stretch;
  white-space: nowrap;
  background-color: #f0c040; /* Yellow color */
  color: white; /* Ensuring text is white for contrast */
  border-color: #f0c040;
}

.save-button:hover {
  background-color: #f0d060; /* Slightly lighter yellow for hover state */
  border-color: #f0d060;
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

.saved-images-container {
  position: relative;
}

.saved-images-dropdown {
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

.saved-image-item {
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.saved-image-item:hover {
  background-color: #f5f5f5;
  color: #18a058;
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

.bottom-right-actions {
  position: absolute;
  bottom: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
}

.bottom-right-actions .action-button {
  background-color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s;
}

.bottom-right-actions .action-button.saved {
  background-color: #18a058;
  color: white;
}

.bottom-right-actions .action-button:hover {
  background-color: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.save-indicator {
  position: absolute;
  bottom: 8px;
  right: 48px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #18a058;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-icon {
  color: white;
}

/* New styles for horizontal status blocks */
.image-status-container {
  display: flex;
  width: 100%;
  margin: 12px 0;
  gap: 12px;
}

.status-block {
  flex: 1;
  padding: 10px 16px;
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.selected-status-block {
  background-color: rgba(32, 128, 240, 0.1);
  border: 1px solid rgba(32, 128, 240, 0.3);
  color: #2080f0;
}

.saved-status-block {
  background-color: rgba(24, 160, 88, 0.1);
  border: 1px solid rgba(24, 160, 88, 0.3);
  color: #18a058;
}

.status-block:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.status-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 20;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 4px;
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

  .image-status-container {
    flex-direction: column;
  }
}
</style>
