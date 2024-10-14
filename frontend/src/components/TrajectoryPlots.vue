<template>
  <div class="trajectory-plots">
    <Dropdown v-model="selectedJoint" :options="jointOptions" optionLabel="name" placeholder="Select a joint" class="mb-3" />
    <div v-if="selectedJoint" class="grid">
      <div class="col-12">
        <Chart type="line" :data="selectedJointData" :options="chartOptions" class="h-30rem" />
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, computed, watch} from 'vue';
import Chart from 'primevue/chart';
import Dropdown from 'primevue/dropdown';
import {useAnimationStore} from '@/stores/animationStore';
import {storeToRefs} from 'pinia';

const animationStore = useAnimationStore();
const {currentFrameNumber, numFrames} = storeToRefs(animationStore);

const trajectoryData = ref(null);
const selectedJoint = ref(null);

onMounted(async () => {
  await fetchTrajectoryData();
});

const fetchTrajectoryData = async () => {
  try {
    const mediapipeResponse = await fetch('/api/data/mediapipe');
    const mediapipeData = await mediapipeResponse.json();

    let qualisysData = null;
    try {
      const qualisysResponse = await fetch('/api/data/qualisys');
      qualisysData = await qualisysResponse.json();
    } catch (error) {
      console.log('Qualisys data not available');
    }

    trajectoryData.value = {mediapipe: mediapipeData, qualisys: qualisysData};
  } catch (error) {
    console.error('Error fetching trajectory data:', error);
  }
};

const jointOptions = computed(() => {
  if (!trajectoryData.value?.mediapipe?.markers) return [];
  return trajectoryData.value.mediapipe.markers.map(marker => ({name: marker, code: marker}));
});

const processedData = computed(() => {
  if (!trajectoryData.value) return {};

  const {mediapipe, qualisys} = trajectoryData.value;
  const processedData = {};

  for (const jointName of mediapipe.markers) {
    const datasets = [];
    const axes = ['x', 'y', 'z'];
    const colors = ['blue', 'green', 'red'];

    axes.forEach((axis, index) => {
      datasets.push({
        label: `Mediapipe ${axis.toUpperCase()}`,
        data: mediapipe.trajectories[jointName].map(frame => frame[index]),
        borderColor: colors[index],
        tension: 0.4
      });

      if (qualisys && qualisys.trajectories[jointName]) {
        datasets.push({
          label: `Qualisys ${axis.toUpperCase()}`,
          data: qualisys.trajectories[jointName].map(frame => frame[index]),
          borderColor: colors[index],
          borderDash: [5, 5],
          tension: 0.4
        });
      }
    });

    processedData[jointName] = {
      labels: [...Array(mediapipe.trajectories[jointName].length).keys()],
      datasets: datasets
    };
  }

  return processedData;
});

const selectedJointData = computed(() => {
  if (!selectedJoint.value) return null;
  return processedData.value[selectedJoint.value.code];
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    },
    title: {
      display: true,
      text: selectedJoint.value ? `${selectedJoint.value.name} Trajectory` : 'Joint Trajectory'
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Frame'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Position (mm)'
      }
    }
  }
}));

watch(currentFrameNumber, (newFrame) => {
  // This function will be implemented later for dynamic updates
});
</script>

<style scoped>
.trajectory-plots {
  padding: 1rem;
}
</style>