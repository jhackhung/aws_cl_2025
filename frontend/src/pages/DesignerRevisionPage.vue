<template>
  <div class="revision-page">
    <DesignerRevisionPageHeader
      :inpaintingLoading="inpaintingLoading"
      @save-edits="saveEdits"
      @apply-inpainting="handleApplyInpainting"
    />

    <NLayoutContent class="page-content">
      <NSpin :show="loading || inpaintingLoading">
        <div v-if="inpaintingLoading" class="inpainting-progress">
          <div class="progress-container">
            <h3>正在進行局部重生成，請稍候...</h3>
            <NProgress
              type="line"
              :percentage="imageStore.generationProgress"
              :height="20"
              :processing="true"
            />
          </div>
        </div>

        <template v-else>
          <NGrid cols="1 l:2" x-gap="24" y-gap="24">
            <NGridItem class="editor-grid-item">
              <div class="editor-container">
                <div class="editor-header">
                  <h2>圖像編輯</h2>
                  <div class="tool-selection">
                    <NButtonGroup>
                      <NButton
                        :type="currentTool === 'brush' ? 'primary' : 'default'"
                        @click="currentTool = 'brush'"
                      >
                        畫筆
                      </NButton>
                      <NButton
                        :type="currentTool === 'eraser' ? 'primary' : 'default'"
                        @click="currentTool = 'eraser'"
                      >
                        橡皮擦
                      </NButton>
                    </NButtonGroup>
                  </div>
                </div>

                <div class="editor-canvas-container">
                  <canvas
                    ref="canvasRef"
                    class="editor-canvas"
                    @mousedown="startDrawing"
                    @mousemove="draw"
                    @mouseup="stopDrawing"
                    @mouseleave="stopDrawing"
                    @touchstart="handleTouchStart"
                    @touchmove="handleTouchMove"
                    @touchend="handleTouchEnd"
                  ></canvas>
                </div>

                <div class="editor-tools">
                  <div class="tool-group">
                    <label>筆刷大小</label>
                    <NSlider
                      v-model:value="brushSize"
                      :min="1"
                      :max="50"
                      :step="1"
                    />
                  </div>

                  <div class="tool-group">
                    <label>筆刷顏色</label>
                    <div class="color-buttons">
                      <div
                        v-for="color in brushColors"
                        :key="color"
                        class="color-button"
                        :style="{ backgroundColor: color }"
                        :class="{ active: brushColor === color }"
                        @click="brushColor = color"
                      ></div>
                    </div>
                  </div>

                  <div class="action-buttons">
                    <NButton @click="clearCanvas">清除畫布</NButton>
                    <NButton @click="undo" :disabled="historyIndex <= 0"
                      >撤銷</NButton
                    >
                    <NButton
                      @click="redo"
                      :disabled="historyIndex >= history.length - 1"
                      >重做</NButton
                    >
                  </div>
                </div>
              </div>
            </NGridItem>

            <NGridItem>
              <div class="settings-container">
                <div class="original-image">
                  <h2>原始圖像</h2>
                  <div v-if="originalImage" class="image-container">
                    <NImage
                      :src="getImageUrl(originalImage)"
                      object-fit="contain"
                      :width="400"
                      :alt="'原始圖像'"
                      show-toolbar
                    />
                  </div>
                  <div v-else class="no-image-placeholder">未找到原始圖像</div>
                </div>

                <div class="inpainting-settings">
                  <h2>重生成設置</h2>

                  <NForm>
                    <NFormItem label="提示詞">
                      <NInput
                        v-model:value="inpaintingPrompt"
                        type="textarea"
                        :autosize="{ minRows: 3, maxRows: 6 }"
                        placeholder="描述你希望局部區域變成的樣子"
                      />
                      <NButton
                        class="optimize-prompt-button"
                        type="primary"
                        @click="optimizePrompt"
                        title="優化提示詞"
                      >
                        ★
                      </NButton>
                    </NFormItem>

                    <NFormItem label="負面提示詞">
                      <NInput
                        v-model:value="negativePrompt"
                        type="textarea"
                        :autosize="{ minRows: 2, maxRows: 4 }"
                        placeholder="指定不希望出現的元素"
                      />
                    </NFormItem>

                    <NFormItem label="重生成強度">
                      <NSlider
                        v-model:value="inpaintingStrength"
                        :min="0"
                        :max="100"
                        :step="1"
                      />
                      <span class="param-value">{{ inpaintingStrength }}%</span>
                    </NFormItem>

                    <NFormItem label="步數">
                      <NSlider
                        v-model:value="inpaintingSteps"
                        :min="10"
                        :max="50"
                        :step="1"
                      />
                      <span class="param-value">{{ inpaintingSteps }}</span>
                    </NFormItem>

                    <NFormItem label="提示詞引導">
                      <NSlider
                        v-model:value="inpaintingGuidance"
                        :min="1"
                        :max="20"
                        :step="0.1"
                      />
                      <span class="param-value">{{ inpaintingGuidance }}</span>
                    </NFormItem>
                  </NForm>
                </div>

                <div v-if="inpaintingResults.length" class="inpainting-results">
                  <h2>重生成結果</h2>
                  <NGrid x-gap="16" y-gap="16" cols="1 s:2">
                    <NGridItem
                      v-for="(result, index) in inpaintingResults"
                      :key="index"
                    >
                      <div
                        class="result-card"
                        :class="{ selected: selectedResultIndex === index }"
                        @click="selectedResultIndex = index"
                      >
                        <NImage
                          :src="result.url"
                          object-fit="cover"
                          :alt="'重生成結果'"
                        />
                        <div class="result-actions">
                          <NButton
                            circle
                            quaternary
                            @click.stop="useInpaintingResult(result)"
                            title="使用此結果"
                          >
                            ✓
                          </NButton>
                        </div>
                      </div>
                    </NGridItem>
                  </NGrid>
                </div>
              </div>
            </NGridItem>
          </NGrid>
        </template>
      </NSpin>
    </NLayoutContent>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useProjectStore } from "../stores/project";
import { useImageStore } from "../stores/image";
import {
  NLayoutContent,
  NButton,
  NButtonGroup,
  NProgress,
  NGrid,
  NGridItem,
  NImage,
  NSpin,
  NForm,
  NFormItem,
  NInput,
  NSlider,
  useMessage,
} from "naive-ui";
import DesignerRevisionPageHeader from "../components/headers/DesignerRevisionPageHeader.vue";
import axios from "axios";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();
const message = useMessage();

// API configuration
const API_BASE_URL = "https://ec2.sausagee.party"; // Base URL for API
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Longer timeout for image processing
});

// Page state
const loading = ref(false);
const inpaintingLoading = ref(false);
const projectId = computed(() => route.params.projectId);
const imageId = computed(() => route.params.imageId);
const originalImage = ref(null);
const inpaintingResults = ref([]);
const selectedResultIndex = ref(null);

// Canvas/drawing state
const canvasRef = ref(null);
const ctx = ref(null);
const isDrawing = ref(false);
const currentTool = ref("brush");
const brushSize = ref(10);
const brushColor = ref("#ffffff");
const brushColors = [
  "#ffffff",
  "#000000",
  "#ff0000",
  "#00ff00",
  "#0000ff",
  "#ffff00",
  "#ff00ff",
];
const history = ref([]);
const historyIndex = ref(-1);
const lastPos = reactive({ x: 0, y: 0 });

// Inpainting parameters
const inpaintingPrompt = ref("");
const negativePrompt = ref("");
const inpaintingStrength = ref(80);
const inpaintingSteps = ref(30);
const inpaintingGuidance = ref(7.5);

// Initialize page
onMounted(async () => {
  loading.value = true;

  try {
    if (imageId.value) {
      // 首先嘗試從 store 獲取圖像
      let image = imageStore.getImageById(imageId.value);

      // 如果找不到圖像，嘗試從 localStorage 恢復
      if (!image) {
        console.log("找不到圖像從 store，嘗試從 localStorage 恢復");
        const savedImageJson = localStorage.getItem("lastSelectedImage");

        if (savedImageJson) {
          try {
            const savedImage = JSON.parse(savedImageJson);
            if (savedImage && savedImage.id === imageId.value) {
              // 將從 localStorage 恢復的圖像添加到 store
              image = savedImage;
              imageStore.generatedImages = [
                savedImage,
                ...imageStore.generatedImages.filter(
                  (img) => img.id !== savedImage.id
                ),
              ];
              console.log("成功從 localStorage 恢復圖像");
            }
          } catch (e) {
            console.error("解析 localStorage 中的圖像失敗:", e);
          }
        }
      }

      if (!image) {
        // 如果仍然找不到圖像，可能需要直接從 API 獲取
        console.error("Image not found in both store and localStorage");
        message.warning("無法找到您選擇的圖像，請返回重新選擇");
        return;
      }

      originalImage.value = image;
      console.log("成功載入原始圖像:", image.id);

      // Initialize prompt with image's prompt
      inpaintingPrompt.value = image.prompt || "";

      // If there are parameters, use them for initial values
      if (image.parameters) {
        inpaintingStrength.value = image.parameters.strength || 80;
        inpaintingSteps.value = image.parameters.steps || 30;
        inpaintingGuidance.value = image.parameters.cfgScale || 7.5;
        negativePrompt.value = image.parameters.negativePrompt || "";
      }

      // Initialize canvas
      initCanvas();
    }
  } catch (error) {
    console.error("Failed to load image:", error);
    message.error("加載圖像失敗: " + error.message);
  } finally {
    loading.value = false;
  }
});

// Initialize canvas
const initCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;

  // Set canvas size to container size
  const container = canvas.parentElement;
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;

  // Get drawing context
  ctx.value = canvas.getContext("2d");

  // Load image
  loadImageToCanvas();

  // Save initial state
  saveToHistory();
};

// Load image to canvas
const loadImageToCanvas = () => {
  if (!ctx.value || !originalImage.value) {
    console.error("Canvas context or original image is null");
    return;
  }

  console.log("原始圖像數據:", originalImage.value); // 添加日誌來檢查圖像數據

  const img = new Image();
  img.crossOrigin = "Anonymous";

  img.onload = () => {
    // Calculate scale to fit image to canvas
    const canvas = canvasRef.value;
    const scale = Math.min(
      canvas.width / img.width,
      canvas.height / img.height
    );

    const scaledWidth = img.width * scale;
    const scaledHeight = img.height * scale;

    // Center image on canvas
    const x = (canvas.width - scaledWidth) / 2;
    const y = (canvas.height - scaledHeight) / 2;

    // Clear canvas
    ctx.value.clearRect(0, 0, canvas.width, canvas.height);

    // Draw image
    ctx.value.drawImage(img, x, y, scaledWidth, scaledHeight);

    // Save to history
    saveToHistory();

    console.log("圖像成功加載到畫布");
  };

  img.onerror = (error) => {
    console.error("載入圖像到畫布失敗:", error);
    message.error("載入圖像到畫布失敗: " + (error?.message || "未知錯誤"));
  };

  // 確保URL格式正確
  let imageUrl = "";

  if (typeof originalImage.value === "string") {
    imageUrl = originalImage.value;
  } else if (originalImage.value.url) {
    // 如果URL不是以http開頭，添加API基礎URL
    if (!originalImage.value.url.startsWith("http")) {
      imageUrl = API_BASE_URL + originalImage.value.url;
    } else {
      imageUrl = originalImage.value.url;
    }
  } else if (originalImage.value.data) {
    imageUrl = `data:${originalImage.value.type || "image/jpeg"};base64,${
      originalImage.value.data
    }`;
  }

  console.log("圖像URL:", imageUrl); // 添加日誌來查看最終使用的URL

  if (!imageUrl) {
    console.error("無法獲取有效的圖像URL");
    message.error("無法獲取有效的圖像URL");
    return;
  }

  img.src = imageUrl;
};

// Start drawing
const startDrawing = (e) => {
  isDrawing.value = true;
  const { offsetX, offsetY } = getCoordinates(e);
  lastPos.x = offsetX;
  lastPos.y = offsetY;
};

// Draw
const draw = (e) => {
  if (!isDrawing.value || !ctx.value) return;

  const { offsetX, offsetY } = getCoordinates(e);

  ctx.value.lineJoin = "round";
  ctx.value.lineCap = "round";
  ctx.value.lineWidth = brushSize.value;

  if (currentTool.value === "brush") {
    ctx.value.strokeStyle = brushColor.value;
    ctx.value.globalCompositeOperation = "source-over";
  } else if (currentTool.value === "eraser") {
    ctx.value.globalCompositeOperation = "destination-out";
  }

  ctx.value.beginPath();
  ctx.value.moveTo(lastPos.x, lastPos.y);
  ctx.value.lineTo(offsetX, offsetY);
  ctx.value.stroke();

  lastPos.x = offsetX;
  lastPos.y = offsetY;
};

// Stop drawing
const stopDrawing = () => {
  if (isDrawing.value) {
    isDrawing.value = false;
    saveToHistory();
  }
};

// Handle touch events
const handleTouchStart = (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent("mousedown", {
    clientX: touch.clientX,
    clientY: touch.clientY,
  });
  canvasRef.value.dispatchEvent(mouseEvent);
};

const handleTouchMove = (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent("mousemove", {
    clientX: touch.clientX,
    clientY: touch.clientY,
  });
  canvasRef.value.dispatchEvent(mouseEvent);
};

const handleTouchEnd = (e) => {
  e.preventDefault();
  const mouseEvent = new MouseEvent("mouseup", {});
  canvasRef.value.dispatchEvent(mouseEvent);
};

// Get coordinates
const getCoordinates = (e) => {
  const canvas = canvasRef.value;
  const rect = canvas.getBoundingClientRect();
  return {
    offsetX: e.clientX - rect.left,
    offsetY: e.clientY - rect.top,
  };
};

// Clear canvas
const clearCanvas = () => {
  if (!ctx.value || !canvasRef.value) return;

  ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  saveToHistory();
};

// Save to history
const saveToHistory = () => {
  if (!ctx.value || !canvasRef.value) return;

  // If we're not at the end of history, truncate it
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1);
  }

  // Save current canvas state
  history.value.push(canvasRef.value.toDataURL());
  historyIndex.value = history.value.length - 1;
};

// Undo
const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--;
    restoreFromHistory();
  }
};

// Redo
const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++;
    restoreFromHistory();
  }
};

// Restore from history
const restoreFromHistory = () => {
  if (!ctx.value || !canvasRef.value || history.value.length === 0) return;

  const img = new Image();
  img.onload = () => {
    ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.value.drawImage(img, 0, 0);
  };
  img.src = history.value[historyIndex.value];
};

// Create mask for inpainting
const createMask = () => {
  // Return the canvas as is (it's already a drawing of the mask)
  return canvasRef.value;
};

// Handle apply inpainting button click
const handleApplyInpainting = async () => {
  if (!originalImage.value) {
    message.error("No image selected for inpainting");
    return;
  }

  inpaintingLoading.value = true;

  try {
    // Create mask
    const maskCanvas = createMask();
    const maskDataUrl = maskCanvas.toDataURL("image/png");

    // Create blob from data URL
    const maskBlob = await fetch(maskDataUrl).then((r) => r.blob());

    // Prepare form data
    const formData = new FormData();
    formData.append("batch_count", 1);
    formData.append("text", inpaintingPrompt.value);
    formData.append("imgs[]", originalImage.value.id); // Make sure format matches backend expectation
    formData.append("mask_image", maskBlob, "mask.png");
    formData.append("negative_prompt", negativePrompt.value);
    formData.append("cfg_scale", inpaintingGuidance.value);
    formData.append("seed", Math.floor(Math.random() * 2147483647)); // Random seed

    // Add parameters
    const parameters = {
      height: originalImage.value.parameters?.height || 1024,
      width: originalImage.value.parameters?.width || 1024,
      strength: inpaintingStrength.value,
      steps: inpaintingSteps.value,
    };
    formData.append("parameters", JSON.stringify(parameters));

    // Submit inpainting task
    const response = await api.post("/img/inpainting", formData);
    const taskId = response.data.id;

    // Poll for results
    await pollTaskStatus(taskId);
  } catch (error) {
    console.error("Inpainting failed:", error);
    message.error(`局部重生成失敗: ${error.message || "未知錯誤"}`);
  } finally {
    inpaintingLoading.value = false;
  }
};

// Poll task status
const pollTaskStatus = async (taskId) => {
  let completed = false;
  let attempts = 0;
  const maxAttempts = 60; // 5 minutes max (60 * 5 seconds)

  while (!completed && attempts < maxAttempts) {
    try {
      const response = await api.get(`/img/result/${taskId}`);
      const status = response.data.status;

      if (status === "done") {
        completed = true;
        // Process results
        if (response.data.urls && response.data.urls.length > 0) {
          const newResults = response.data.urls.map((url) => ({
            url: API_BASE_URL + url,
            id: url.split("/").pop().split(".")[0], // Extract ID from URL
            createdAt: new Date().toISOString(),
          }));
          inpaintingResults.value = [...newResults, ...inpaintingResults.value];
          selectedResultIndex.value = 0; // Select first new result
          message.success("局部重生成成功完成");
        } else {
          message.warning("局部重生成未返回结果");
        }
      } else if (status === "error") {
        completed = true;
        throw new Error(response.data.error || "任務失敗");
      }

      // Update progress if available
      if (response.data.progress) {
        imageStore.updateGenerationProgress(response.data.progress);
      }
    } catch (error) {
      console.error("Error polling task status:", error);
      message.error(`任務監控失敗: ${error.message}`);
      completed = true;
    }

    if (!completed) {
      // Wait before polling again
      await new Promise((resolve) => setTimeout(resolve, 5000)); // 5 second delay
      attempts++;
    }
  }

  if (!completed) {
    message.warning("局部重生成耗時超過預期。請稍後在畫廊中查看結果。");
  }
};

// Use inpainting result
const useInpaintingResult = async (result) => {
  if (!result) return;

  try {
    // Get project ID from route
    const projectId = route.params.projectId;

    // Fetch image data
    const imageResponse = await fetch(result.url);
    const imageBlob = await imageResponse.blob();

    // Create form data for saving
    const formData = new FormData();
    formData.append("projectId", projectId);
    formData.append("file", imageBlob, `inpainted_${Date.now()}.jpg`);
    formData.append("prompt", inpaintingPrompt.value);

    // Include original parameters but update with inpainting parameters
    const parameters = {
      ...(originalImage.value.parameters || {}),
      strength: inpaintingStrength.value,
      steps: inpaintingSteps.value,
      cfgScale: inpaintingGuidance.value,
      inpainted: true,
      sourceImageId: originalImage.value.id,
      negativePrompt: negativePrompt.value,
    };
    formData.append("parameters", JSON.stringify(parameters));

    // Save new image
    const response = await api.post("/img/save", formData);
    const newImageId = response.data.id;

    message.success("重生成的圖像已儲存到專案");

    // Navigate to generate page
    router.push({
      name: "ai-generate",
      params: { projectId: projectId },
    });
  } catch (error) {
    console.error("Failed to save inpainted result:", error);
    message.error(`保存結果失敗: ${error.message}`);
  }
};

// Save edits (without inpainting)
const saveEdits = async () => {
  if (!canvasRef.value || !originalImage.value) return;

  try {
    // Get edited image data
    const editedImageDataUrl = canvasRef.value.toDataURL("image/png");

    // Convert data URL to blob
    const response = await fetch(editedImageDataUrl);
    const blob = await response.blob();

    // Create form data
    const formData = new FormData();
    formData.append("projectId", route.params.projectId);
    formData.append("file", blob, `edited_${Date.now()}.png`);
    formData.append("prompt", originalImage.value.prompt || "");

    // Include original parameters
    const parameters = {
      ...(originalImage.value.parameters || {}),
      edited: true,
      sourceImageId: originalImage.value.id,
    };
    formData.append("parameters", JSON.stringify(parameters));

    // Save image
    const saveResponse = await api.post("/img/save", formData);

    message.success("編輯已儲存");

    // Return to generate page
    router.push({
      name: "ai-generate",
      params: { projectId: route.params.projectId },
    });
  } catch (error) {
    console.error("Failed to save edits:", error);
    message.error(`保存編輯失敗: ${error.message}`);
  }
};

// 輔助函數：獲取正確格式的圖像URL
const getImageUrl = (image) => {
  if (!image) return "";

  if (typeof image === "string") {
    return image;
  } else if (image.url) {
    // 如果URL不是以http開頭，添加API基礎URL
    if (!image.url.startsWith("http")) {
      return API_BASE_URL + image.url;
    }
    return image.url;
  } else if (image.data) {
    return `data:${image.type || "image/jpeg"};base64,${image.data}`;
  }

  return "";
};
</script>

<style scoped>
.revision-page {
  min-height: 100vh;
  background-color: var(--bg-color, #f5f7fa);
}

.page-content {
  padding: 0 24px 24px 24px;
  width: 100%;
  box-sizing: border-box;
}

.inpainting-progress {
  padding: 40px 0;
  max-width: 600px;
  margin: 0 auto;
}

.input-with-button {
  position: relative;
  width: 100%;
}

.optimize-prompt-button {
  position: absolute;
  top: 8px;
  bottom: 8px;
  right: 8px;
  z-index: 2;
  font-size: 16px;
  padding: 4px 8px;
  width: 32px;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 確保輸入框內容左對齊並預留右側空間 */
:deep(.text-input-left textarea) {
  text-align: left !important;
  padding-right: 40px;
}

.progress-container {
  text-align: center;
}

.progress-container h3 {
  margin-bottom: 16px;
}

.editor-container {
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  gap: 12px;
}

.editor-canvas-container {
  flex: 1;
  position: relative;
  height: 500px;
  overflow: hidden;
}

.editor-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: crosshair;
  background-color: #ddd;
}

.editor-tools {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.tool-group {
  margin-bottom: 16px;
}

.tool-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

:deep(.text-input-left textarea) {
  text-align: left !important;
}

.color-buttons {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.color-button {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid #ddd;
  cursor: pointer;
  transition: transform 0.2s;
}

.color-button:hover {
  transform: scale(1.1);
}

.color-button.active {
  border-color: #333;
  transform: scale(1.15);
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.original-image,
.inpainting-settings,
.inpainting-results {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 3px solid transparent;
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-card.selected {
  border-color: #2080f0;
}

.result-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.result-card:hover .result-actions {
  opacity: 1;
}

.param-value {
  margin-left: 8px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .page-content {
    padding: 0 16px 16px 16px;
  }

  .editor-canvas-container {
    height: 300px;
  }

  .editor-header,
  .editor-tools {
    flex-direction: column;
    align-items: flex-start;
  }

  .tool-selection {
    margin-top: 8px;
    width: 100%;
  }

  .action-buttons {
    width: 100%;
    justify-content: center;
  }

  .color-buttons {
    justify-content: center;
  }

  .inpainting-settings {
    margin-top: 16px;
  }
}

/* Dark mode support */
:root.dark .editor-container {
  background-color: #1a1a1a;
}

:root.dark .editor-header,
:root.dark .editor-tools {
  background-color: #252525;
  border-color: #333;
}

:root.dark .editor-canvas {
  background-color: #333;
}

:root.dark .original-image,
:root.dark .inpainting-settings,
:root.dark .inpainting-results {
  background-color: #252525;
}

:root.dark .color-button {
  border-color: #555;
}

:root.dark .color-button.active {
  border-color: #eaeaea;
}

:root.dark .param-value {
  color: #aaa;
}
</style>
