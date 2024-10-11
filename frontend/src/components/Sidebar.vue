<template>
  <div>
    <Button icon="pi pi-bars" @click="toggleSidebar" class="sidebar-toggle p-button-rounded" />
    <Sidebar v-model:visible="visible" position="right" :baseZIndex="1000" class="p-sidebar-sm">
      <Button @click="triggerFetch('qualisys')" label="Add Qualisys Data" />
    </Sidebar>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from 'primevue/button';
import Sidebar from 'primevue/sidebar';
import { useSkeletonStore } from '@/stores/skeletonStore';

// State to control visibility of the sidebar
const visible = ref(false);

// Skeleton store instance
const skeletonStore = useSkeletonStore();

// Function to toggle the sidebar visibility
const toggleSidebar = () => {
  visible.value = !visible.value;
};

// Function to trigger fetching data from a specified source
const triggerFetch = (trackerToFetch) => {
  skeletonStore.triggerDataFetch(trackerToFetch); // This will dynamically fetch the provided source
};


</script>

<style scoped>
.sidebar-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1001;
  background-color: #2e80da;
  color: #ffffff;
}

.sidebar-toggle:hover {
  background-color: #0056b3;
}
</style>
