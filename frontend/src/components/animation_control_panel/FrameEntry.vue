<script setup>
import { useAnimationStore } from '@/stores/animationStore';
import { storeToRefs } from 'pinia';

const animationStore = useAnimationStore();
const { currentFrameNumber } = storeToRefs(animationStore);

</script>

<template>
<div class = 'frame-counter-container'>
  <label id = 'frame-label'> Frame: </label>
  <span class = 'frame-counter'> {{ currentFrameNumber }}</span>
</div>
</template>

<style scoped>
#frame-label {
  color:black;
}

.frame-counter {
  text-align: center;
  font-weight: bold;
  color: black;
}
</style>