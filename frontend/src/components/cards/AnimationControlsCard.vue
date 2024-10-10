<template>
  <div class="card animation-control-panel">
    <div class="frame-row">
      <FrameEntry />
    </div>
    <div class="slider-row">
      <Slider />
    </div>
    <div class="bottom-row">
      <PlaybackControls />
      <DownloadButton />
    </div>
  </div>
</template>

<script setup>
import Slider from '../animation_control_panel/Slider.vue';
import FrameEntry from '../animation_control_panel/FrameEntry.vue';
import PlaybackControls from "../animation_control_panel/PlaybackControls.vue";
import DownloadButton from '../animation_control_panel/DownloadButton.vue';
import { useAnimationStore } from '@/stores/animationStore';
import { storeToRefs } from 'pinia';

const animationStore = useAnimationStore();
const { fps } = storeToRefs(animationStore);
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 1rem;
  border-radius: 15px;
  background-color: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.frame-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

.slider-row {
  width: 100%;
  margin-bottom: 1rem;
}

.bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}



</style>