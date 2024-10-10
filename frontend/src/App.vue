<template>
  <div id="app">
    <div class="grid-container">
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
    <Button icon="pi pi-bars" @click="toggleSidebar" class="sidebar-toggle p-button-rounded" />
    <Sidebar v-model:visible="sidebarVisible" position="right" :baseZIndex="1000" class="p-sidebar-sm">
      <h2>Sidebar Content</h2>
      <p>Add your sidebar content here.</p>
    </Sidebar>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import PrimeVueThreeJS from '@/components/cards/ThreeJSCard.vue';
import AnimationControlPanel from '@/components/cards/AnimationControlsCard.vue';
import VideoPlayerCard from '@/components/cards/VideoPlayerCard.vue';
import Button from 'primevue/button';
import Sidebar from 'primevue/sidebar';

const sidebarVisible = ref(false);

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};
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

.sidebar-toggle {
  background-color: #2e80da; /* Replace with your desired color */
  color: #ffffff; /* Text/icon color */
}

.sidebar-toggle:hover {
  background-color: #0056b3; /* Darker shade for hover state */
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

.sidebar-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1001;
}
</style>