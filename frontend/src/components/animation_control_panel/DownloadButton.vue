<script setup>
import {storeToRefs} from 'pinia';
import {useAnimationStore} from '@/stores/animationStore.js';
import {useRendererStore} from '@/stores/rendererStore.js';
import {ref} from 'vue';

// Access the animation store
const animationStore = useAnimationStore();
const {currentFrameNumber, numFrames} = storeToRefs(animationStore);

// Access the renderer store
const rendererStore = useRendererStore();
const {renderer, scene, camera} = storeToRefs(rendererStore);

// Initialize variables
let capturer = null;
const isCapturing = ref(false);
let captureInterval = null;

// Define the animate function
const animate = () => {
  if (currentFrameNumber.value >= numFrames.value - 1) {
    // Stop capturing when all frames are processed
    clearInterval(captureInterval);
    capturer.stop();
    capturer.save();
    isCapturing.value = false;
    return;
  }

  // Update the frame number
  animationStore.setFrameNumber(currentFrameNumber.value + 1);

  // Ensure the renderer, scene, and camera are initialized
  if (!renderer.value || !scene.value || !camera.value) {
    console.error('Renderer, scene, or camera is not initialized');
    return;
  }

  // Render the scene
  renderer.value.render(scene.value, camera.value);

  // Capture the frame
  capturer.capture(renderer.value.domElement);
};

// Define the startCapture function
const startCapture = () => {
  if (typeof window.CCapture === 'undefined') {
    console.error('CCapture is not available');
    return;
  }

  isCapturing.value = true;

  capturer = new window.CCapture({
    format: 'png',
    framerate: 30,
    name: 'skeleton_animation',
    quality: 100,
    verbose: true,
    useRaf: false, // Ensure CCapture doesn't override requestAnimationFrame
  });

  capturer.start();

  // Reset the frame number
  animationStore.setFrameNumber(0);

  // Start the animation loop using setInterval
  captureInterval = setInterval(animate, 1000 / 30); // 30 FPS
};
</script>

<template>
  <div class="download-button">
    <button @click="startCapture" :disabled="isCapturing">
      {{ isCapturing ? 'Capturing...' : 'Download' }}
    </button>
  </div>
</template>
