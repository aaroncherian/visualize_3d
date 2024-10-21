<template>
  <div class="com-bos-plot">
    <h3>Center of Mass vs Base of Support</h3>
    <div class="chart-container">
      <Chart
          ref="chartRef"
          type="scatter"
          :data="chartData"
          :options="chartOptions"
          class="full-size-chart"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Chart from 'primevue/chart';
import { useAnimationStore } from '@/stores/animationStore';
import { storeToRefs } from 'pinia';

const animationStore = useAnimationStore();
const { currentFrameNumber, numFrames } = storeToRefs(animationStore);

const comData = ref(null);
const bodyData = ref(null);
const chartRef = ref(null);

const fetchData = async () => {
  try {
    const [comResponse, bodyResponse] = await Promise.all([
      fetch('/api/data_extra/com'),
      fetch('/api/data/mediapipe')
    ]);
    const comJson = await comResponse.json();
    const bodyJson = await bodyResponse.json();
    comData.value = comJson.com_data;
    bodyData.value = bodyJson;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

onMounted(fetchData);

const calculateAxisRanges = computed(() => {
  if (!comData.value || !bodyData.value) return { xMin: 0, xMax: 1, yMin: 0, yMax: 1 };

  const allX = [...comData.value.map(p => p[0]), ...Object.values(bodyData.value.trajectories).flatMap(t => t.map(p => p[0]))];
  const allY = [...comData.value.map(p => p[1]), ...Object.values(bodyData.value.trajectories).flatMap(t => t.map(p => p[1]))];

  const xMin = Math.min(...allX);
  const xMax = Math.max(...allX);
  const yMin = Math.min(...allY);
  const yMax = Math.max(...allY);

  const xPadding = (xMax - xMin) * 0.1;
  const yPadding = (yMax - yMin) * 0.1;

  return {
    xMin: xMin - xPadding,
    xMax: xMax + xPadding,
    yMin: yMin - yPadding,
    yMax: yMax + yPadding
  };
});

const chartData = computed(() => {
  if (!comData.value || !bodyData.value) return { datasets: [] };

  const frame = currentFrameNumber.value;
  const trailLength = 20;

  const datasets = [
    // Left foot (current frame)
    {
      label: 'Left Foot',
      data: [
        { x: bodyData.value.trajectories.left_heel[frame][0], y: bodyData.value.trajectories.left_heel[frame][1] },
        { x: bodyData.value.trajectories.left_foot_index[frame][0], y: bodyData.value.trajectories.left_foot_index[frame][1] }
      ],
      borderColor: 'black',
      backgroundColor: 'blue',
      pointStyle: 'circle',
      pointRadius: 7,
      pointBorderWidth: 2,
      showLine: true,
      borderWidth: 2,
      borderDash: [5, 5]
    },
    // Right foot (current frame)
    {
      label: 'Right Foot',
      data: [
        { x: bodyData.value.trajectories.right_heel[frame][0], y: bodyData.value.trajectories.right_heel[frame][1] },
        { x: bodyData.value.trajectories.right_foot_index[frame][0], y: bodyData.value.trajectories.right_foot_index[frame][1] }
      ],
      borderColor: 'black',
      backgroundColor: 'red',
      pointStyle: 'circle',
      pointRadius: 7,
      pointBorderWidth: 2,
      showLine: true,
      borderWidth: 2,
      borderDash: [5, 5]
    },
    // Center of Mass (current frame)
    {
      label: 'Center of Mass',
      data: [{ x: comData.value[frame][0], y: comData.value[frame][1] }],
      borderColor: 'darkorange',
      backgroundColor: 'orange',
      pointStyle: 'star',
      pointRadius: 12,
      pointBorderWidth: 2,
      showLine: false
    }
  ];

  // Add trails
  ['Left Foot', 'Right Foot', 'Center of Mass'].forEach((label, index) => {
    for (let i = 1; i <= trailLength; i++) {
      const trailFrame = Math.max(0, frame - i);
      const opacity = 1 - (i / trailLength);
      let trailData;

      if (label.includes('Foot')) {
        const side = label.split(' ')[0].toLowerCase();
        trailData = [
          { x: bodyData.value.trajectories[`${side}_heel`][trailFrame][0], y: bodyData.value.trajectories[`${side}_heel`][trailFrame][1] },
          { x: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][0], y: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][1] }
        ];
      } else {
        trailData = [{ x: comData.value[trailFrame][0], y: comData.value[trailFrame][1] }];
      }

      datasets.push({
        data: trailData,
        borderColor: `rgba(${label.includes('Left') ? '0,0,255' : label.includes('Right') ? '255,0,0' : '255,165,0'},${opacity})`,
        backgroundColor: `rgba(${label.includes('Left') ? '0,0,255' : label.includes('Right') ? '255,0,0' : '255,165,0'},${opacity})`,
        pointStyle: 'circle',
        pointRadius: label.includes('Foot') ? 3 : 5,
        showLine: label.includes('Foot'),
        borderDash: label.includes('Foot') ? [5, 5] : undefined,
        borderWidth: 1
      });
    }
  });

  return { datasets };
});

const chartOptions = computed(() => ({
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      title: { display: true, text: 'X Position (m)' },
      min: calculateAxisRanges.value.xMax,  // Swap min and max
      max: calculateAxisRanges.value.xMin,  // Swap min and max
      reverse: true,  // Add this line to reverse the axis
    },
    y: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: 'Y Position (m)' },
      min: calculateAxisRanges.value.yMin,
      max: calculateAxisRanges.value.yMax,
    }
  },
  aspectRatio: 1,
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false }
  }
}));

watch(currentFrameNumber, () => {
  if (chartRef.value && chartRef.value.chart) {
    chartRef.value.chart.data = chartData.value;
    chartRef.value.chart.update('none'); // Update without animation
  }
});

watch([comData, bodyData], () => {
  if (comData.value && bodyData.value && chartRef.value && chartRef.value.chart) {
    chartRef.value.chart.data = chartData.value;
    chartRef.value.chart.options = chartOptions.value;
    chartRef.value.chart.update('none');
  }
}, { immediate: true });
</script>

<style scoped>
.com-bos-plot {
  padding: 1rem;
  width: 100%;
}

.chart-container {
  width: 800px;
  height: 800px;
  margin: 0 auto;
}

.full-size-chart {
  width: 100% !important;
  height: 100% !important;
}
</style>