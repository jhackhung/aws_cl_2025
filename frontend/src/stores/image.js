import { defineStore } from "pinia";
import axios from "axios";

export const useImageStore = defineStore("image", {
  state: () => ({
    generatedImages: [],
    selectedImage: null,
    generationParams: {
      prompt: "",
      negativePrompt: "",
      strength: 75,
      steps: 30,
      seed: Math.floor(Math.random() * 1000000),
      batchCount: 4,
    },
    referenceImages: [],
    loading: false,
    generationProgress: 0,
    error: null,
  }),

  getters: {
    getImageById: (state) => (id) =>
      state.generatedImages.find((img) => img.id === id),
    filteredImages: (state) => (tags) => {
      if (!tags || tags.length === 0) return state.generatedImages;
      return state.generatedImages.filter((img) =>
        img.tags.some((tag) => tags.includes(tag))
      );
    },
  },

  actions: {
    async generateImages(params) {
      this.loading = true;
      this.generationProgress = 0;

      try {
        // 實際使用時需要替換為真實的 API 端點
        // const { data } = await axios.post('/api/images/generate', {
        //   ...this.generationParams,
        //   ...params
        // })

        // 模擬進度更新
        const progressInterval = setInterval(() => {
          this.generationProgress += 10;
          if (this.generationProgress >= 100) {
            clearInterval(progressInterval);
          }
        }, 500);

        // 模擬 API 調用延遲
        await new Promise((resolve) => setTimeout(resolve, 5000));

        // 清除進度更新
        clearInterval(progressInterval);
        this.generationProgress = 100;

        // 模擬生成的圖像數據
        const newImages = Array(
          params?.batchCount || this.generationParams.batchCount
        )
          .fill(0)
          .map((_, index) => ({
            id: `gen-${Date.now()}-${index}`,
            projectId: params?.projectId || null,
            prompt: params?.prompt || this.generationParams.prompt,
            url: `https://picsum.photos/800/600?random=${Date.now() + index}`,
            thumbnail: `https://picsum.photos/400/300?random=${
              Date.now() + index
            }`,
            createdAt: new Date().toISOString(),
            params: {
              ...this.generationParams,
              ...params,
            },
            tags: [],
          }));

        // 添加到生成的圖像列表
        this.generatedImages = [...newImages, ...this.generatedImages];

        return newImages;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    setGenerationParams(params) {
      this.generationParams = {
        ...this.generationParams,
        ...params,
      };
    },

    setReferenceImages(images) {
      this.referenceImages = images.map(img => 
        typeof img === 'string' ? { url: img, prompt: '' } : img
      );
    },

    selectImage(image) {
      this.selectedImage = image;
    },

    async applyInpainting(imageId, mask, prompt, params = {}) {
      this.loading = true;
      this.generationProgress = 0;

      try {
        const originalImage = this.getImageById(imageId);
        if (!originalImage) {
          throw new Error("找不到原始圖像");
        }

        // 實際使用時需要替換為真實的 API 端點
        // const { data } = await axios.post('/api/images/inpaint', {
        //   imageId,
        //   mask,
        //   prompt,
        //   ...params
        // })

        // 模擬進度更新
        const progressInterval = setInterval(() => {
          this.generationProgress += 10;
          if (this.generationProgress >= 100) {
            clearInterval(progressInterval);
          }
        }, 500);

        // 模擬 API 調用延遲
        await new Promise((resolve) => setTimeout(resolve, 3000));

        // 清除進度更新
        clearInterval(progressInterval);
        this.generationProgress = 100;

        // 模擬生成的新圖像數據
        const newImage = {
          id: `inpaint-${Date.now()}`,
          projectId: originalImage.projectId,
          prompt: prompt || originalImage.prompt,
          url: `https://picsum.photos/800/600?random=${Date.now()}`,
          thumbnail: `https://picsum.photos/400/300?random=${Date.now()}`,
          createdAt: new Date().toISOString(),
          originalImageId: imageId,
          params: {
            ...originalImage.params,
            ...params,
          },
          tags: [...(originalImage.tags || [])],
        };

        // 添加到生成的圖像列表
        this.generatedImages = [newImage, ...this.generatedImages];

        return newImage;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async saveImage(imageId, updates) {
      this.loading = true;

      try {
        const index = this.generatedImages.findIndex(
          (img) => img.id === imageId
        );
        if (index === -1) {
          throw new Error("找不到圖像");
        }

        // 實際使用時需要替換為真實的 API 端點
        // const { data } = await axios.put(`/api/images/${imageId}`, updates)

        // 模擬 API 調用
        const updatedImage = {
          ...this.generatedImages[index],
          ...updates,
        };

        // 更新圖像
        this.generatedImages.splice(index, 1, updatedImage);

        // 如果是當前選擇的圖像，也更新它
        if (this.selectedImage && this.selectedImage.id === imageId) {
          this.selectedImage = updatedImage;
        }

        return updatedImage;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async deleteImage(imageId) {
      this.loading = true;

      try {
        // 實際使用時需要替換為真實的 API 端點
        // await axios.delete(`/api/images/${imageId}`)

        // 從列表中移除圖像
        this.generatedImages = this.generatedImages.filter(
          (img) => img.id !== imageId
        );

        // 如果是當前選擇的圖像，清除選擇
        if (this.selectedImage && this.selectedImage.id === imageId) {
          this.selectedImage = null;
        }

        return true;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});
