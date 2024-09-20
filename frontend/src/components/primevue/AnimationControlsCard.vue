<template>
  <div class="card animation-control-panel">
    <div class="controls mt-3" style="flex-grow: 1;">
      <Slider />
      <FrameEntry />
    </div>
  </div>
</template>

<script setup>
import Slider from '../animation_control_panel/Slider.vue';
import FrameEntry from '../animation_control_panel/FrameEntry.vue';

</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure the card takes full height */
  width: 100%; /* Ensure the card takes full width */
  padding: 1rem;
  border-radius: 15px;
  background-color: #ffffff;
  justify-content: center; /* Center content vertically */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1)
}

.animation-control-panel {
  display: flex;
  flex-direction: row; /* Align slider and frame entry horizontally */
  justify-content: space-between; /* Space out the controls */
  align-items: center;
  gap: 1rem;
}

.controls {
  display: flex;
  flex-grow: 1;
  align-items: center;
  gap: 1rem;
}
</style>
