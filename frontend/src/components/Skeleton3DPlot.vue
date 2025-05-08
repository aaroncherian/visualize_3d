<template>
<!--  <button @click="getQualisys"></button>-->
  <div ref="container" class="threejs-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, defineExpose } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { useAnimationStore } from "@/stores/animationStore.js";
import { useRendererStore } from '@/stores/rendererStore.js';
import {useSkeletonStore} from "@/stores/skeletonStore.js";
import {storeToRefs} from "pinia";

const animationStore = useAnimationStore();
const { numFrames, currentFrameNumber } = storeToRefs(animationStore);

const rendererStore = useRendererStore();
const skeletonStore = useSkeletonStore();

const container = ref(null);
let availableSkeletonData = ref({});

let scene, camera, renderer, controls;



const props = defineProps({
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '100%'
  }
});

const skeletonSphereColorMap = {
  mediapipe: 0x1857ba,  // Blue
  qualisys: 0xf54242,   // Red
  // Add more mappings as needed
  default: 0x000000     // Black (default color)
};

const skeletonLineColorMap = {
  mediapipe: 0x0a367a,  // Blue
  qualisys: 0xab1515,   // Red
  // Add more mappings as needed
  default: 0x000000     // Black (default color)
};

const getSkeletonSphereColor = (trackerType) => {
  return skeletonSphereColorMap[trackerType] || skeletonSphereColorMap.default;
};

const getSkeletonLineColor = (trackerType) => {
  return skeletonLineColorMap[trackerType] || skeletonLineColorMap.default;
}

const handleResize = () => {
  camera.aspect = container.value.clientWidth / container.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
};

// Clean up on unmount
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

onMounted(async () => {
  initializeScene();
  animationStore.setFrameNumber(0)
  await fetchData('mediapipe');
  animate();

  watch(currentFrameNumber, (newFrame) => {
    visualizeAvailableSkeletons(newFrame, availableSkeletonData)
  });

  watch(
      () => skeletonStore.trackerToFetch,
      (newTracker) => {
        if (newTracker) {
          fetchData(newTracker);
          skeletonStore.resetFetchTracker(); // Reset after fetching if needed
        }
      }
  );


  setTimeout(handleResize, 0); // Trigger resize to ensure correct dimensions after initial load

  window.addEventListener('resize', handleResize);

});

let skeletonIDCounter = 0;

const fetchData = async (trackerType) => {
  try {
    const response = await fetch(`/api/data`);
    // Check if the response was successful (status 200-299)
    if (!response.ok) {
      console.error(`Failed to fetch skeleton data. HTTP status: ${response.status}`);
      return;  // Early exit if fetch fails
    }

    const skeletonData = await response.json();
    if (!isValidSkeletonData(skeletonData)) throw new Error('Invalid skeleton data');
    console.log('Skeleton data fetched: ', skeletonData);

    animationStore.setNumFrames(skeletonData.num_frames - 1);

    // Initialize Three.js group and add it to the scene
    const skeletonDataGroup = new THREE.Group();
    scene.add(skeletonDataGroup);

    // Increment skeleton ID counter and generate a unique ID
    skeletonIDCounter++;
    const skeletonID = `skeleton-${skeletonIDCounter}`;

    // Store the skeleton data in the availableSkeletonData object
    availableSkeletonData.value[skeletonID] = {
      id: skeletonID,
      trackerType,
      data: skeletonData,
      group: skeletonDataGroup
    };

    console.log(`Skeleton ${skeletonID} added to availableSkeletonData.`);
    visualizeAvailableSkeletons(animationStore.currentFrameNumber, availableSkeletonData);


  } catch (error) {
    // Catch and log any unexpected errors
    console.error('Error fetching or processing skeleton data:', error);
  }
};
defineExpose({ fetchData });


const getQualisys = () => {
  console.log('Fetching qualisys data');
  fetchData('qualisys');
};

const visualizeAvailableSkeletons = (frame, availableSkeletonData) => {
  Object.values(availableSkeletonData.value).forEach(skeleton => {
    visualizeData(frame, skeleton.data, skeleton.group, skeleton.trackerType);
  });
};


const visualizeData = (frame, data, group, trackerType) => {
  // console.log('Visualizing data for frame:', frame);
  clearDataGroup(group);
  plotSpheresAsJoints(frame, data.trajectories, group, trackerType)
  plotLinesAsConnections(data.segments, group, trackerType)
};

const clearDataGroup = (groupToClear) => {
  while (groupToClear.children.length > 0) {
    const child = groupToClear.children[0];
    groupToClear.remove(child);
    child.geometry.dispose();
    child.material.dispose();
  }
};

const plotSpheresAsJoints = (frame, trajectories, group, trackerType) => {
  const defaultSphereGeometry = new THREE.SphereGeometry(2, 16, 16);
  const selectedSphereGeometry = new THREE.SphereGeometry(2.5, 16, 16);
  const sphereColor = getSkeletonSphereColor(trackerType);
  const outlineMaterial = new THREE.MeshBasicMaterial({
    color: 0x000000,
    side: THREE.BackSide
  });
  const defaultSphereMaterial = new THREE.MeshBasicMaterial({color: sphereColor});
  const selectedSphereMaterial = new THREE.MeshBasicMaterial({color: 0x009aa6});

  for (const markerName in trajectories) {
    const markerData = trajectories[markerName];
    if (markerData && markerData[frame]) {
      // Create main sphere
      const sphereMaterial = defaultSphereMaterial;
      const sphereGeometry = defaultSphereGeometry;
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.position.set(markerData[frame][0] / 10, markerData[frame][1] / 10, markerData[frame][2] / 10);
      sphere.name = markerName;

      // Create outline sphere
      // const outlineSphere = new THREE.Mesh(sphereGeometry, outlineMaterial);
      // outlineSphere.position.copy(sphere.position);
      // outlineSphere.scale.multiplyScalar(1.2); // Make it slightly larger

      // Add both spheres to the group
      group.add(sphere);
      // group.add(outlineSphere);
    }
  }
}

const plotLinesAsConnections = (connections, group, trackerType) => {
  const lineColor = getSkeletonLineColor(trackerType);
  const lineMaterial = new THREE.LineBasicMaterial({
    color: lineColor,
  });

  const lineVertices = [];
  for (const [segmentName, segmentData] of Object.entries(connections)) {
    lineVertices.length = 0
    for (const [connectionPoint, markerName] of Object.entries(segmentData)) {
      lineVertices.push(group.getObjectByName(markerName).position.clone())
    }
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(lineVertices);
    const lineObject = new THREE.Line(lineGeometry, lineMaterial);
    group.add(lineObject);
  }
}

const initializeScene = () => {
  // const scene = new THREE.Scene();
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xffffff);

  // const renderer = new THREE.WebGLRenderer();
  renderer = new THREE.WebGLRenderer();
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio); // Set the pixel ratio for better clarity
  container.value.appendChild(renderer.domElement);

  // const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 250, 500);
  camera.lookAt(0, 0, 0);
  camera.up.set(0, 0, 1);

  rendererStore.setScene(scene);
  console.log('Scene initialized:', rendererStore.scene);

  rendererStore.setCamera(camera);
  console.log('Camera initialized:', rendererStore.camera);

  rendererStore.setRenderer(renderer);
  console.log('Renderer initialized:', rendererStore.renderer);

  // const controls = new OrbitControls(camera, renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  // const skeletonDataGroup = new THREE.Group();
  // skeletonDataGroup = new THREE.Group();
  // scene.add(skeletonDataGroup);
  const grid_size = 500;
  const grid_divisions = 10;
  const gridHelper = new THREE.GridHelper(grid_size, grid_divisions);
  gridHelper.rotation.x = Math.PI / 2;
  const gridLine = new THREE.Line3(gridHelper.geometry.attributes.position.array[0], gridHelper.geometry.attributes.position.array[1]);
  scene.add(gridHelper);

}

const isValidSkeletonData = (data) => {
  return data && typeof data === 'object' &&
      typeof data.num_frames === 'number' &&
      data.trajectories && data.segments;
};

const animate = function () {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);


};
</script>

<style scoped>
.threejs-container {
  width: v-bind(width);
  height: v-bind(height);
}

</style>
