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
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
}

.project-card:hover {
  transform: translateY(-4px);
}

.project-thumbnail {
  height: 200px;
  overflow: hidden;
}

.project-info {
  padding: 8px 0;
}

.project-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
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
}
</style>
