<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <Sidebar
      :collapsed="sidebarCollapsed"
      @collapse-change="handleSidebarCollapse"
    />

    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import Sidebar from "./Sidebar.vue";

const sidebarCollapsed = ref(false);

const handleSidebarCollapse = (collapsed) => {
  sidebarCollapsed.value = collapsed;
};
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  position: relative;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  transition: all 0.3s ease;
  width: calc(100% - 250px);
  overflow-x: hidden;
}

.sidebar-collapsed .main-content {
  margin-left: 64px;
  width: calc(100% - 64px);
}

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .main-content {
    margin-left: 0;
    width: 100%;
    margin-top: 50px; /* 為移動版側邊欄騰出空間 */
  }

  .sidebar-collapsed .main-content {
    margin-left: 0;
    width: 100%;
  }
}
</style>
