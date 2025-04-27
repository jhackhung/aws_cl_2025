// src/stores/image.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

// API Base URL
const API_BASE_URL = "https://ec2.sausagee.party";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Longer timeout for image operations
});

export const useImageStore = defineStore("image", () => {
  // State
  const generatedImages = ref([]);
  const referenceImages = ref([]);
  const generationParams = ref({
    prompt: "",
    negativePrompt: "",
    style: null,
    size: "1024x1024",
    cfgScale: 7.5,
    steps: 30,
    seed: -1,
  });
  const generationProgress = ref(0);
  const loading = ref(false);

  // Getters
  const getImageById = computed(() => (id) => {
    return generatedImages.value.find((img) => img.id === id);
  });

  const getImagesByProject = computed(() => (projectId) => {
    return generatedImages.value.filter((img) => img.projectId === projectId);
  });

  // Actions

  // Update generation parameters
  function setGenerationParams(params) {
    generationParams.value = { ...generationParams.value, ...params };
  }

  function updateGenerationParams(params) {
    generationParams.value = { ...generationParams.value, ...params };
  }

  // Set reference images
  function setReferenceImages(images) {
    referenceImages.value = images;
  }

  // Update generation progress
  function updateGenerationProgress(progress) {
    generationProgress.value = progress;
  }

  // Generate images
  async function generateImages(params) {
    loading.value = true;
    generationProgress.value = 0;

    try {
      // Prepare form data
      const formData = new FormData();
      formData.append("batch_count", params.batchCount || 4);
      formData.append("text", params.prompt);
      formData.append("cfg_scale", params.cfgScale || 7.5);

      // Add seed if not random
      if (params.seed && params.seed !== -1) {
        formData.append("seed", params.seed);
      }

      // Add reference images if available
      if (referenceImages.value.length > 0) {
        referenceImages.value.forEach((img) => {
          formData.append("imgs[]", img.id || img);
        });

        // Add similarity strength if provided
        if (params.similarityStrength) {
          formData.append("similarityStrength", params.similarityStrength);
        }
      }

      // Add other parameters
      const additionalParams = {
        height: params.height || 1024,
        width: params.width || 1024,
        style: params.style,
      };
      formData.append("parameters", JSON.stringify(additionalParams));

      // Submit generation task
      const response = await api.post("/img/generate", formData);
      const taskId = response.data.id;

      // Poll for results
      const results = await pollTaskStatus(taskId);

      // Add new images to the store
      if (results && results.length > 0) {
        const newImages = await Promise.all(
          results.map(async (url) => {
            // Get image ID from URL
            const id = url.split("/").pop().split(".")[0];

            // Fetch image data
            const imageResponse = await api.get(`/img/${id}`);

            return {
              id,
              url: API_BASE_URL + url,
              prompt: params.prompt,
              projectId: params.projectId,
              parameters: {
                ...additionalParams,
                cfgScale: params.cfgScale,
                seed: params.seed,
                style: params.style,
              },
              createdAt: new Date().toISOString(),
            };
          })
        );

        // Add to generated images
        generatedImages.value = [...newImages, ...generatedImages.value];
      }

      return results;
    } catch (error) {
      console.error("Image generation failed:", error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // Apply inpainting to an image
  async function applyInpainting(imageId, maskData, prompt, params = {}) {
    loading.value = true;
    generationProgress.value = 0;

    try {
      // Get original image
      const originalImage = getImageById.value(imageId);
      if (!originalImage) {
        throw new Error("Image not found");
      }

      // Convert mask data to blob
      const maskBlob = await fetch(maskData).then((r) => r.blob());

      // Prepare form data
      const formData = new FormData();
      formData.append("batch_count", params.batchCount || 1);
      formData.append("text", prompt);
      formData.append("imgs[]", imageId);
      formData.append("mask_image", maskBlob, "mask.png");
      formData.append("negative_prompt", params.negativePrompt || "");
      formData.append("cfg_scale", params.guidance || 7.5);

      // Add seed if provided
      if (params.seed) {
        formData.append("seed", params.seed);
      }

      // Add other parameters
      const additionalParams = {
        height: params.height || originalImage.parameters?.height || 1024,
        width: params.width || originalImage.parameters?.width || 1024,
        strength: params.strength || 80,
        steps: params.steps || 30,
      };
      formData.append("parameters", JSON.stringify(additionalParams));

      // Submit inpainting task
      const response = await api.post("/img/inpainting", formData);
      const taskId = response.data.id;

      // Poll for results
      const results = await pollTaskStatus(taskId);

      // Add new images to the store
      if (results && results.length > 0) {
        const newImages = await Promise.all(
          results.map(async (url) => {
            // Get image ID from URL
            const id = url.split("/").pop().split(".")[0];

            // Fetch image data
            const imageResponse = await api.get(`/img/${id}`);

            return {
              id,
              url: API_BASE_URL + url,
              prompt,
              projectId: params.projectId || originalImage.projectId,
              parameters: {
                ...additionalParams,
                cfgScale: params.guidance || 7.5,
                negativePrompt: params.negativePrompt,
                inpainted: true,
                sourceImageId: imageId,
              },
              createdAt: new Date().toISOString(),
            };
          })
        );

        // Add to generated images
        generatedImages.value = [...newImages, ...generatedImages.value];

        return newImages[0]; // Return the first image
      }

      return null;
    } catch (error) {
      console.error("Inpainting failed:", error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // Poll task status until completion
  async function pollTaskStatus(taskId) {
    let completed = false;
    let attempts = 0;
    const maxAttempts = 60; // Poll for up to 5 minutes (60 attempts x 5 seconds)

    while (!completed && attempts < maxAttempts) {
      try {
        const response = await api.get(`/img/result/${taskId}`);
        const result = response.data;

        if (result.status === "done") {
          completed = true;
          return result.urls || [];
        } else if (result.status === "error") {
          completed = true;
          throw new Error(result.error || "Task failed");
        }

        // Update progress if available
        if (result.progress) {
          generationProgress.value = result.progress;
        }
      } catch (error) {
        console.error("Error polling task status:", error);
        completed = true;
        throw error;
      }

      if (!completed) {
        // Wait 5 seconds before polling again
        await new Promise((resolve) => setTimeout(resolve, 5000));
        attempts++;
      }
    }

    if (!completed) {
      throw new Error("Task timed out");
    }

    return [];
  }

  // Save an image (e.g., after inpainting or editing)
  async function saveImage(imageData, params = {}) {
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append("projectId", params.projectId);

      // Handle different image data formats
      if (imageData instanceof Blob) {
        formData.append("file", imageData, `image_${Date.now()}.png`);
      } else if (
        typeof imageData === "string" &&
        imageData.startsWith("data:")
      ) {
        // Convert data URL to blob
        const blob = await fetch(imageData).then((r) => r.blob());
        formData.append("file", blob, `image_${Date.now()}.png`);
      } else if (typeof imageData === "string") {
        // Assume it's an image ID
        formData.append("id", imageData);
      }

      // Add metadata
      if (params.prompt) {
        formData.append("prompt", params.prompt);
      }

      if (params.seed) {
        formData.append("seed", params.seed);
      }

      if (params.parameters) {
        formData.append("parameters", JSON.stringify(params.parameters));
      }

      // Save the image
      const response = await api.post("/img/save", formData);
      return response.data;
    } catch (error) {
      console.error("Failed to save image:", error);
      throw error;
    }
  }

  // Delete an image
  async function deleteImage(imageId) {
    try {
      // Not implemented in the API, so just remove from local state
      generatedImages.value = generatedImages.value.filter(
        (img) => img.id !== imageId
      );
      return { success: true };
    } catch (error) {
      console.error("Failed to delete image:", error);
      throw error;
    }
  }

  // 選擇一個圖像（例如，用於設計師修訂頁面）
  function selectImage(image) {
    // 可以在這裡儲存所選圖像的狀態，或執行其他操作
    console.log("選擇圖像：", image.id);
    // 不需要修改任何狀態，只需作為一個事件處理函數
  }

  // Fetch image metadata
  async function fetchImageMetadata(imageId) {
    loading.value = true;
    try {
      const response = await axios.get(`https://ec2.sausagee.party/img/${imageId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching image metadata:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // Fetch image file
  async function fetchImageFile(imageId) {
    loading.value = true;
    try {
      const response = await axios.get(
        `https://ec2.sausagee.party/img/${imageId}/file`,
        { responseType: 'blob' }
      );
      return URL.createObjectURL(response.data);
    } catch (error) {
      console.error('Error fetching image file:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // Delete image
  async function deleteImage(imageId) {
    loading.value = true;
    try {
      const formData = new FormData();
      formData.append('id', imageId);

      await axios.post('https://ec2.sausagee.party/img/delete', formData);

      // Remove image from local state if it exists
      generatedImages.value = generatedImages.value.filter(img => img.id !== imageId);

    } catch (error) {
      console.error('Error deleting image:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // Helper method to get both metadata and file URL
  async function getFullImageData(imageId) {
    try {
      const [metadata, fileUrl] = await Promise.all([
        fetchImageMetadata(imageId),
        fetchImageFile(imageId)
      ]);

      return {
        ...metadata,
        url: fileUrl
      };
    } catch (error) {
      console.error('Error fetching full image data:', error);
      throw error;
    }
  }

  return {
    // State
    generatedImages,
    referenceImages,
    generationParams,
    generationProgress,
    loading,

    // Getters
    getImageById,
    getImagesByProject,

    // Actions
    setGenerationParams,
    updateGenerationParams,
    setReferenceImages,
    updateGenerationProgress,
    generateImages,
    applyInpainting,
    saveImage,
    deleteImage,
    selectImage,
    fetchImageMetadata,
    fetchImageFile,
    getFullImageData,
  };
});
