<template>
  <div class="com-bos-plot">
    <h3 id = 'plot_title'>Center of Mass vs Base of Support</h3>
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

const chartData = computed(() => {
  if (!comData.value || !bodyData.value) return { datasets: [] };

  const frame = currentFrameNumber.value;
  const trailLength = 20; // Length of the trail for both feet and COM

  // Create the foot datasets first
  const datasets = [
    // Left foot (current frame)
    {
      label: 'Left Foot',
      data: [
        { x: bodyData.value.trajectories.left_heel[frame][0], y: bodyData.value.trajectories.left_heel[frame][1] * -1 },
        { x: bodyData.value.trajectories.left_foot_index[frame][0], y: bodyData.value.trajectories.left_foot_index[frame][1] * -1 }
      ],
      borderColor: 'black',
      backgroundColor: 'blue',
      pointStyle: 'circle',
      pointRadius: 7,
      pointBorderWidth: 2,
      showLine: true,
      borderWidth: 2,
      borderDash: [5, 5],
      order: 1,
    },
    // Right foot (current frame)
    {
      label: 'Right Foot',
      data: [
        { x: bodyData.value.trajectories.right_heel[frame][0], y: bodyData.value.trajectories.right_heel[frame][1] * -1 },
        { x: bodyData.value.trajectories.right_foot_index[frame][0], y: bodyData.value.trajectories.right_foot_index[frame][1] * -1 }
      ],
      borderColor: 'black',
      backgroundColor: 'red',
      pointStyle: 'circle',
      pointRadius: 7,
      pointBorderWidth: 2,
      showLine: true,
      borderWidth: 2,
      borderDash: [5, 5],
      order: 2,
    },
  ];

  // Add foot trails
  ['Left Foot', 'Right Foot'].forEach((label, index) => {
    for (let i = 1; i <= trailLength; i++) {
      const trailFrame = Math.max(0, frame - i);
      const opacity = 1 - (i / trailLength);
      let trailData;

      const side = label.split(' ')[0].toLowerCase();  // "left" or "right"
      trailData = [
        { x: bodyData.value.trajectories[`${side}_heel`][trailFrame][0], y: bodyData.value.trajectories[`${side}_heel`][trailFrame][1] * -1 },
        { x: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][0], y: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][1] * -1 }
      ];

      datasets.push({
        data: trailData,
        borderColor: `rgba(${label.includes('Left') ? '0,0,255' : '255,0,0'},${opacity})`,
        backgroundColor: `rgba(${label.includes('Left') ? '0,0,255' : '255,0,0'},${opacity})`,
        pointStyle: 'circle',
        pointRadius: 3,
        showLine: true,
        borderDash: [5, 5],
        borderWidth: 1,
        order: 3,  // Lower order for trails
      });
    }
  });

  // Add light trails for the Center of Mass
  for (let i = 1; i <= trailLength; i++) {
    const trailFrame = Math.max(0, frame - i);
    const opacity = 0.1 + (i / trailLength) * 0.4; // Light opacity (0.1 to 0.5)

    datasets.push({
      label: 'COM Trail',
      data: [
        { x: comData.value[trailFrame][0], y: comData.value[trailFrame][1] * -1 }
      ],
      borderColor: `rgba(255,165,0, ${opacity})`, // Light orange for the trail
      backgroundColor: `rgba(255,165,0, ${opacity})`,
      pointStyle: 'triangle',
      pointRadius: 4, // Smaller points for the trail
      borderWidth: 1,
      showLine: false,
      order: 8 // Lower order than the current frame COM
    });
  }

  // Center of Mass (current frame) - This will be added last to render on top
  const comDataset = {
    label: 'Center of Mass',
    data: [{ x: comData.value[frame][0], y: comData.value[frame][1] * -1 }],
    borderColor: 'black',
    backgroundColor: 'orange',
    pointStyle: 'triangle',
    pointRadius: 8,
    borderWidth: 2,
    showLine: false,
    order: 10 // High order for the COM dataset to ensure it's on top
  };

  // Explicitly push COM dataset last to ensure it renders on top
  datasets.push(comDataset);

  return { datasets };
});



const chartOptions = computed(() => ({
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      title: { display: true, text: 'X Position (m)' },
      min: -1200,
      max: 1200,
      reverse: true,
    },
    y: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: 'Y Position (m)' },
      min: -1200,
      max: 1200,
    }
  },
  aspectRatio: 1,
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false }
  },
  elements: {
    point: {
      radius: 0 // Hide all points by default
    }
  },
  datasets: {
    scatter: {
      pointRadius: (context) => {
        const dataset = context.dataset;
        const dataIndex = context.dataIndex;
        if (dataset.label === 'Center of Mass') {
          return dataIndex === 0 ? 12 : 5; // Larger point for current frame, smaller for trail
        }
        return dataset.pointRadius; // Use default radius for other datasets
      },
      z: (context) => {
        // Ensure the Center of Mass is always on top
        return context.dataset.label === 'Center of Mass' ? 1000 : 1;
      }
    }
  }
}));

watch(currentFrameNumber, () => {
  if (chartRef.value && chartRef.value.chart) {
    chartRef.value.chart.data = chartData.value;
    chartRef.value.chart.update('none'); // Update without animation
  }
});

watch([currentFrameNumber, comData, bodyData], () => {
  if (comData.value && bodyData.value && chartRef.value && chartRef.value.chart) {
    chartRef.value.chart.data = chartData.value;
    chartRef.value.chart.options = chartOptions.value;
    chartRef.value.chart.update('none'); // Update without animation
  }
}, { immediate: true });
</script>

<style scoped>
.com-bos-plot {
  padding: 1rem;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items:center;
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 100%;
  max-width: 800px;
  max-height: 800px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.full-size-chart {
  width: 100% !important;
  height: 100% !important;
  max-width: 100%;
  max-height: 100%;
}

#plot_title  {
  color: black;
}
</style>