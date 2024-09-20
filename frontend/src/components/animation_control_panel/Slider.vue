<template>
  <div class="slider-container">
    <Slider
        id="frame-slider"
        ref="frameSlider"
        v-model="currentFrameNumber"
        :min="0"
        :max="100"
        class="w-full"
    />
    <label for="frame-slider">Frame:</label>
    <span class="slider-value">{{ currentFrameNumber }}</span>
  </div>
</template>

<script setup>
import Slider from 'primevue/slider';
import { ref } from 'vue';
const currentFrameNumber = ref(0);
</script>

<style scoped>
.slider-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

:deep(.p-slider-handle) {
  transform: translateY(-50%);
}

.slider-value {
  text-align: center;
  font-weight: bold;
  color: black;
}
</style>
