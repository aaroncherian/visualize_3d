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
const windowSize = 100; // Total number of frames to show (4 before, 1 current, 4 after)

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
  const currentFrame = currentFrameNumber.value;
  const totalFrames = mediapipe.trajectories[jointName].length;

  const halfWindow = Math.floor(windowSize / 2);
  const startFrame = Math.max(0, currentFrame - halfWindow);
  const endFrame = Math.min(totalFrames - 1, startFrame + windowSize - 1);

  // Adjust startFrame if we're near the end of the data
  const adjustedStartFrame = Math.max(0, endFrame - windowSize + 1);

  const labels = [...Array(endFrame - adjustedStartFrame + 1).keys()].map(i => i + adjustedStartFrame);

  return ['x', 'y', 'z'].reduce((acc, axis, index) => {
    const mediapipeData = mediapipe.trajectories[jointName].slice(adjustedStartFrame, endFrame + 1).map(frame => frame[index]);
    const qualisysData = qualisys && qualisys.trajectories[jointName]
        ? qualisys.trajectories[jointName].slice(adjustedStartFrame, endFrame + 1).map(frame => frame[index])
        : [];

    // Calculate min and max for y-axis using the full dataset
    const allMediapipeData = mediapipe.trajectories[jointName].map(frame => frame[index]);
    const allQualisysData = qualisys && qualisys.trajectories[jointName]
        ? qualisys.trajectories[jointName].map(frame => frame[index])
        : [];
    const allData = [...allMediapipeData, ...allQualisysData];
    const minY = Math.min(...allData);
    const maxY = Math.max(...allData);
    const yPadding = (maxY - minY) * 0.1; // 10% padding

    const freemocapColor = '#1E88E5'; // Blue
    const qualisysColor = '#f54242'; // Orange

    acc[axis] = {
      labels,
      datasets: [
        {
          label: 'FreeMoCap',
          data: mediapipeData,
          borderColor: freemocapColor,
          backgroundColor: freemocapColor,
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4,
          order: 4 // Lowest order, drawn first
        },
        ...(qualisys && qualisys.trajectories[jointName] ? [{
          label: 'Qualisys',
          data: qualisysData,
          borderColor: qualisysColor,
          backgroundColor: qualisysColor,
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4,
          order: 3
        }] : []),
        {
          label: 'Current Frame',
          data: [
            {x: currentFrame, y: minY - yPadding},
            {x: currentFrame, y: maxY + yPadding}
          ],
          borderColor: 'black',
          borderWidth: 2,
          pointRadius: 0,
          order: 2
        },
        {
          label: 'Freemocap Current Frame',
          data: labels.map(frame => frame === currentFrame ? mediapipe.trajectories[jointName][frame][index] : null),
          borderColor: freemocapColor,
          backgroundColor: freemocapColor,
          borderWidth: 0,
          pointRadius: 6,
          pointHoverRadius: 8,
          order: 1
        },
        ...(qualisys && qualisys.trajectories[jointName] ? [{
          label: 'Qualisys Current Frame',
          data: labels.map(frame => frame === currentFrame ? qualisys.trajectories[jointName][frame][index] : null),
          borderColor: qualisysColor,
          backgroundColor: qualisysColor,
          borderWidth: 0,
          pointRadius: 6,
          pointHoverRadius: 8,
          order: 0 // Highest order, drawn last
        }] : [])
      ],
      yAxisMin: minY - yPadding,
      yAxisMax: maxY + yPadding
    };
    return acc;
  }, {});
});

const getChartOptions = (axis) => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false, // Disable animations for better performance
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
      type: 'linear',
      title: {
        display: true,
        text: 'Frame'
      },
      ticks: {
        maxTicksLimit: 10,
        stepSize: 1,
        precision: 0
      },
      min: axisChartData.value[axis].labels[0],
      max: axisChartData.value[axis].labels[axisChartData.value[axis].labels.length - 1]
    },
    y: {
      title: {
        display: true,
        text: 'Position (mm)'
      },
      min: axisChartData.value[axis].yAxisMin,
      max: axisChartData.value[axis].yAxisMax
    }
  }
});

watch(currentFrameNumber, () => {
  // This will trigger a re-computation of axisChartData
});

watch(selectedJoint, () => {
  // This will trigger a re-computation of axisChartData
});
</script>

<style scoped>
.trajectory-plots {
  padding: 1rem;
  width: 100%;
}
</style>