<script setup>
import { storeToRefs } from 'pinia';
import { useAnimationStore } from '@/stores/animationStore.js';
import { useRendererStore } from '@/stores/rendererStore.js';
import { ref } from 'vue';

const animationStore = useAnimationStore();
const { currentFrameNumber, numFrames } = storeToRefs(animationStore);

const rendererStore = useRendererStore();
const { renderer, scene, camera } = storeToRefs(rendererStore);

const isCapturing = ref(false);
const captureProgress = ref(0);

let frames = [];

const BATCH_SIZE = 500; // Adjust this value based on your needs

const startCapture = async () => {
  animationStore.setFrameNumber(0);
  animationStore.setIsPlaying(true);
  isCapturing.value = true;
  frames = [];

  for (let frame = 0; frame < numFrames.value; frame++) {
    animationStore.setFrameNumber(frame);
    renderer.value.render(scene.value, camera.value);
    await captureFrame(frame);
    captureProgress.value = (frame + 1) / numFrames.value * 100;
  }

  isCapturing.value = false;
  animationStore.setIsPlaying(false);

  await uploadFramesInBatches(frames);
  frames = [];
}

const captureFrame = (frameNumber) => {
  return new Promise((resolve) => {
    const canvas = renderer.value.domElement;
    canvas.toBlob((blob) => {
      frames.push({
        frameNumber,
        data: blob,
      });
      console.log(`Captured frame: ${frameNumber}`);
      resolve();
    }, 'image/png');
  }); 
}

const uploadFramesInBatches = async (frames) => {
  const totalBatches = Math.ceil(frames.length / BATCH_SIZE);
  for (let i = 0; i < totalBatches; i++) {
    const batchFrames = frames.slice(i * BATCH_SIZE, (i + 1) * BATCH_SIZE);
    await uploadBatch(batchFrames, i);
  }
}

const uploadBatch = async (batchFrames, batchIndex) => {
  try {
    const formData = new FormData();
    batchFrames.forEach((frame) => {
      formData.append('files', frame.data, `frame_${frame.frameNumber}.png`);
    });
    formData.append('width', renderer.value.domElement.width);
    formData.append('height', renderer.value.domElement.height);
    formData.append('batchIndex', batchIndex);
    formData.append('totalFrames', frames.length);

    const response = await fetch('/api/upload-frames', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload frames');
    }

    const result = await response.json();
    console.log(`Batch ${batchIndex} upload successful:`, result);

  } catch (error) {
    console.error(`Error uploading batch ${batchIndex}:`, error);
    throw error;
  }
};
</script>

<template>
  <div class="download-button">
    <button @click="startCapture" :disabled="isCapturing">
      {{ isCapturing ? 'Capturing...' : 'Download' }}
    </button>
  </div>
</template>