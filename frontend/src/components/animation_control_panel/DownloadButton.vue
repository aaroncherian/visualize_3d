<script setup>
import {storeToRefs} from 'pinia';
import {useAnimationStore} from '@/stores/animationStore.js';
import {useRendererStore} from '@/stores/rendererStore.js';
import {ref, nextTick} from 'vue';

// Access the animation store
const animationStore = useAnimationStore();
const {currentFrameNumber, numFrames} = storeToRefs(animationStore);

// Access the renderer store
const rendererStore = useRendererStore();
const {renderer, scene, camera} = storeToRefs(rendererStore);

// Initialize variables
const isCapturing = ref(false);

let frames = [];

const startCapture = async () => {
  animationStore.setFrameNumber(0);

  animationStore.setIsPlaying(true);
  isCapturing.value = true;
  for (let frame = 1; frame < numFrames.value; frame++) {
    console.log(currentFrameNumber.value);
    animationStore.setFrameNumber(frame);
    // await nextTick();
    renderer.value.render(scene.value, camera.value);
    await captureFrame();

  }

  isCapturing.value = false;
  animationStore.setIsPlaying(false);
}

const captureFrame = (frameNumber) => {
  return new Promise( (resolve) => {
    renderer.value.domElement.toBlob(
        (blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = reader.result.split(',')[1];
            frames.push({
              frameNumber,
              data: base64data,
            });
            resolve();
          };
          reader.readAsDataURL(blob);
        },
        'image/jpeg',
        .8
    )
      }
  )
}
</script>

<template>
  <div class="download-button">
    <button @click="startCapture" :disabled="isCapturing">
      {{ isCapturing ? 'Capturing...' : 'Download' }}
    </button>
  </div>
</template>
