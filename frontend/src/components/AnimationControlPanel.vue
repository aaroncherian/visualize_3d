<template>
  <div class="animation-control-panel">
    <Slider />
    <FrameEntry />
  </div>
</template>

<script setup>
import Slider from '@/components/animation_control_panel/Slider.vue';  // Adjust path
import FrameEntry from '@/components/animation_control_panel/FrameEntry.vue';  // Adjust path

// The Pinia store is used in both child components, so no need to import here
</script>

<style scoped>
.animation-control-panel {
  display: flex;
  flex-direction: row; /* Align components horizontally */
  justify-content: space-between; /* Distribute space between components */
  align-items: center; /* Vertically align components */
  gap: 1rem; /* Adds spacing between components */
  padding: 1rem; /* Padding for breathing space */
  border: 1px solid #fbf5f1; /* Optional border for styling */
  border-radius: 4px;
  background-color: #fffefe;
}
</style>
