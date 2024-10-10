<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAnimationStore } from "@/stores/animationStore.js";
import { storeToRefs } from "pinia";

const animationStore = useAnimationStore();
const { currentFrameNumber } = storeToRefs(animationStore);

const videos = ref([]);
const currentFrameURLs = ref({});

const fetchVideoInfo = async () => {
  try {
    const response = await fetch('/api/video-info');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    videos.value = data.videos;
  } catch (error) {
    console.error('Error fetching video info:', error);
  }
};

const fetchFrames = async (frameNumber) => {
  try {
    const response = await fetch(`/api/video/frames/${frameNumber}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const frames = await response.json();

    Object.entries(frames).forEach(([videoId, base64Data]) => {
      // Convert base64 to binary
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const blob = new Blob([bytes], { type: 'image/webp' });
      if (currentFrameURLs.value[videoId]) {
        URL.revokeObjectURL(currentFrameURLs.value[videoId]);
      }
      currentFrameURLs.value[videoId] = URL.createObjectURL(blob);
    });
  } catch (error) {
    console.error('Error fetching frames:', error);
  }
};

onMounted(async () => {
  await fetchVideoInfo();
  fetchFrames(animationStore.currentFrameNumber);
});

watch(() => animationStore.currentFrameNumber, (newFrame) => {
  fetchFrames(newFrame);
});
</script>

<template>
  <div class="video-grid">
    <template v-for="(video, index) in videos" :key="index">
      <div class="video-frame-viewer">
        <img :src="currentFrameURLs[index]" alt="Video Frame" />
      </div>
      <!-- Add a line break after every second video -->
      <br v-if="(index + 1) % 2 === 0">
    </template>
  </div>
</template>

<style scoped>
.video-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 10px; /* Adjust this value to control spacing between videos */
}

.video-frame-viewer {
  width: calc(50% - 5px); /* Adjust width to account for gap */
  margin-bottom: 10px;
  text-align: center;
}

.video-frame-viewer img {
  max-width: 100%;
  height: auto;
}

/* Remove the <br> elements */
br {
  display: none;
}
</style>