<template>
  <div class="trajectory-plots">
    <Dropdown
        v-model="selectedJoint"
        :options="jointOptions"
        placeholder="Select a joint"
        class="mb-3 w-full"
    />
    <div v-if="selectedJoint" class="grid">
      <div
          v-for="(chartData, axis) in axisChartData"
          :key="axis"
          class="col-12 md:col-4 mb-3"
      >
        <Chart
            type="line"
            :data="chartData"
            :options="getChartOptions(axis)"
            class="h-20rem"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'primevue/chart';
import Dropdown from 'primevue/dropdown';
import { useAnimationStore } from '@/stores/animationStore';
import { storeToRefs } from 'pinia';

const animationStore = useAnimationStore();
const { currentFrameNumber } = storeToRefs(animationStore);

const trajectoryData = ref(null);
const selectedJoint = ref(null);
const windowSize = 100;

onMounted(async () => {
  await fetchTrajectoryData();
});

const fetchTrajectoryData = async () => {
  try {
    const mediapipeResponse = await fetch('/api/data/mediapipe');
    const mediapipeData = await mediapipeResponse.json();
    trajectoryData.value = { mediapipe: mediapipeData };
  } catch (error) {
    console.error('Error fetching mediapipe trajectory data:', error);
  }
};

const jointOptions = computed(() => {
  if (!trajectoryData.value?.mediapipe?.markers) return [];
  return trajectoryData.value.mediapipe.markers;
});

const axisChartData = computed(() => {
  if (!selectedJoint.value || !trajectoryData.value) return {};

  const { mediapipe } = trajectoryData.value;
  const jointName = selectedJoint.value;
  const currentFrame = currentFrameNumber.value;
  const totalFrames = mediapipe.trajectories[jointName].length;

  const halfWindow = Math.floor(windowSize / 2);
  const startFrame = Math.max(0, currentFrame - halfWindow);
  const endFrame = Math.min(totalFrames - 1, startFrame + windowSize - 1);
  const adjustedStartFrame = Math.max(0, endFrame - windowSize + 1);

  const labels = [...Array(endFrame - adjustedStartFrame + 1).keys()].map(
      i => i + adjustedStartFrame
  );

  return ['x', 'y', 'z'].reduce((acc, axis, index) => {
    const jointFrames = mediapipe.trajectories[jointName];

    const mediapipeData = jointFrames
        .slice(adjustedStartFrame, endFrame + 1)
        .map(frame => frame[index]);

    const allData = jointFrames.map(frame => frame[index]);
    const safeData = allData.length > 0 ? allData : [0];
    const minY = Math.min(...safeData);
    const maxY = Math.max(...safeData);
    const yPadding = (maxY - minY) * 0.1;

    const freemocapColor = '#1E88E5';

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
          order: 2
        },
        {
          label: 'Current Frame Line',
          data: [
            { x: currentFrame, y: minY - yPadding },
            { x: currentFrame, y: maxY + yPadding }
          ],
          borderColor: 'black',
          borderWidth: 2,
          pointRadius: 0,
          order: 1
        },
        {
          label: 'Current Frame Dot',
          data: labels.map(frame =>
              frame === currentFrame
                  ? jointFrames[frame][index]
                  : null
          ),
          borderColor: freemocapColor,
          backgroundColor: freemocapColor,
          borderWidth: 0,
          pointRadius: 6,
          pointHoverRadius: 8,
          order: 0,
          showLine: false
        }
      ],
      yAxisMin: minY - yPadding,
      yAxisMax: maxY + yPadding
    };

    return acc;
  }, {});
});

const getChartOptions = axis => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        filter: item => !item.text.includes('Current Frame'),
        font: { size: 14 }
      }
    },
    title: {
      display: true,
      text: `${selectedJoint.value} - ${axis.toUpperCase()} Trajectory`,
      font: {
        size: 18,
        weight: 'bold'
      }
    }
  },
  scales: {
    x: {
      type: 'linear',
      title: {
        display: true,
        text: 'Frame',
        font: { size: 16, weight: 'bold' }
      },
      ticks: {
        maxTicksLimit: 10,
        stepSize: 1,
        precision: 0,
        font: { size: 12 }
      },
      min: axisChartData.value[axis].labels[0],
      max:
          axisChartData.value[axis].labels[
          axisChartData.value[axis].labels.length - 1
              ]
    },
    y: {
      title: {
        display: true,
        text: 'Position (mm)',
        font: { size: 16, weight: 'bold' }
      },
      ticks: {
        font: { size: 12 }
      },
      min: axisChartData.value[axis].yAxisMin,
      max: axisChartData.value[axis].yAxisMax
    }
  }
});

watch(currentFrameNumber, () => {
  // Triggers re-computation
});

watch(selectedJoint, () => {
  // Triggers re-computation
});
</script>

<style scoped>
.trajectory-plots {
  padding: 1rem;
  width: 100%;
}
</style>
