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

const chartData = computed(() => {
  if (!comData.value || !bodyData.value) return { datasets: [] };

  const frame = currentFrameNumber.value;
  const trailLength = 20;

  const datasets = [
    // Left foot (current frame)
    {
      label: 'Left Foot',
      data: [
        { x: bodyData.value.trajectories.left_heel[frame][0], y: bodyData.value.trajectories.left_heel[frame][1]*-1 },
        { x: bodyData.value.trajectories.left_foot_index[frame][0],
          y: bodyData.value.trajectories.left_foot_index[frame][1] * -1
        }
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
        {x: bodyData.value.trajectories.right_heel[frame][0], y: bodyData.value.trajectories.right_heel[frame][1] * -1},
        {
          x: bodyData.value.trajectories.right_foot_index[frame][0],
          y: bodyData.value.trajectories.right_foot_index[frame][1] * -1
        }
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
  ];

  // Add trails for feet
  ['Left Foot', 'Right Foot'].forEach((label, index) => {
    for (let i = 1; i <= trailLength; i++) {
      const trailFrame = Math.max(0, frame - i);
      const opacity = 1 - (i / trailLength);
      let trailData;

      if (label.includes('Foot')) {
        const side = label.split(' ')[0].toLowerCase();
        trailData = [
          {
            x: bodyData.value.trajectories[`${side}_heel`][trailFrame][0],
            y: bodyData.value.trajectories[`${side}_heel`][trailFrame][1] * -1
          },
          {
            x: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][0],
            y: bodyData.value.trajectories[`${side}_foot_index`][trailFrame][1] * -1
          }
        ];
      }

      datasets.push({
        data: trailData,
        borderColor: `rgba(${label.includes('Left') ? '0,0,255' : '255,0,0'},${opacity})`,
        backgroundColor: `rgba(${label.includes('Left') ? '0,0,255' : '255,0,0'},${opacity})`,
        pointStyle: 'circle',
        pointRadius: 3,
        showLine: true,
        borderDash: [5, 5],
        borderWidth: 1
      });
    }
  });

  // Center of Mass (current frame and trail)
  const comDataset = {
    label: 'Center of Mass',
    data: [{x: comData.value[frame][0], y: comData.value[frame][1] * -1}],
    borderColor: 'orange',
    backgroundColor: 'orange',
    pointStyle: 'star',
    pointRadius: 12,
    pointBorderWidth: 2,
    showLine: false,
  };

  // COM trail
  for (let i = 1; i <= trailLength; i++) {
    const trailFrame = Math.max(0, frame - i);
    const opacity = 1 - (i / trailLength);
    comDataset.data.push({
      x: comData.value[trailFrame][0],
      y: comData.value[trailFrame][1] * -1,
      pointStyle: 'circle',
      pointRadius: 5,
      borderColor: `rgba(255,165,0,${opacity})`,
      backgroundColor: `rgba(255,165,0,${opacity})`
    });
  }

  // Add COM dataset last to ensure it's on top
  datasets.push(comDataset);

  return {datasets};
});

const chartOptions = computed(() => ({
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      title: {display: true, text: 'X Position (m)'},
      min: -1000,
      max: 1000,
      reverse: true,
    },
    y: {
      type: 'linear',
      position: 'left',
      title: {display: true, text: 'Y Position (m)'},
      min: -1000,
      max: 1000,
    }
  },
  aspectRatio: 1,
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {display: false},
    tooltip: {enabled: false}
  },
  elements: {
    point: {
      radius: 0 // Hide all points by default
    }
  },
  datasets: {
    scatter: {
      pointRadius: (context) => {
        // Custom function to set point radius
        const dataset = context.dataset;
        const dataIndex = context.dataIndex;
        if (dataset.label === 'Center of Mass') {
          return dataIndex === 0 ? 12 : 5; // Larger point for current frame, smaller for trail
        }
        return dataset.pointRadius; // Use default radius for other datasets
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

watch([comData, bodyData], () => {
  if (comData.value && bodyData.value && chartRef.value && chartRef.value.chart) {
    chartRef.value.chart.data = chartData.value;
    chartRef.value.chart.options = chartOptions.value;
    chartRef.value.chart.update('none');
  }
}, {immediate: true});
</script>

<style scoped>
.com-bos-plot {
  padding: 1rem;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex-grow: 1;
  width: 100%;
  height: 100%;
}

.full-size-chart {
  width: 100% !important;
  height: 100% !important;
}
</style>