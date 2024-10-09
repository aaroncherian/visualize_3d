<template>
  <div id="app" class="grid-container">
    <div class="grid-item threejs-item">
      <PrimeVueThreeJS />
    </div>
    <div class="grid-item slider-item">
      <AnimationControlPanel />
    </div>
    <div class="grid-item video-item">
      <VideoPlayerCard />
    </div>
  </div>
</template>

<script setup>
import PrimeVueThreeJS from '@/components/cards/ThreeJSCard.vue';
import AnimationControlPanel from '@/components/cards/AnimationControlsCard.vue';
import VideoPlayerCard from '@/components/cards/VideoPlayerCard.vue';
</script>

<style>
@import 'primeflex/primeflex.css';

body {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
  width: 100%;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(12, 1fr);
  gap: 10px;
  height: 100vh;
  padding: 20px;
}

.grid-item {
  display: flex;
  justify-content: center;
  align-items: center;
}

.threejs-item {
  grid-column: 2 / span 6;
  grid-row: 2 / span 6;
}

.slider-item {
  grid-column: 2 / span 6;
  grid-row: 9 / span 2;
}

.video-item {
  grid-column: 9 / span 3;
  grid-row: 2 / span 10;
}
</style>