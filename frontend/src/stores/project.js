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
        // Get list of project IDs
        const response = await axios.get('https://ec2.sausagee.party/projects');
        const { projects: projectIds } = response.data;

        // Fetch details for each project
        const projectDetails = await Promise.all(
          projectIds.map(async (id) => {
            const detailResponse = await axios.get(`https://ec2.sausagee.party/project/${id}`);
            return detailResponse.data;
          })
        );

        this.projects = projectDetails;
        this.error = null;
      } catch (err) {
        console.error('Error fetching projects:', err);
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchProjectById(id) {
      if (!id) return;

      this.loading = true;
      try {
        const response = await axios.get(`https://ec2.sausagee.party/project/${id}`);
        this.currentProject = response.data;
        this.error = null;
        return response.data;
      } catch (err) {
        console.error('Error fetching project:', err);
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async createProject(project) {
      this.loading = true;
      try {
        const formData = new FormData();
        formData.append('name', project.name);
        formData.append('description', project.description);
        if (project.templateId) {
          formData.append('templateId', project.templateId);
        }

        const response = await axios.post('https://ec2.sausagee.party/project/create', formData);
        const newProjectId = response.data.id;

        // Fetch the created project details
        const newProject = await this.fetchProjectById(newProjectId);
        this.projects.push(newProject);
        return newProject;
      } catch (err) {
        console.error('Error creating project:', err);
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async updateProject(id, updates) {
      this.loading = true;
      try {
        // Update project implementation will be added later when the endpoint is ready
        const updatedProject = await this.fetchProjectById(id);
        const index = this.projects.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.projects[index] = updatedProject;
        }
        return updatedProject;
      } catch (err) {
        console.error('Error updating project:', err);
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async deleteProject(id) {
      this.loading = true;
      try {
        const formData = new FormData();
        formData.append('id', id);

        await axios.post('https://ec2.sausagee.party/project/delete', formData);
        
        // Remove from local state
        const index = this.projects.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.projects.splice(index, 1);
        }
        if (this.currentProject?.id === id) {
          this.currentProject = null;
        }
        return true;
      } catch (err) {
        console.error('Error deleting project:', err);
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
