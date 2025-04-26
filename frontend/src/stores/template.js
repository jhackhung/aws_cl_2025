import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useTemplateStore = defineStore('template', () => {
  // 狀態
  const templates = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  
  // 最近使用的模板ID
  const recentlyUsedTemplateIds = ref([]);
  
  // 模擬一些樣本模板數據（實際應用中將從API獲取）
  const sampleTemplates = [
    {
      id: '1',
      name: '現代簡約風格設計',
      description: '適合各種簡約風格的產品設計，強調簡潔線條和功能性',
      category: 'product',
      thumbnail: 'https://picsum.photos/400/300?random=1',
      tags: ['簡約', '現代', '產品'],
      featured: true,
      isNew: false,
      createdAt: '2024-03-10T08:30:00.000Z',
      updatedAt: '2024-03-10T08:30:00.000Z',
      params: {
        style: 'modern_minimalist',
        size: '1024x1024',
        prompt: '現代簡約風格的產品設計，清晰線條，簡單幾何形狀，白色和淺灰色為主',
        negativePrompt: '過度複雜，華麗紋飾，混亂佈局'
      },
      relatedImages: [
        { id: '101', url: 'https://picsum.photos/400/300?random=10' },
        { id: '102', url: 'https://picsum.photos/400/300?random=11' }
      ]
    },
    {
      id: '2',
      name: '復古工業風格模板',
      description: '帶有復古工業元素的設計模板，適合創建具有歷史感的產品設計',
      category: 'product',
      thumbnail: 'https://picsum.photos/400/300?random=2',
      tags: ['復古', '工業', '金屬質感'],
      featured: false,
      isNew: true,
      createdAt: '2024-04-05T10:15:00.000Z',
      updatedAt: '2024-04-05T10:15:00.000Z',
      params: {
        style: 'industrial',
        size: '1024x1024',
        prompt: '復古工業風格設計，帶有金屬質感和舊化處理，使用銅、鐵等材料元素',
        negativePrompt: '塑料感，現代感，鮮豔色彩'
      },
      relatedImages: [
        { id: '201', url: 'https://picsum.photos/400/300?random=20' }
      ]
    },
    {
      id: '3',
      name: '有機自然風格',
      description: '以自然元素為靈感的設計模板，強調有機形狀和環保材質',
      category: 'product',
      thumbnail: 'https://picsum.photos/400/300?random=3',
      tags: ['自然', '有機', '環保'],
      featured: true,
      isNew: false,
      createdAt: '2024-03-22T14:40:00.000Z',
      updatedAt: '2024-03-22T14:40:00.000Z',
      params: {
        style: 'natural_organic',
        size: '1024x1024',
        prompt: '有機設計風格，使用自然曲線和紋理，木材、竹子等天然材質表現',
        negativePrompt: '幾何形狀，銳角，工業感'
      },
      relatedImages: [
        { id: '301', url: 'https://picsum.photos/400/300?random=30' },
        { id: '302', url: 'https://picsum.photos/400/300?random=31' },
        { id: '303', url: 'https://picsum.photos/400/300?random=32' }
      ]
    },
    {
      id: '4',
      name: '品牌識別套件',
      description: '完整的品牌識別設計模板，包含標誌、顏色方案和應用示例',
      category: 'branding',
      thumbnail: 'https://picsum.photos/400/300?random=4',
      tags: ['品牌', '標誌', '識別系統'],
      featured: false,
      isNew: false,
      createdAt: '2024-02-15T09:20:00.000Z',
      updatedAt: '2024-02-15T09:20:00.000Z',
      params: {
        style: 'modern_minimalist',
        size: '1920x1080',
        prompt: '現代品牌識別設計，包含簡潔標誌、一致的顏色方案和簡約的排版',
        negativePrompt: '複雜圖案，不協調的顏色，破碎的佈局'
      },
      relatedImages: [
        { id: '401', url: 'https://picsum.photos/400/300?random=40' },
        { id: '402', url: 'https://picsum.photos/400/300?random=41' }
      ]
    },
    {
      id: '5',
      name: '科技未來感設計',
      description: '充滿未來科技感的設計模板，適合創新產品和數位介面',
      category: 'product',
      thumbnail: 'https://picsum.photos/400/300?random=5',
      tags: ['科技', '未來', '創新'],
      featured: false,
      isNew: true,
      createdAt: '2024-04-10T16:50:00.000Z',
      updatedAt: '2024-04-10T16:50:00.000Z',
      params: {
        style: 'tech_futuristic',
        size: '1024x1024',
        prompt: '未來科技風格設計，藍色光效，高科技材質和細節，懸浮元素',
        negativePrompt: '老舊感，自然元素，復古風格'
      },
      relatedImages: [
        { id: '501', url: 'https://picsum.photos/400/300?random=50' },
        { id: '502', url: 'https://picsum.photos/400/300?random=51' }
      ]
    },
    {
      id: '6',
      name: '包裝設計模板',
      description: '高端產品包裝設計，適合化妝品、食品或精品類產品',
      category: 'package',
      thumbnail: 'https://picsum.photos/400/300?random=6',
      tags: ['包裝', '豪華', '精緻'],
      featured: true,
      isNew: false,
      createdAt: '2024-01-20T11:30:00.000Z',
      updatedAt: '2024-01-20T11:30:00.000Z',
      params: {
        style: 'modern_minimalist',
        size: '1024x1024',
        prompt: '高端簡約包裝設計，精緻質感，適合奢侈品牌，使用白色、金色和黑色元素',
        negativePrompt: '複雜圖案，廉價感，俗氣，過度裝飾'
      },
      relatedImages: [
        { id: '601', url: 'https://picsum.photos/400/300?random=60' },
        { id: '602', url: 'https://picsum.photos/400/300?random=61' }
      ]
    },
    {
      id: '7',
      name: '北歐風格傢俱',
      description: '簡約北歐風格的傢俱設計，適合現代家居環境',
      category: 'interior',
      thumbnail: 'https://picsum.photos/400/300?random=7',
      tags: ['北歐', '傢俱', '木質'],
      featured: false,
      isNew: false,
      createdAt: '2023-12-05T09:20:00.000Z',
      updatedAt: '2024-01-10T14:15:00.000Z',
      params: {
        style: 'scandinavian',
        size: '1024x1024',
        prompt: '北歐風格傢俱設計，簡約線條，淺色木材，自然材質，舒適功能性',
        negativePrompt: '華麗裝飾，暗色調，繁複設計'
      },
      relatedImages: [
        { id: '701', url: 'https://picsum.photos/400/300?random=70' }
      ]
    },
    {
      id: '8',
      name: '社交媒體海報',
      description: '現代風格的社交媒體貼文和故事模板，適合品牌推廣',
      category: 'graphic',
      thumbnail: 'https://picsum.photos/400/300?random=8',
      tags: ['社媒', '海報', '推廣'],
      featured: true,
      isNew: false,
      createdAt: '2024-02-28T16:40:00.000Z',
      updatedAt: '2024-02-28T16:40:00.000Z',
      params: {
        style: 'modern_minimalist',
        size: '1080x1920',
        prompt: '時尚現代的社交媒體海報設計，簡潔排版，明亮配色，清晰品牌標識',
        negativePrompt: '文字過多，雜亂佈局，模糊元素'
      },
      relatedImages: [
        { id: '801', url: 'https://picsum.photos/400/300?random=80' },
        { id: '802', url: 'https://picsum.photos/400/300?random=81' },
        { id: '803', url: 'https://picsum.photos/400/300?random=82' }
      ]
    }
  ];
  
  // 獲取所有模板
  const fetchTemplates = async () => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // 從API獲取模板，這裡模擬API呼叫
      // 實際應用中應該替換為真實的API呼叫
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // 使用樣本數據
      templates.value = [...sampleTemplates];
      
      return templates.value;
    } catch (err) {
      console.error('獲取模板失敗:', err);
      error.value = '無法載入模板數據';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 根據ID獲取模板
  const getTemplateById = (id) => {
    return templates.value.find(template => template.id === id);
  };
  
  // 添加最近使用的模板ID
  const addRecentlyUsedTemplate = (id) => {
    // 如果ID已存在，先移除它
    recentlyUsedTemplateIds.value = recentlyUsedTemplateIds.value.filter(templateId => templateId !== id);
    
    // 添加到列表最前面
    recentlyUsedTemplateIds.value.unshift(id);
    
    // 只保留最近的5個
    if (recentlyUsedTemplateIds.value.length > 5) {
      recentlyUsedTemplateIds.value = recentlyUsedTemplateIds.value.slice(0, 5);
    }
    
    // 可以選擇將最近使用的模板ID保存到本地存儲
    localStorage.setItem('recentlyUsedTemplates', JSON.stringify(recentlyUsedTemplateIds.value));
  };
  
  // 獲取最近使用的模板
  const getRecentlyUsedTemplates = computed(() => {
    return recentlyUsedTemplateIds.value
      .map(id => templates.value.find(template => template.id === id))
      .filter(Boolean); // 過濾掉未找到的模板
  });
  
  // 獲取精選模板
  const getFeaturedTemplates = computed(() => {
    return templates.value.filter(template => template.featured);
  });
  
  // 獲取特定類別的模板
  const getTemplatesByCategory = (category) => {
    return templates.value.filter(template => template.category === category);
  };
  
  // 創建新模板
  const createTemplate = async (templateData) => {
    isLoading.value = true;
    
    try {
      // 模擬API調用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 生成唯一ID和時間戳
      const newId = `template-${Date.now()}`;
      const now = new Date().toISOString();
      
      // 創建新模板對象
      const newTemplate = {
        id: newId,
        createdAt: now,
        updatedAt: now,
        isNew: true,
        featured: false,
        ...templateData
      };
      
      // 將新模板添加到列表
      templates.value.unshift(newTemplate);
      
      return newTemplate;
    } catch (err) {
      console.error('創建模板失敗:', err);
      error.value = '無法創建新模板';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 更新模板
  const updateTemplate = async (id, updateData) => {
    isLoading.value = true;
    
    try {
      // 檢查模板是否存在
      const templateIndex = templates.value.findIndex(template => template.id === id);
      if (templateIndex === -1) {
        throw new Error('模板不存在');
      }
      
      // 模擬API調用
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // 更新模板
      const updatedTemplate = {
        ...templates.value[templateIndex],
        ...updateData,
        updatedAt: new Date().toISOString()
      };
      
      // 替換原始模板
      templates.value[templateIndex] = updatedTemplate;
      
      return updatedTemplate;
    } catch (err) {
      console.error('更新模板失敗:', err);
      error.value = '無法更新模板';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 刪除模板
  const deleteTemplate = async (id) => {
    isLoading.value = true;
    
    try {
      // 檢查模板是否存在
      const templateExists = templates.value.some(template => template.id === id);
      if (!templateExists) {
        throw new Error('模板不存在');
      }
      
      // 模擬API調用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 從列表中移除模板
      templates.value = templates.value.filter(template => template.id !== id);
      
      // 如果該模板在最近使用列表中，也將其移除
      recentlyUsedTemplateIds.value = recentlyUsedTemplateIds.value.filter(templateId => templateId !== id);
      localStorage.setItem('recentlyUsedTemplates', JSON.stringify(recentlyUsedTemplateIds.value));
      
      return true;
    } catch (err) {
      console.error('刪除模板失敗:', err);
      error.value = '無法刪除模板';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // 初始化 - 從本地存儲加載最近使用的模板
  const initStore = () => {
    try {
      const storedRecentlyUsed = localStorage.getItem('recentlyUsedTemplates');
      if (storedRecentlyUsed) {
        recentlyUsedTemplateIds.value = JSON.parse(storedRecentlyUsed);
      }
    } catch (err) {
      console.error('加載本地存儲的模板數據失敗:', err);
    }
  };
  
  // 在創建 store 時初始化
  initStore();
  
  return {
    templates,
    isLoading,
    error,
    recentlyUsedTemplateIds,
    fetchTemplates,
    getTemplateById,
    addRecentlyUsedTemplate,
    getRecentlyUsedTemplates,
    getFeaturedTemplates,
    getTemplatesByCategory,
    createTemplate,
    updateTemplate,
    deleteTemplate
  };
});