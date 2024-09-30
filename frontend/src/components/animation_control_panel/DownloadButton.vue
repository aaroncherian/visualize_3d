<script setup>
import { storeToRefs } from "pinia";
import { useAnimationStore } from "@/stores/animationStore.js";
import { useRendererStore } from "@/stores/rendererStore.js";
import { nextTick, ref } from "vue";

const animationStore = useAnimationStore();
const { currentFrameNumber, numFrames, fps, isPlaying } = storeToRefs(animationStore);

const rendererStore = useRendererStore();

let capturer = null;
const isCapturing = ref(false);
let captureInterval = null;

const startCapture = async () => {
  if (typeof window.CCapture === 'undefined') {
    console.error('CCapture is not available');
    return;
  }

  capturer = new window.CCapture({
    format: "png",
    framerate: fps.value,
    name: "skeleton_animation",
    quality: 100
  });
  capturer.start();

  animationStore.setFrameNumber(0);
  isCapturing.value = true;

  // Start the animation if it's not already playing
  if (!isPlaying.value) {
    animationStore.setIsPlaying(true);
  }

  captureFrames();
};

const captureFrames = () => {
  captureInterval = setInterval(() => {
    if (currentFrameNumber.value < numFrames.value - 1) {
      capturer.capture(rendererStore.renderer.value.domElement);
      animationStore.setFrameNumber(currentFrameNumber.value + 1);
    } else {
      clearInterval(captureInterval);
      animationStore.setIsPlaying(false);
      isCapturing.value = false;
      capturer.stop();
      capturer.save();
      capturer = null;
    }
  }, 30);
};

</script>

<template>
  <div class='download-button'>
    <button @click="startCapture" :disabled="isCapturing">
      {{ isCapturing ? 'Capturing...' : 'Download' }}
    </button>
  </div>
</template>