<template>
  <div class="design-input-page">
    <DesignInputPageHeader
      :project="project"
      :loading="loading"
      :isFormValid="!!form.prompt.trim()"
      @clear-form="clearForm"
      @start-generation="startGeneration"
    />

    <NLayoutContent class="page-content">
      <NSpin :show="loading">
        <NGrid cols="1 l:3" x-gap="24" y-gap="24">
          <NGridItem class="design-form-container" span="1 l:2">
            <NCard title="設計提示詞" class="design-form">
              <NForm
                ref="formRef"
                :model="form"
                :rules="rules"
                label-placement="left"
                label-width="auto"
                require-mark-placement="right-hanging"
              >
                <NFormItem label="提示詞" path="prompt" required>
                  <NInput
                    v-model:value="form.prompt"
                    type="textarea"
                    class="text-input-left"
                    placeholder="描述你想要的設計，例如：現代簡約風格的客廳，採用白色和木質元素..."
                    :autosize="{ minRows: 5, maxRows: 10 }"
                  />
                  <NButton
                    class="optimize-prompt-button"
                    type="primary"
                    @click="optimizePrompt"
                    :disabled="!form.prompt.trim()"
                    title="優化提示詞"
                  >
                    <template #icon>★</template>
                  </NButton>
                </NFormItem>

                <NFormItem label="負面提示詞" path="negativePrompt">
                  <NInput
                    v-model:value="form.negativePrompt"
                    type="textarea"
                    placeholder="描述你不想出現在生成結果中的元素，例如：模糊, 畸形, 低質量..."
                    :autosize="{ minRows: 3, maxRows: 5 }"
                    class="text-input-left"
                  />
                </NFormItem>

                <NFormItem label="風格" path="style">
                  <NSelect
                    v-model:value="form.style"
                    :options="styleOptions"
                    placeholder="選擇設計風格"
                    clearable
                  />
                </NFormItem>

                <NFormItem label="尺寸" path="size">
                  <NSelect
                    v-model:value="form.size"
                    :options="sizeOptions"
                    placeholder="選擇圖像尺寸"
                  />
                </NFormItem>

                <NFormItem label="生成數量" path="count">
                  <NSlider
                    v-model:value="form.count"
                    :min="1"
                    :max="5"
                    :step="1"
                  />
                  <NInputNumber
                    v-model:value="form.count"
                    :min="1"
                    :max="10"
                    size="small"
                    style="margin-left: 12px"
                  />
                </NFormItem>

                <NFormItem label="提示詞引導強度" path="cfgScale">
                  <NTooltip trigger="hover" placement="top">
                    <template #trigger>
                      <NSlider
                        v-model:value="form.cfgScale"
                        :min="1"
                        :max="20"
                        :step="0.5"
                      />
                    </template>
                    數值越高，AI 生成時會更嚴格地遵循提示詞
                  </NTooltip>
                </NFormItem>

                <NFormItem label="迭代步數" path="steps">
                  <NTooltip trigger="hover" placement="top">
                    <template #trigger>
                      <NSlider
                        v-model:value="form.steps"
                        :min="10"
                        :max="150"
                        :step="1"
                      />
                    </template>
                    步數越多，生成結果越精細，但耗時也越長
                  </NTooltip>
                </NFormItem>

                <NFormItem label="隨機種子" path="seed">
                  <div class="seed-input">
                    <NInputNumber
                      v-model:value="form.seed"
                      :min="-1"
                      :max="2147483647"
                      style="width: 160px"
                      :disabled="form.randomizeSeed"
                    />
                    <NCheckbox v-model:checked="form.randomizeSeed"
                      >隨機</NCheckbox
                    >
                  </div>
                </NFormItem>
              </NForm>
            </NCard>
          </NGridItem>

          <NGridItem class="reference-container">
            <NCard title="參考圖像" class="reference-card">
              <div class="reference-content">
                <div
                  v-if="referenceImages.length === 0"
                  class="empty-reference"
                >
                  <p>沒有參考圖像</p>
                  <NButton @click="openReferenceUpload">上傳參考圖像</NButton>
                </div>
                <div v-else class="reference-images">
                  <div
                    v-for="(image, index) in referenceImages"
                    :key="index"
                    class="reference-image-wrapper"
                  >
                    <NImage
                      :src="image"
                      object-fit="contain"
                      width="100%"
                      :alt="'參考圖像 ' + (index + 1)"
                      class="reference-image"
                    />
                    <div class="reference-image-overlay">
                      <NButton
                        circle
                        quaternary
                        type="error"
                        @click="removeReferenceImage(index)"
                        class="remove-button"
                      >
                        <template #icon>✕</template>
                      </NButton>
                    </div>
                    <div class="reference-prompt">
                      <NInput
                        v-model:value="image.prompt"
                        type="text"
                        placeholder="輸入此參考圖像的提示詞"
                        @update:value="updateReferencePrompt(index, $event)"
                      />
                    </div>
                  </div>
                  <div class="reference-actions">
                    <NButton
                      @click="openReferenceUpload"
                      :disabled="referenceImages.length >= 3"
                    >
                      {{
                        referenceImages.length >= 3
                          ? "最多 3 張參考圖"
                          : "添加參考圖"
                      }}
                    </NButton>
                    <NButton
                      @click="clearReferenceImages"
                      :disabled="referenceImages.length === 0"
                    >
                      清除所有
                    </NButton>
                  </div>
                </div>

                <div
                  class="reference-strength"
                  v-if="referenceImages.length > 0"
                >
                  <span>參考強度：{{ form.referenceStrength }}%</span>
                  <NSlider
                    v-model:value="form.referenceStrength"
                    :min="0"
                    :max="100"
                    :step="5"
                  />
                </div>
              </div>
            </NCard>

            <NCard title="自訂模型" class="model-card">
              <NSelect
                v-model:value="form.model"
                :options="modelOptions"
                placeholder="選擇生成模型"
              />
              <div class="model-description" v-if="selectedModelDescription">
                {{ selectedModelDescription }}
              </div>
            </NCard>
          </NGridItem>
        </NGrid>
      </NSpin>
    </NLayoutContent>

    <NModal
      v-model:show="showUploadModal"
      preset="card"
      title="上傳參考圖像"
      class="upload-modal"
      style="
        width: 90%;
        max-width: 600px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      "
    >
      <div class="upload-area">
        <NUpload
          ref="uploadRef"
          accept="image/*"
          :default-upload="false"
          :max="1"
          :multiple="false"
          @change="handleUploadChange"
        >
          <div class="upload-trigger">
            <div class="upload-inner">
              <div class="upload-icon">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M12 5V19M5 12H19"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div class="upload-text">
                <p class="primary-text">點擊或拖曳圖片至此處</p>
                <p class="secondary-text">支持 JPG, PNG, WEBP 格式</p>
              </div>
              <NButton class="select-image-button">選擇圖像</NButton>
            </div>
          </div>
        </NUpload>

        <div class="upload-preview" v-if="uploadFile">
          <NImage
            :src="uploadFileUrl"
            object-fit="contain"
            :alt="'預覽圖像'"
            style="max-height: 300px; border-radius: 8px"
          />
        </div>
      </div>

      <template #footer>
        <div class="modal-footer">
          <NButton @click="showUploadModal = false">取消</NButton>
          <NButton
            type="primary"
            :disabled="!uploadFile"
            @click="addReferenceImage"
          >
            添加
          </NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<script setup>
// 導入所需組件
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
  NCard,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NSlider,
  NInputNumber,
  NCheckbox,
  NTooltip,
  NUpload,
} from "naive-ui";
import DesignInputPageHeader from "../components/headers/DesignInputPageHeader.vue";

const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const imageStore = useImageStore();

// 表單參考
const formRef = ref(null);

// 頁面狀態
const loading = ref(false);
const projectId = computed(() => route.params.projectId);
const project = computed(() => projectStore.currentProject);
const referenceImages = computed(() => imageStore.referenceImages);
const showUploadModal = ref(false);
const uploadRef = ref(null);
const uploadFile = ref(null);
const uploadFileUrl = ref("");

// 表單數據
const form = ref({
  prompt: "",
  negativePrompt: "",
  style: null,
  size: "1024x1024",
  count: 4,
  cfgScale: 7.5,
  steps: 30,
  seed: -1,
  randomizeSeed: true,
  referenceStrength: 60,
  model: "default",
});

// 表單驗證規則
const rules = {
  prompt: {
    required: true,
    message: "請輸入提示詞",
    trigger: ["blur", "input"],
  },
};

// 優化提示詞
const optimizePrompt = async () => {
  if (!form.value.prompt.trim()) return;

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
        text: form.value.prompt,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("優化提示詞失敗:", response.status, errorText);
      throw new Error(`API錯誤: ${response.status}`);
    }

    const data = await response.json();

    if (data && data.text) {
      form.value.prompt = data.text;
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

// 風格選項
const styleOptions = [
  { label: "現代簡約", value: "modern_minimalist" },
  { label: "科技未來", value: "tech_futuristic" },
  { label: "工業風格", value: "industrial" },
];

// 尺寸選項
const sizeOptions = [
  { label: "1:1 (1024x1024)", value: "1024x1024" },
  { label: "16:9 (1920x1080)", value: "1920x1080" },
  { label: "9:16 (1080x1920)", value: "1080x1920" },
  { label: "4:3 (1600x1200)", value: "1600x1200" },
  { label: "3:4 (1200x1600)", value: "1200x1600" },
];

// 模型選項
const modelOptions = [
  { label: "預設模型", value: "default" },
  { label: "高品質", value: "high_quality" },
  { label: "寫實風格", value: "realistic" },
  { label: "插畫風格", value: "illustration" },
  { label: "水彩風格", value: "watercolor" },
];

// 選擇的模型描述
const selectedModelDescription = computed(() => {
  switch (form.value.model) {
    case "high_quality":
      return "適合需要高細節的設計，生成時間較長";
    case "realistic":
      return "擅長生成逼真的場景和物品";
    case "illustration":
      return "生成插畫風格的圖像，適合用於平面設計";
    case "watercolor":
      return "生成帶有水彩藝術風格的圖像";
    default:
      return "適用於大多數設計任務的通用模型";
  }
});

// 初始載入數據
onMounted(async () => {
  loading.value = true;
  try {
    // 如果有項目 ID，加載項目數據
    if (projectId.value && projectId.value !== "temp") {
      await projectStore.fetchProjectById(projectId.value);

      // 如果項目有初始參數，使用它們
      if (project.value && project.value.designParams) {
        form.value = {
          ...form.value,
          ...project.value.designParams,
        };
      }
    }

    // 獲取存儲的生成參數
    const storedParams = imageStore.generationParams;
    if (storedParams) {
      form.value = {
        ...form.value,
        prompt: storedParams.prompt || form.value.prompt,
        negativePrompt:
          storedParams.negativePrompt || form.value.negativePrompt,
        cfgScale: storedParams.cfgScale || form.value.cfgScale,
        steps: storedParams.steps || form.value.steps,
        seed: storedParams.seed || form.value.seed,
      };
    }
  } catch (error) {
    console.error("載入項目數據失敗:", error);
  } finally {
    loading.value = false;
  }
});

// 開啟參考圖像上傳對話框
const openReferenceUpload = () => {
  showUploadModal.value = true;
  uploadFile.value = null;
  uploadFileUrl.value = "";
};

// 處理上傳變化
const handleUploadChange = (options) => {
  const { file } = options;
  uploadFile.value = file;

  // 獲取文件 URL
  if (file.file) {
    uploadFileUrl.value = URL.createObjectURL(file.file);
  }
};

// 添加參考圖像
const addReferenceImage = () => {
  if (uploadFileUrl.value) {
    imageStore.setReferenceImages([
      ...referenceImages.value,
      { url: uploadFileUrl.value, prompt: "" },
    ]);
    showUploadModal.value = false;
  }
};

// 移除參考圖像
const removeReferenceImage = (index) => {
  const newImages = [...referenceImages.value];
  newImages.splice(index, 1);
  imageStore.setReferenceImages(newImages);
};

// 清除所有參考圖像
const clearReferenceImages = () => {
  imageStore.setReferenceImages([]);
};

// 清空表單
const clearForm = () => {
  form.value = {
    prompt: "",
    negativePrompt: "",
    style: null,
    size: "1024x1024",
    count: 4,
    cfgScale: 7.5,
    steps: 30,
    seed: -1,
    randomizeSeed: true,
    referenceStrength: 60,
    model: "default",
  };
};

// 更新參考圖像的提示詞
const updateReferencePrompt = (index, prompt) => {
  const newImages = [...referenceImages.value];
  if (newImages[index]) {
    newImages[index].prompt = prompt;
    imageStore.setReferenceImages(newImages);
  }
};

// 開始生成
const startGeneration = async () => {
  if (!form.value.prompt.trim()) return;

  try {
    loading.value = true;

    // 如果選擇隨機種子，生成一個新的隨機種子
    if (form.value.randomizeSeed) {
      form.value.seed = Math.floor(Math.random() * 1000000).toString();
    }

    // 創建表單數據
    const formData = new FormData();
    formData.append("batch_count", form.value.count);
    formData.append("text", form.value.prompt);

    // 添加負面提示詞（如果有）
    if (form.value.negativePrompt) {
      formData.append("negative_prompt", form.value.negativePrompt);
    }

    formData.append("cfg_scale", form.value.cfgScale);
    // 會導致錯誤，因為 API 端點不接受這個參數
    // formData.append("seed", form.value.seed);

    // 處理尺寸參數與其他參數
    const [width, height] = form.value.size.split("x").map(Number);

    // 直接將參數作為字典形式傳遞，不使用 JSON.stringify
    formData.append("parameters[width]", width);
    formData.append("parameters[height]", height);
    formData.append("parameters[steps]", form.value.steps);

    // 如果有選擇風格，加入參數
    if (form.value.style) {
      formData.append("parameters[style]", form.value.style);
    }

    // 如果有選擇特定模型，加入參數
    if (form.value.model && form.value.model !== "default") {
      formData.append("parameters[model]", form.value.model);
    }

    // 處理參考圖像
    if (referenceImages.value.length > 0) {
      // 獲取參考圖像 URL 列表
      const imageUrls = referenceImages.value.map((img) => img.url || img);

      // 將圖像 URL 數組轉為 JSON 字符串
      formData.append("imgs", JSON.stringify(imageUrls));

      // 添加參考強度
      formData.append(
        "similarityStrength",
        (form.value.referenceStrength / 100).toString()
      );

      // 收集參考圖像的提示詞
      const refPrompts = referenceImages.value.map((img) => img.prompt || "");
      if (refPrompts.some((prompt) => prompt)) {
        formData.append("reference_prompts", JSON.stringify(refPrompts));
      }
    }

    // 發送請求到 API 端點
    const response = await fetch("https://ec2.sausagee.party/img/generate", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error("生成失敗:", response.status, errorData);
      throw new Error(`API 錯誤: ${response.status} - ${errorData}`);
    }

    const data = await response.json();

    // 檢查回應中是否包含任務 ID
    if (!data.id) {
      throw new Error("API 返回的數據中缺少任務 ID");
    }

    const taskId = data.id;
    console.log("生成任務已啟動，任務 ID:", taskId);

    // 保存生成參數
    imageStore.setGenerationParams({
      prompt: form.value.prompt,
      negativePrompt: form.value.negativePrompt,
      style: form.value.style,
      size: form.value.size,
      steps: form.value.steps,
      cfgScale: form.value.cfgScale,
      seed: form.value.seed,
      batchCount: form.value.count,
      model: form.value.model,
      taskId: taskId, // 儲存任務 ID 以供後續使用
    });

    // 導航到生成頁面
    router.push({
      name: "ai-generate",
      params: {
        projectId: projectId.value !== "temp" ? projectId.value : "temp",
      },
      query: {
        taskId: taskId, // 將任務 ID 作為查詢參數傳遞
      },
    });
  } catch (error) {
    console.error("開始生成失敗:", error);
    // 這裡可以加入錯誤處理，例如使用通知組件顯示錯誤信息
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reference-image-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.reference-prompt {
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
}
/* 現有的文本對齊樣式 */
.text-input-left :deep(.n-input__textarea-el) {
  text-align: left !important;
  direction: ltr !important;
}

/* 使輸入框中的文字默認左對齊 */
:deep(.n-input__textarea-el),
:deep(.n-input__input-el) {
  text-align: left !important;
}

/* 新增：讓 placeholder 文字也靠左對齊 */
:deep(.n-input__textarea-el::placeholder),
:deep(.n-input__input-el::placeholder) {
  text-align: left !important;
}

/* 針對 Firefox 瀏覽器的特殊規則 */
:deep(.n-input__textarea-el::-moz-placeholder),
:deep(.n-input__input-el::-moz-placeholder) {
  text-align: left !important;
}

/* 針對 Edge 的特殊規則 */
:deep(.n-input__textarea-el::-ms-input-placeholder),
:deep(.n-input__input-el::-ms-input-placeholder) {
  text-align: left !important;
}

.design-input-page {
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-color, #f5f7fa);
}

.prompt-input-container {
  position: relative;
  width: 100%;
}

.optimize-prompt-button {
  position: absolute;
  right: 8px;
  top: 8px;
  bottom: 8px;
  height: auto;
  padding: 4px 12px;
  font-size: 14px;
  z-index: 2;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-content {
  padding: 0 24px 24px 24px;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 10;
}

.design-form-container {
  width: 100%;
}

.design-form {
  height: 100%;
  background-color: #fff;
}

.n-card {
  background-color: #fff !important;
  border: 1px solid #eaeaea;
  overflow: visible !important;
  position: relative;
  z-index: 15;
}

.n-card__content {
  padding: 16px;
}

.n-card-header__main {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 加強設計表單的顯示 */
.n-form .n-form-item {
  margin-bottom: 16px;
  position: relative;
  z-index: 20;
}

.n-form .n-form-item-label {
  font-weight: 500;
  color: #333;
}

.seed-input {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.reference-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reference-card,
.model-card {
  width: 100%;
  height: 100%;
  background-color: #fff;
}

.reference-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-reference {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
  color: #909399;
}

.reference-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reference-image-wrapper {
  position: relative;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
}

.reference-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.reference-image-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
}

.remove-button {
  background-color: rgba(255, 255, 255, 0.7);
  color: #ff4d4f;
}

.reference-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.reference-strength {
  margin-top: 16px;
}

.model-description {
  margin-top: 12px;
  font-size: 14px;
  color: #606266;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-trigger {
  display: flex;
  justify-content: center;
  padding: 24px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
}

.upload-preview {
  display: flex;
  justify-content: center;
  max-height: 300px;
  overflow: hidden;
  border-radius: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 解決深色模式下顯示問題 */
:root.dark .design-form,
:root.dark .reference-card,
:root.dark .model-card,
:root.dark .n-card {
  background-color: var(--card-bg-color, #1f1f1f) !important;
  color: var(--text-color, #e0e0e0);
  border-color: #333;
}

:root.dark .n-card-header__main,
:root.dark .n-form-item-label {
  color: var(--text-color, #e0e0e0) !important;
}

:root.dark .empty-reference {
  color: #aaa;
}

:root.dark .model-description {
  color: #aaa;
}

:root.dark .upload-trigger {
  border-color: #444;
}

@media (max-width: 768px) {
  .page-content {
    padding: 0 16px 16px 16px;
  }

  .reference-image-wrapper {
    height: 150px;
  }

  .upload-preview img {
    max-width: 100%;
    height: auto;
  }
}

/* Add new styles for the enhanced upload modal */
.upload-modal :deep(.n-card-header__main) {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
  width: 100%;
  transition: all 0.3s ease;
}

.upload-trigger {
  width: 100%;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  transition: all 0.3s ease;
  background-color: rgba(0, 0, 0, 0.02);
}

.upload-trigger:hover {
  border-color: #2080f0;
  background-color: rgba(32, 128, 240, 0.05);
}

.upload-icon {
  color: #909399;
  font-size: 48px;
  margin-bottom: 8px;
}

.upload-text {
  text-align: center;
}

.primary-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.secondary-text {
  font-size: 14px;
  color: #909399;
  margin-top: 0;
}

.select-image-button {
  margin-top: 8px;
  padding: 8px 24px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 6px;
}

.upload-preview {
  display: flex;
  justify-content: center;
  border-radius: 12px;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.03);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.modal-footer {
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

:root.dark .upload-trigger {
  background-color: rgba(255, 255, 255, 0.03);
  border-color: #444;
}

:root.dark .upload-trigger:hover {
  border-color: #2080f0;
  background-color: rgba(32, 128, 240, 0.1);
}

:root.dark .primary-text {
  color: #e0e0e0;
}

:root.dark .upload-preview {
  background-color: rgba(255, 255, 255, 0.05);
}

:root.dark .upload-icon {
  color: #aaa;
}

:root.dark .modal-footer {
  border-color: rgba(255, 255, 255, 0.1);
}
</style>
