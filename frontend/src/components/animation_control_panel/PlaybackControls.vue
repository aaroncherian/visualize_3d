<script setup>
import { storeToRefs } from "pinia";
import { useAnimationStore } from "@/stores/animationStore.js";
import { onUnmounted } from "vue";

const animationStore = useAnimationStore();
const {currentFrameNumber, numFrames, isPlaying, fps} = storeToRefs(animationStore);

let playInterval = null;

const togglePlay = () => {
  console.log('isPlaying:', isPlaying.value);
  if (isPlaying.value) {
    animationStore.setIsPlaying(false);
    clearInterval(playInterval);
  }
  else {
    animationStore.setIsPlaying(true);
    playAnimation();
  }
};

const playAnimation = () => {
  const interval = 1000/fps.value;
  playInterval = setInterval(() => {
    if (currentFrameNumber.value < numFrames.value - 1) {
      animationStore.setFrameNumber(currentFrameNumber.value+1);
    }
    else {
      animationStore.setFrameNumber(0);
    }
      }, interval);
};

onUnmounted(() => {
  if (playInterval) {
    clearInterval(playInterval);
  }
});

</script>

<template>
<div class = "playback-controls">
  <button @click="togglePlay"> {{ isPlaying ? "Pause" : "Play"}} </button>
  <label for="fps-input"> FPS: </label>
  <input id="fps-input" type="number" v-model="fps" min="1" max="300" />
</div>

</template>

<style scoped>
.playback-controls{
  display:flex;
  align-items:center;
}
</style>