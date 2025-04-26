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
  import { ref } from 'vue';
  import Sidebar from './Sidebar.vue';
  
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
  }
  
  .main-content {
    flex: 1;
    margin-left: 250px;
    transition: margin-left 0.3s ease;
    width: calc(100% - 250px);
  }
  
  .sidebar-collapsed .main-content {
    margin-left: 64px;
    width: calc(100% - 64px);
  }
  
  @media (max-width: 768px) {
    .main-content {
      margin-left: 0;
      width: 100%;
    }
    
    .sidebar-collapsed .main-content {
      margin-left: 0;
      width: 100%;
    }
  }
  </style>