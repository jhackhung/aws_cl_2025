// 應用程式所有翻譯字符串
const translations = {
  "zh-TW": {
    // 導航菜單
    project: "專案",
    gallery: "圖庫",
    designInput: "設計輸入",
    aiGenerate: "AI 生成",
    settings: "設定",

    // 按鈕和操作
    save: "保存",
    cancel: "取消",
    confirm: "確認",
    delete: "刪除",
    edit: "編輯",
    generate: "生成",
    upload: "上傳",
    download: "下載",
    preview: "預覽",
    apply: "應用",
    reset: "重置",

    // 專案相關
    newProject: "新建專案",
    projectName: "專案名稱",
    projectDescription: "專案描述",
    projectType: "專案類型",
    createDate: "創建日期",
    lastModified: "最後修改",
    noProjects: "暫無專案",
    projectTitle: "設計畫廊",
    projectDesc: "品牌設計資料庫",

    // 設計輸入
    designBrief: "設計需求",
    designStyle: "設計風格",
    colorScheme: "配色方案",
    layoutPreference: "版面偏好",
    targetAudience: "目標受眾",
    reference: "參考資料",

    // AI生成
    generationOptions: "生成選項",
    variationCount: "變體數量",
    generationProgress: "生成進度",
    regenerate: "重新生成",
    saveToGallery: "保存到圖庫",

    // 設定
    language: "語言",
    theme: "主題",
    darkMode: "暗色模式",
    lightMode: "亮色模式",
    notifications: "通知",
    account: "帳戶",
    about: "關於我們",
    privacy: "隱私政策",
    terms: "使用條款",
    languageSettings: "語言設定",
    themeSettings: "主題設定",
    selectLanguage: "選擇語言",
    instructions: "使用說明",
    homePage: "首頁",
    "Go To ": "前往",

    // 錯誤訊息
    errorOccurred: "發生錯誤",
    tryAgain: "請重試",
    networkError: "網絡錯誤",
    pageNotFound: "頁面未找到",

    // 設計流程步驟
    designProcess: "設計流程",
    designProcessSubtitle: "從概念到完成只需幾分鐘",

    // Step 1: Design Input
    designInputTitle: "設計資料輸入",
    designInputDescription: "設置設計參數與構想，提供 AI 生成精確的設計指導",

    // Step 2: AI Generate
    aiGenerateTitle: "AI 生成設計",
    aiGenerateDescription:
      "我們的平台利用多種 AI 模型，包括 Stability AI、Titan ImageGenerator G1 v2 和 Nova Canvas，生成多樣化的設計選項",

    // Step 3: Designer Revision
    designerRevisionTitle: "設計師精修",
    designerRevisionDescription:
      "使用 Nova Canvas 工具手動修改圖像，或上傳您自己的藍圖以進行 AI 增強和整合",

    // Step 4: Integration
    integrationTitle: "專案管理歷程",
    integrationDescription:
      "將設計圖像保存到您的專案中，將專案保存為模板，並為新圖像添加標籤",
    galleryTitle: "我的圖片生成歷程",
    galleryDescription: "瀏覽和管理此專案的圖像",

    // 頁面標題
    designInputPageTitle: "設計輸入",
    aiGeneratePageTitle: "AI 生成",
    designerRevisionPageTitle: "設計師精修",
    integrationPageTitle: "專案管理",

    // 步驟提示
    step1: "第一步",
    step2: "第二步",
    step3: "第三步",
    step4: "第四步",

    // 步驟說明
    step1Desc: "收集設計參數與構想",
    step2Desc: "快速生成多樣且符合品牌風格的概念圖",
    step3Desc: "手動細修與創意微調",
    step4Desc: "我的圖片生成歷程",
  },
  "en-US": {
    // Navigation menu
    project: "Project",
    gallery: "Gallery",
    designInput: "Design Input",
    aiGenerate: "AI Generate",
    settings: "Settings",

    // Buttons and operations
    save: "Save",
    cancel: "Cancel",
    confirm: "Confirm",
    delete: "Delete",
    edit: "Edit",
    generate: "Generate",
    upload: "Upload",
    download: "Download",
    preview: "Preview",
    apply: "Apply",
    reset: "Reset",

    // Project related
    newProject: "New Project",
    projectName: "Project Name",
    projectDescription: "Project Description",
    projectType: "Project Type",
    createDate: "Created Date",
    lastModified: "Last Modified",
    noProjects: "No Projects",
    projectTitle: "Design Gallery",
    projectDesc: "Brand Design Database",

    // Design input
    designBrief: "Design Brief",
    designStyle: "Design Style",
    colorScheme: "Color Scheme",
    layoutPreference: "Layout Preference",
    targetAudience: "Target Audience",
    reference: "Reference",

    // AI generation
    generationOptions: "Generation Options",
    variationCount: "Variation Count",
    generationProgress: "Generation Progress",
    regenerate: "Regenerate",
    saveToGallery: "Save to Gallery",

    // Settings
    language: "Language",
    theme: "Theme",
    darkMode: "Dark Mode",
    lightMode: "Light Mode",
    notifications: "Notifications",
    account: "Account",
    about: "About Us",
    privacy: "Privacy Policy",
    terms: "Terms of Service",
    languageSettings: "Language Settings",
    themeSettings: "Theme Settings",
    selectLanguage: "Select Language",
    instructions: "Instructions",
    homePage: "Home Page",
    "Go To ": "Go To",

    // Error messages
    errorOccurred: "An error occurred",
    tryAgain: "Please try again",
    networkError: "Network error",
    pageNotFound: "Page not found",

    // Design process steps
    designProcess: "Design Process",
    designProcessSubtitle: "From concept to completion in just minutes",

    // Step 1: Design Input
    designInputTitle: "Design Input",
    designInputDescription:
      "Set design parameters and concepts to provide precise design guidance for AI generation",

    // Step 2: AI Generate
    aiGenerateTitle: "AI Generate Design",
    aiGenerateDescription:
      "Our platform leverages multiple AI models, including Stability AI, Titan ImageGenerator G1 v2, and Nova Canvas, to generate diverse design options",

    // Step 3: Designer Revision
    designerRevisionTitle: "Designer Revision",
    designerRevisionDescription:
      "Use Nova Canvas tools to manually modify images or upload your own blueprint for AI enhancement and integration",

    // Step 4: Integration
    integrationTitle: "Project Management History",
    integrationDescription:
      "Save designed images to your projects, save projects as templates, and add tags to new images",
    galleryTitle: "My Image Generation History",
    galleryDescription: "Browse and manage images for this project",

    // Page titles
    designInputPageTitle: "Design Input",
    aiGeneratePageTitle: "AI Generate",
    designerRevisionPageTitle: "Designer Revision",
    integrationPageTitle: "Project Management",

    // Step prompts
    step1: "Step 1",
    step2: "Step 2",
    step3: "Step 3",
    step4: "Step 4",

    // Step descriptions
    step1Desc: "Collect design parameters and concepts",
    step2Desc: "Generate diverse concepts that match brand style",
    step3Desc: "Manual refinement and creative adjustments",
    step4Desc: "My image generation history",
  },
  "ko-KR": {
    // 導航菜單
    project: "프로젝트",
    gallery: "갤러리",
    designInput: "디자인 입력",
    aiGenerate: "AI 생성",
    settings: "설정",

    // 按鈕和操作
    save: "저장",
    cancel: "취소",
    confirm: "확인",
    delete: "삭제",
    edit: "편집",
    generate: "생성",
    upload: "업로드",
    download: "다운로드",
    preview: "미리보기",
    apply: "적용",
    reset: "초기화",

    // 專案相關
    newProject: "새 프로젝트",
    projectName: "프로젝트 이름",
    projectDescription: "프로젝트 설명",
    projectType: "프로젝트 유형",
    createDate: "생성일",
    lastModified: "최종 수정일",
    noProjects: "프로젝트 없음",
    projectTitle: "디자인 갤러리",
    projectDesc: "브랜드 디자인 데이터베이스",

    // 設計輸入
    designBrief: "디자인 요구사항",
    designStyle: "디자인 스타일",
    colorScheme: "색상 구성",
    layoutPreference: "레이아웃 설정",
    targetAudience: "타겟 고객",
    reference: "참고 자료",

    // AI生成
    generationOptions: "생성 옵션",
    variationCount: "변형 수",
    generationProgress: "생성 진행률",
    regenerate: "재생성",
    saveToGallery: "갤러리에 저장",

    // 設定
    language: "언어",
    theme: "테마",
    darkMode: "다크 모드",
    lightMode: "라이트 모드",
    notifications: "알림",
    account: "계정",
    about: "소개",
    privacy: "개인정보 처리방침",
    terms: "이용약관",
    languageSettings: "언어 설정",
    themeSettings: "테마 설정",
    selectLanguage: "언어 선택",
    instructions: "사용 방법",
    homePage: "홈페이지",
    "Go To ": "이동",

    // 錯誤訊息
    errorOccurred: "오류가 발생했습니다",
    tryAgain: "다시 시도해주세요",
    networkError: "네트워크 오류",
    pageNotFound: "페이지를 찾을 수 없습니다",

    // 設計流程步驟
    designProcess: "디자인 프로세스",
    designProcessSubtitle: "컨셉부터 완성까지 단 몇 분이면 됩니다",

    // Step 1: Design Input
    designInputTitle: "디자인 매개변수 및 참조 자료 입력",
    designInputDescription:
      "색상, 재질, 크기와 같은 디자인 매개변수를 설정하거나 시장 트렌드와 영감을 찾기 위해 웹 크롤링 시스템을 사용하세요.",

    // Step 2: AI Generate
    aiGenerateTitle: "AI 디자인 컨셉 생성",
    aiGenerateDescription:
      "우리 플랫폼은 Stability AI, Titan ImageGenerator G1 v2, Nova Canvas를 포함한 다양한 AI 모델을 활용하여 다양한 디자인 옵션을 생성합니다.",

    // Step 3: Designer Revision
    designerRevisionTitle: "디자이너 수정",
    designerRevisionDescription:
      "Nova Canvas 도구를 사용하여 이미지를 수동으로 수정하거나 자체 청사진을 업로드하여 AI 향상 및 통합을 위해 3단계로 진행할 수 있습니다.",

    // Step 4: Integration
    integrationTitle: "브랜드 디자인 갤러리에 통합",
    integrationDescription:
      "설계된 이미지를 프로젝트에 저장하고, 프로젝트를 템플릿으로 저장하며, 새 이미지에 태그를 추가할 수 있습니다.",
    galleryTitle: "내 이미지 생성 기록",
    galleryDescription: "이 프로젝트의 이미지 탐색 및 관리",

    // 頁面標題
    designInputPageTitle: "디자인 입력",
    aiGeneratePageTitle: "AI 생성",
    designerRevisionPageTitle: "디자이너 수정",
    integrationPageTitle: "갤러리 통합",

    // 步驟提示
    step1: "1단계",
    step2: "2단계",
    step3: "3단계",
    step4: "4단계",

    // 步驟說明
    step1Desc: "디자인 매개변수와 참조 자료를 입력하세요",
    step2Desc: "AI가 다양한 디자인 옵션을 생성합니다",
    step3Desc: "디자이너가 세부 사항을 수정합니다",
    step4Desc: "최종 디자인을 갤러리에 저장합니다",
  },
};

export default translations;
