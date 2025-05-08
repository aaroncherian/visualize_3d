<template>
  <div id="app">
    <div class="grid-container">
      <div class="grid-item threejs-item">
        <PrimeVueThreeJS />
      </div>
      <div class="grid-item trajectory-item">
        <TrajectoryPlotsCard />
      </div>
<!--      <div class="grid-item trajectory-item">-->
<!--       <COM_BOSCard />-->
<!--      </div>-->
      <div class="grid-item video-item">
        <VideoPlayerCard />
      </div>
      <div class="grid-item slider-item">
        <AnimationControlPanel />
      </div>
    </div>
    <Sidebar />
  </div>
</template>

<script setup>
import PrimeVueThreeJS from '@/components/cards/ThreeJSCard.vue';
import AnimationControlPanel from '@/components/cards/AnimationControlsCard.vue';
import VideoPlayerCard from '@/components/cards/VideoPlayerCard.vue';
import Sidebar from '@/components/Sidebar.vue';
import TrajectoryPlotsCard from "@/components/cards/TrajectoryPlotsCard.vue";
import COM_BOSCard from "@/components/cards/COM_BOSCard.vue";
</script>

<style>
@import 'primevue/resources/themes/saga-blue/theme.css';
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
  width: 100vw; /* Ensure full width */
  padding: 20px;
  box-sizing: border-box;
}

.grid-item {
  display: flex;
  justify-content: center;
  align-items: stretch;
  width: 100%; /* Ensure full width */
}

.threejs-item {
  grid-column: 1 / span 8;
  grid-row: 1 / span 6;
}

.trajectory-item {
  grid-column: 1 / span 8;
  grid-row: 7 / span 5;
}

.video-item {
  grid-column: 9 / span 4;
  grid-row: 1 / span 11;
}

.slider-item {
  grid-column: 1 / span 12;
  grid-row: 12 / span 1;
}
</style>