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
  </div>
</template>

<script setup>
import Slider from 'primevue/slider';
import { useAnimationStore } from '@/stores/animationStore';
import { storeToRefs } from 'pinia';


const animationStore = useAnimationStore();
const { currentFrameNumber } = storeToRefs(animationStore);

</script>

<style scoped>
.slider-container {
  flex: 1;
  padding: 1rem;

}

:deep(.p-slider-handle) {
  transform: translateY(-50%);
}

</style>
