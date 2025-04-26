import { defineAsyncComponent } from "vue";

// 使用非同步元件載入，提高性能
const ProjectPage = defineAsyncComponent(() =>
  import("../pages/ProjectPage.vue")
);
const DesignInputPage = defineAsyncComponent(() =>
  import("../pages/DesignInputPage.vue")
);
const AiGeneratePage = defineAsyncComponent(() =>
  import("../pages/AiGeneratePage.vue")
);
const DesignerRevisionPage = defineAsyncComponent(() =>
  import("../pages/DesignerRevisionPage.vue")
);
const GalleryPage = defineAsyncComponent(() =>
  import("../pages/GalleryPage.vue")
);
const SettingsPage = defineAsyncComponent(() =>
  import("../pages/SettingsPage.vue")
);
const NotFoundPage = defineAsyncComponent(() =>
  import("../pages/NotFoundPage.vue")
);

// 路由配置
const routes = [
  {
    path: "/",
    component: ProjectPage,
    name: "home",
  },
  {
    path: "/project/:id?",
    component: ProjectPage,
    name: "project",
  },
  {
    path: "/design/:projectId",
    component: DesignInputPage,
    name: "design-input",
  },
  {
    path: "/generate/:projectId",
    component: AiGeneratePage,
    name: "ai-generate",
  },
  {
    path: "/revise/:projectId/:imageId",
    component: DesignerRevisionPage,
    name: "designer-revision",
  },
  {
    path: "/gallery",
    component: GalleryPage,
    name: "gallery",
  },
  {
    path: "/settings",
    component: SettingsPage,
    name: "settings",
  },
  {
    path: "/:pathMatch(.*)*",
    component: NotFoundPage,
    name: "not-found",
  },
];

export default routes;
