<template>
  <div class="tag-selector">
    <div class="tag-list">
      <NTag
        v-for="tag in tags"
        :key="tag"
        :type="selected.includes(tag) ? 'primary' : 'default'"
        :bordered="false"
        class="selectable-tag"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </NTag>
    </div>
  </div>
</template>

<script setup>
import { NTag } from "naive-ui";

const props = defineProps({
  tags: {
    type: Array,
    default: () => [],
  },
  selected: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:selected"]);

// 切換標籤選中狀態
const toggleTag = (tag) => {
  const newSelected = [...props.selected];
  const index = newSelected.indexOf(tag);

  if (index === -1) {
    newSelected.push(tag);
  } else {
    newSelected.splice(index, 1);
  }

  emit("update:selected", newSelected);
};
</script>

<style scoped>
.tag-selector {
  margin-bottom: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selectable-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.selectable-tag:hover {
  transform: scale(1.05);
}
</style>
