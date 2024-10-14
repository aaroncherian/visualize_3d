<template>
  <div class="trajectory-plots">
    <Dropdown v-model="selectedJoint" :options="jointOptions" optionLabel="name" placeholder="Select a joint" class="mb-3 w-full" />
    <div v-if="selectedJoint" class="grid">
      <div v-for="(chartData, axis) in axisChartData" :key="axis" class="col-12 md:col-4 mb-3">
        <Chart type="line" :data="chartData" :options="getChartOptions(axis)" class="h-20rem" />
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

const axisChartData = computed(() => {
  if (!selectedJoint.value || !trajectoryData.value) return {};

  const {mediapipe, qualisys} = trajectoryData.value;
  const jointName = selectedJoint.value.code;
  const labels = [...Array(mediapipe.trajectories[jointName].length).keys()];

  return ['x', 'y', 'z'].reduce((acc, axis, index) => {
    acc[axis] = {
      labels,
      datasets: [
        {
          label: 'Mediapipe',
          data: mediapipe.trajectories[jointName].map(frame => frame[index]),
          borderColor: '#1E88E5',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        },
        ...(qualisys && qualisys.trajectories[jointName] ? [{
          label: 'Qualisys',
          data: qualisys.trajectories[jointName].map(frame => frame[index]),
          borderColor: '#FFA726',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0.4
        }] : [])
      ]
    };
    return acc;
  }, {});
});

const getChartOptions = (axis) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top'
    },
    title: {
      display: true,
      text: `${selectedJoint.value.name} - ${axis.toUpperCase()} Trajectory`
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Frame'
      },
      ticks: {
        maxTicksLimit: 10
      }
    },
    y: {
      title: {
        display: true,
        text: 'Position (mm)'
      }
    }
  }
});

watch(currentFrameNumber, (newFrame) => {
  // This function will be implemented later for dynamic updates
});
</script>

<style scoped>
.trajectory-plots {
  padding: 1rem;
  width: 100%;
}
</style>