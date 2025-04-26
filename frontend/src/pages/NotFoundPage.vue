<template>
  <div class="not-found-page">
    <NResult
      status="404"
      title="頁面未找到"
      description="您嘗試訪問的頁面不存在或已被移除"
    >
      <template #footer>
        <NButton type="primary" @click="goHome"> 返回首頁 </NButton>
      </template>
    </NResult>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { NResult, NButton } from "naive-ui";

const router = useRouter();

const goHome = () => {
  router.push({ name: "home" });
};
</script>

<style scoped>
.not-found-page {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}
</style>
