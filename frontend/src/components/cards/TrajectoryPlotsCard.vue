<template>
  <div class="card trajectory-plots-card">
    <h3>Joint Trajectories</h3>
    <TrajectoryPlots />
  </div>
</template>

<script setup>
import TrajectoryPlots from '@/components/TrajectoryPlots.vue';
</script>

<style scoped>
.trajectory-plots-card {
  background-color: var(--surface-card);
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 2px 1px -1px rgba(0,0,0,.2), 0 1px 1px 0 rgba(0,0,0,.14), 0 1px 3px 0 rgba(0,0,0,.12);
  height: 100%;
  width: 100%;
  overflow: auto;
}

h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: black;
}
</style>