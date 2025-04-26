<template>
  <div class="revision-page">
    <DesignerRevisionPageHeader
      :inpaintingLoading="inpaintingLoading"
      @save-edits="saveEdits"
      @apply-inpainting="applyInpainting"
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
                        @click="setTool('brush')"
                      >
                        畫筆
                      </NButton>
                      <NButton
                        :type="currentTool === 'eraser' ? 'primary' : 'default'"
                        @click="setTool('eraser')"
                      >
                        橡皮擦
                      </NButton>
                    </NButtonGroup>
                  </div>
                </div>

                <div class="editor-canvas-container">
                  <canvas
                    ref="editorCanvas"
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
                  <NImage
                    v-if="originalImage"
                    :src="originalImage.url"
                    object-fit="contain"
                    :width="400"
                    :alt="'原始圖像'"
                  />
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
                        class="text-input-left"
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

                    <NFormItem label="重生成強度">
                      <NSlider
                        v-model:value="inpaintingStrength"
                        :min="0"
                        :max="100"
                        :step="1"
                      />
                    </NFormItem>

                    <NFormItem label="步數">
                      <NSlider
                        v-model:value="inpaintingSteps"
                        :min="10"
                        :max="50"
                        :step="1"
                      />
                    </NFormItem>

                    <NFormItem label="提示詞引導">
                      <NSlider
                        v-model:value="inpaintingGuidance"
                        :min="1"
                        :max="20"
                        :step="0.1"
                      />
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
                        @click="selectResult(index)"
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
                            @click.stop="useResult(result)"
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
import { ref, computed, onMounted, onUnmounted } from "vue";
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
} from "naive-ui";
import DesignerRevisionPageHeader from "../components/headers/DesignerRevisionPageHeader.vue";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();

// 頁面狀態
const loading = ref(false);
const inpaintingLoading = ref(false);
const projectId = computed(() => route.params.projectId);
const imageId = computed(() => route.params.imageId);
const originalImage = ref(null);
const editorCanvas = ref(null);
const ctx = ref(null);
const isDrawing = ref(false);
const lastX = ref(0);
const lastY = ref(0);
const history = ref([]);
const historyIndex = ref(-1);
const inpaintingResults = ref([]);
const selectedResultIndex = ref(null);

// 編輯工具設置
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
const inpaintingPrompt = ref("");
const inpaintingStrength = ref(80);
const inpaintingSteps = ref(30);
const inpaintingGuidance = ref(7.5);

// 初始化頁面
onMounted(async () => {
  loading.value = true;

  try {
    if (imageId.value) {
      // 加載原始圖像
      const image = imageStore.getImageById(imageId.value);

      if (!image) {
        // 如果在本地狀態中找不到圖像，可能需要從 API 加載
        console.error("找不到指定的圖像");
        return;
      }

      originalImage.value = image;

      // 初始化提示詞
      inpaintingPrompt.value = image.prompt || "";

      // 初始化畫布
      initCanvas();
    }
  } catch (error) {
    console.error("載入圖像失敗:", error);
  } finally {
    loading.value = false;
  }
});

// 在組件卸載時清理資源
onUnmounted(() => {
  // 清理任何可能的資源
});

// 初始化畫布
const initCanvas = () => {
  const canvas = editorCanvas.value;
  if (!canvas) return;

  // 設置畫布大小為容器大小
  const container = canvas.parentElement;
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;

  // 獲取繪圖上下文
  ctx.value = canvas.getContext("2d");

  // 載入圖像
  loadImageToCanvas();

  // 儲存初始狀態到歷史記錄
  saveToHistory();
};

const optimizePrompt = async () => {
  if (!inpaintingPrompt.value.trim()) return;

  try {
    loading.value = true;

    // 向後端發送優化請求
    // 實際實現應該替換為您的API調用
    const response = await fetch("https://ec2.sausagee.party/txt/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        text: inpaintingPrompt.value,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("優化提示詞失敗:", response.status, errorText);
      throw new Error(`API錯誤: ${response.status}`);
    }

    const data = await response.json();

    if (data && data.text) {
      inpaintingPrompt.value = data.text;
      console.log("提示詞已優化:", data.text);
    } else {
      console.warn("API返回了未預期的數據格式:", data);
    }
  } catch (error) {
    console.error("優化提示詞失敗:", error);
    // 這裡可以加入錯誤處理，例如使用通知組件顯示錯誤信息
  } finally {
    loading.value = false;
  }
};

// 載入圖像到畫布
const loadImageToCanvas = () => {
  if (!ctx.value || !originalImage.value) return;

  const img = new Image();
  img.crossOrigin = "Anonymous";
  img.onload = () => {
    // 計算圖像縮放比例以適應畫布
    const canvas = editorCanvas.value;
    const scale = Math.min(
      canvas.width / img.width,
      canvas.height / img.height
    );

    const scaledWidth = img.width * scale;
    const scaledHeight = img.height * scale;

    // 計算圖像在畫布中的位置（居中）
    const x = (canvas.width - scaledWidth) / 2;
    const y = (canvas.height - scaledHeight) / 2;

    // 清除畫布
    ctx.value.clearRect(0, 0, canvas.width, canvas.height);

    // 繪製圖像
    ctx.value.drawImage(img, x, y, scaledWidth, scaledHeight);

    // 儲存到歷史記錄
    saveToHistory();
  };

  img.onerror = () => {
    console.error("載入圖像到畫布失敗");
  };

  img.src = originalImage.value.url;
};

// 設置當前工具
const setTool = (tool) => {
  currentTool.value = tool;
};

// 開始繪製
const startDrawing = (e) => {
  isDrawing.value = true;
  const { offsetX, offsetY } = getCoordinates(e);
  lastX.value = offsetX;
  lastY.value = offsetY;
};

// 繪製
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
  ctx.value.moveTo(lastX.value, lastY.value);
  ctx.value.lineTo(offsetX, offsetY);
  ctx.value.stroke();

  lastX.value = offsetX;
  lastY.value = offsetY;
};

// 停止繪製
const stopDrawing = () => {
  if (isDrawing.value) {
    isDrawing.value = false;
    saveToHistory();
  }
};

// 處理觸摸事件
const handleTouchStart = (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent("mousedown", {
    clientX: touch.clientX,
    clientY: touch.clientY,
  });
  editorCanvas.value.dispatchEvent(mouseEvent);
};

const handleTouchMove = (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent("mousemove", {
    clientX: touch.clientX,
    clientY: touch.clientY,
  });
  editorCanvas.value.dispatchEvent(mouseEvent);
};

const handleTouchEnd = (e) => {
  e.preventDefault();
  const mouseEvent = new MouseEvent("mouseup", {});
  editorCanvas.value.dispatchEvent(mouseEvent);
};

// 獲取座標
const getCoordinates = (e) => {
  const canvas = editorCanvas.value;
  const rect = canvas.getBoundingClientRect();
  return {
    offsetX: e.clientX - rect.left,
    offsetY: e.clientY - rect.top,
  };
};

// 清除畫布
const clearCanvas = () => {
  if (!ctx.value || !editorCanvas.value) return;

  ctx.value.clearRect(
    0,
    0,
    editorCanvas.value.width,
    editorCanvas.value.height
  );
  loadImageToCanvas();
};

// 保存到歷史記錄
const saveToHistory = () => {
  if (!ctx.value || !editorCanvas.value) return;

  // 如果當前不在歷史記錄的末尾，刪除後面的記錄
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1);
  }

  // 保存當前畫布狀態
  history.value.push(editorCanvas.value.toDataURL());
  historyIndex.value = history.value.length - 1;
};

// 撤銷
const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--;
    restoreFromHistory();
  }
};

// 重做
const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++;
    restoreFromHistory();
  }
};

// 從歷史記錄恢復
const restoreFromHistory = () => {
  if (!ctx.value || !editorCanvas.value || history.value.length === 0) return;

  const img = new Image();
  img.onload = () => {
    ctx.value.clearRect(
      0,
      0,
      editorCanvas.value.width,
      editorCanvas.value.height
    );
    ctx.value.drawImage(img, 0, 0);
  };
  img.src = history.value[historyIndex.value];
};

// 應用局部重生成
const applyInpainting = async () => {
  if (!ctx.value || !editorCanvas.value || !originalImage.value) return;

  // 獲取遮罩
  const maskDataUrl = editorCanvas.value.toDataURL("image/png");

  // 創建遮罩
  const mask = generateMask(maskDataUrl);

  inpaintingLoading.value = true;

  try {
    // 執行局部重生成
    const newImage = await imageStore.applyInpainting(
      originalImage.value.id,
      mask,
      inpaintingPrompt.value,
      {
        strength: inpaintingStrength.value,
        steps: inpaintingSteps.value,
        guidance: inpaintingGuidance.value,
        projectId: projectId.value !== "temp" ? projectId.value : null,
      }
    );

    // 將結果添加到重生成結果列表
    inpaintingResults.value.unshift(newImage);

    // 選擇最新的結果
    selectedResultIndex.value = 0;
  } catch (error) {
    console.error("局部重生成失敗:", error);
  } finally {
    inpaintingLoading.value = false;
  }
};

// 生成遮罩
const generateMask = (dataUrl) => {
  // 在實際的應用中，您需要處理圖像數據，提取畫筆區域作為遮罩
  // 現在我們只是簡單地返回原始畫布數據
  return dataUrl;
};

// 選擇結果
const selectResult = (index) => {
  selectedResultIndex.value = index;
};

// 使用選定的結果
const useResult = (result) => {
  if (!result) return;

  // 導航到圖像生成頁面，顯示選定的結果
  router.push({
    name: "ai-generate",
    params: {
      projectId: projectId.value !== "temp" ? projectId.value : "temp",
    },
  });
};

// 保存編輯
const saveEdits = async () => {
  if (!editorCanvas.value || !originalImage.value) return;

  // 獲取編輯後的圖像數據
  const editedImageDataUrl = editorCanvas.value.toDataURL("image/png");

  try {
    // 保存編輯後的圖像
    // 在實際應用中，您需要將圖像數據上傳到服務器
    // 現在我們只是簡單地模擬這個過程
    const editedImage = {
      ...originalImage.value,
      url: editedImageDataUrl,
      editedAt: new Date().toISOString(),
    };

    console.log("圖像編輯已保存", editedImage);

    // 返回到生成頁面
    router.push({
      name: "ai-generate",
      params: {
        projectId: projectId.value !== "temp" ? projectId.value : "temp",
      },
    });
  } catch (error) {
    console.error("保存編輯失敗:", error);
  }
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
</style>
