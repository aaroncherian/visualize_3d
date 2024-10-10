<template>
  <div class="card video-player-card">
    <div class="mt-3" style="flex-grow: 1;">
      <VideoPlayer />
    </div>
  </div>
</template>

<script setup>
import VideoPlayer from '@/components/VideoPlayer.vue';
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
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.video-player-card {
  overflow: hidden; /* Prevent content from expanding the card */
}
</style>