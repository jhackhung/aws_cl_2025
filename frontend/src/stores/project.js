import { defineStore } from "pinia";
import axios from "axios";

export const useProjectStore = defineStore("project", {
  state: () => ({
    projects: [],
    currentProject: null,
    templates: [],
    loading: false,
    error: null,
  }),

  getters: {
    getProjectById: (state) => (id) => state.projects.find((p) => p.id === id),
    filteredProjects: (state) => (tags) => {
      if (!tags || tags.length === 0) return state.projects;
      return state.projects.filter((p) =>
        p.tags.some((tag) => tags.includes(tag))
      );
    },
  },

  actions: {
    async fetchProjects() {
      this.loading = true;
      try {
        // 模擬 API 調用，實際使用時需要替換為真實的 API 端點
        // const { data } = await axios.get('/api/projects')
        // 臨時使用模擬數據
        const data = [
          {
            id: "1",
            name: "產品設計 A",
            description: "智能手錶的視覺設計",
            tags: ["產品", "科技", "手錶"],
            createdAt: "2025-04-20T12:00:00Z",
            thumbnail: "https://picsum.photos/400/300?random=1",
          },
          {
            id: "2",
            name: "概念設計 B",
            description: "未來風格的傢俱設計",
            tags: ["傢俱", "概念", "未來"],
            createdAt: "2025-04-22T14:30:00Z",
            thumbnail: "https://picsum.photos/400/300?random=2",
          },
          {
            id: "3",
            name: "海報設計 C",
            description: "夏季促銷活動海報",
            tags: ["海報", "促銷", "夏季"],
            createdAt: "2025-04-23T09:15:00Z",
            thumbnail: "https://picsum.photos/400/300?random=3",
          },
        ];
        this.projects = data;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchProjectById(id) {
      if (!id) return;

      this.loading = true;
      try {
        // 模擬 API 調用
        // const { data } = await axios.get(`/api/projects/${id}`)
        // 臨時使用模擬數據
        const data = this.projects.find((p) => p.id === id) || {
          id,
          name: `項目 ${id}`,
          description: "項目描述...",
          tags: [],
          createdAt: new Date().toISOString(),
          images: [],
        };
        this.currentProject = data;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    async createProject(project) {
      this.loading = true;
      try {
        // 模擬 API 調用
        // const { data } = await axios.post('/api/projects', project)
        // 臨時使用模擬數據
        const data = {
          ...project,
          id: Date.now().toString(),
          createdAt: new Date().toISOString(),
          thumbnail: "https://picsum.photos/400/300?random=4",
        };
        this.projects.push(data);
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async updateProject(id, updates) {
      this.loading = true;
      try {
        // 模擬 API 調用
        // const { data } = await axios.put(`/api/projects/${id}`, updates)
        // 臨時使用模擬數據
        const index = this.projects.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.projects[index] = { ...this.projects[index], ...updates };
          if (this.currentProject && this.currentProject.id === id) {
            this.currentProject = { ...this.currentProject, ...updates };
          }
          return this.projects[index];
        }
        throw new Error("找不到項目");
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async deleteProject(id) {
      this.loading = true;
      try {
        // 模擬 API 調用
        // await axios.delete(`/api/projects/${id}`)
        // 臨時使用模擬數據
        const index = this.projects.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.projects.splice(index, 1);
          if (this.currentProject && this.currentProject.id === id) {
            this.currentProject = null;
          }
          return true;
        }
        throw new Error("找不到項目");
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchTemplates() {
      this.loading = true;
      try {
        // 模擬 API 調用
        // const { data } = await axios.get('/api/templates')
        // 臨時使用模擬數據
        const data = [
          {
            id: "t1",
            name: "產品設計模板",
            description: "適合各種產品設計專案",
            thumbnail: "https://picsum.photos/400/300?random=5",
          },
          {
            id: "t2",
            name: "海報設計模板",
            description: "適合各種海報和廣告設計",
            thumbnail: "https://picsum.photos/400/300?random=6",
          },
          {
            id: "t3",
            name: "概念藝術模板",
            description: "適合概念藝術和插畫設計",
            thumbnail: "https://picsum.photos/400/300?random=7",
          },
        ];
        this.templates = data;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
});
