<template>
  <NCard class="project-card" hoverable @click="$emit('click')">
    <template #cover>
      <div class="project-thumbnail">
        <NImage
          :src="project.thumbnail"
          object-fit="cover"
          fallback-src="https://www.naiveui.com/assets/no-image.png"
          :alt="project.name"
        />
      </div>
    </template>

    <div class="project-info">
      <h3 class="project-title">{{ project.name }}</h3>
      <p class="project-description">{{ project.description }}</p>

      <div class="project-tags">
        <NTag
          v-for="tag in project.tags"
          :key="tag"
          size="small"
          :bordered="false"
          type="info"
        >
          {{ tag }}
        </NTag>
      </div>

      <div class="project-meta">
        <span class="project-date">{{ formatDate(project.createdAt) }}</span>
      </div>
    </div>
  </NCard>
</template>

<script setup>
import { NCard, NImage, NTag } from "naive-ui";

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
});

defineEmits(["click"]);

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-TW", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
</script>

<style scoped>
.project-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
  height: 100%; /* Make card fill the grid cell height */
  width: 100%; /* Make card fill the grid cell width */
}

.project-card:hover {
  transform: translateY(-4px);
}

.project-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 */
  overflow: hidden;
  flex: none;
}

.project-thumbnail :deep(.n-image) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.project-info {
  padding: 12px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.project-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.project-meta {
  font-size: 12px;
  color: #999;
  margin-top: auto; /* Push meta to bottom of card */
}
</style>