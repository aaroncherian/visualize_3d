<script setup>
import {watch, onMounted, ref} from 'vue';
import {useAnimationStore} from "@/stores/animationStore.js";
import {storeToRefs} from "pinia";

const animationStore = useAnimationStore();
const currentFrameNumber = storeToRefs(animationStore);
const currentFrameURL = ref('');
const fetchFrame = async (frameNumber) => {
  try {
    const response = await fetch(`/api/video/frame/${frameNumber}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const blob = await response.blob();
    if (currentFrameURL.value) {
      URL.revokeObjectURL(currentFrameURL.value);
    }
    currentFrameURL.value = URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error fetching frame:', error);
  }
};

const updateFrame = (frameNumber) => {
  fetchFrame(frameNumber);
}

onMounted(() => {
  updateFrame(animationStore.currentFrameNumber);
});


watch(() => animationStore.currentFrameNumber, (newFrame) => {
  updateFrame(animationStore.currentFrameNumber);
});

</script>

<template>
<div class = 'video-frame-viewer'>
  <img :src="currentFrameURL" alt = 'Video Frame'/>
</div>
</template>

<style scoped>
.video-frame-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>