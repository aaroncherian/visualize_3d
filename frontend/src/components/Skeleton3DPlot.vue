<template>
  <div ref="container" class="threejs-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { useAnimationStore } from "@/stores/animationStore.js";
import { useRendererStore } from '@/stores/rendererStore.js';
import {storeToRefs} from "pinia";

const animationStore = useAnimationStore();
const { numFrames, currentFrameNumber } = storeToRefs(animationStore);

const rendererStore = useRendererStore();

const container = ref(null);
let availableSkeletonData = ref({});

let scene, camera, renderer, controls, skeletonDataGroup;

const skeletonDataObject = {};

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
  await fetchData('mediapipe');
  animationStore.setFrameNumber(0)
  visualizeAvailableSkeletons(animationStore.currentFrameNumber, availableSkeletonData);
  animate();

  watch(currentFrameNumber, (newFrame) => {
    visualizeAvailableSkeletons(newFrame, availableSkeletonData)
  });


  setTimeout(handleResize, 0); // Trigger resize to ensure correct dimensions after initial load

  window.addEventListener('resize', handleResize);

});

let skeletonIDCounter = 0;

const fetchData = async (trackerType) => {
  try {
    const response = await fetch(`/api/data/${trackerType}`);

    // Check if the response was successful (status 200-299)
    if (!response.ok) {
      console.error(`Failed to fetch skeleton data. HTTP status: ${response.status}`);
      return;  // Early exit if fetch fails
    }

    const skeletonData = ref([]);  // Reactive skeletonData
    skeletonData.value = await response.json();

    // Validate that skeletonData exists and contains expected properties
    if (!skeletonData.value || typeof skeletonData.value !== 'object') {
      console.error('Fetched skeleton data is invalid or empty:', skeletonData.value);
      return;  // Early exit if skeletonData is not valid
    }

    console.log('Skeleton data fetched: ', skeletonData.value);

    // Check that num_frames exists before proceeding
    if (!skeletonData.value.num_frames || typeof skeletonData.value.num_frames !== 'number') {
      console.error('Skeleton data does not contain valid num_frames:', skeletonData.value);
      return;  // Early exit if num_frames is invalid
    }

    console.log(currentFrameNumber.value);
    animationStore.setNumFrames(skeletonData.value.num_frames - 1);

    // Initialize Three.js group and add it to the scene
    const skeletonDataGroup = new THREE.Group();
    scene.add(skeletonDataGroup);

    // Increment skeleton ID counter and generate a unique ID
    skeletonIDCounter++;
    const skeletonID = `skeleton-${skeletonIDCounter}`;

    // Store the skeleton data in the availableSkeletonData object
    const thisSkeletonData = {
      id: skeletonID,
      trackerType: trackerType,
      data: skeletonData,
      group: skeletonDataGroup
    };

    availableSkeletonData.value[skeletonID] = thisSkeletonData;

    console.log(`Skeleton ${skeletonID} added to availableSkeletonData.`);

  } catch (error) {
    // Catch and log any unexpected errors
    console.error('Error fetching or processing skeleton data:', error);
  }
};

const visualizeAvailableSkeletons = (frame, availableSkeletonData) => {
  for (let skeletonID in availableSkeletonData.value) {
    const availableSkeleton = availableSkeletonData.value[skeletonID];
    visualizeData(frame, availableSkeleton.data, availableSkeleton.group);
  }
};

const visualizeData = (frame, data, group) => {
  console.log('Visualizing data for frame:', frame);
  clearDataGroup(group);

  plotSpheresAsJoints(frame, data.trajectories, group)
  plotLinesAsConnections(data.segments, group)
};

const clearDataGroup = (groupToClear) => {
  while (groupToClear.children.length > 0) {
    const child = groupToClear.children[0];
    groupToClear.remove(child);
    child.geometry.dispose();
    child.material.dispose();
  }
};

const plotSpheresAsJoints = (frame, trajectories, group) => {

  const defaultSphereGeometry = new THREE.SphereGeometry(2, 16, 16);
  const selectedSphereGeometry = new THREE.SphereGeometry(2.5, 16, 16);
  const defaultSphereMaterial = new THREE.MeshBasicMaterial({color: 0x000000});
  const selectedSphereMaterial = new THREE.MeshBasicMaterial({color: 0x009aa6});

  for (const markerName in trajectories) {
    const markerData = trajectories[markerName];
    if (markerData && markerData[frame]) {
      const sphereMaterial = defaultSphereMaterial;
      const sphereGeometry = defaultSphereGeometry;
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.position.set(markerData[frame][0] / 10, markerData[frame][1] / 10, markerData[frame][2] / 10);
      sphere.name = markerName;
      group.add(sphere);
    }
  }
}

const plotLinesAsConnections = (connections, group) => {
  const lineVertices = [];
  for (const [segmentName, segmentData] of Object.entries(connections)) {
    lineVertices.length = 0
    for (const [connectionPoint, markerName] of Object.entries(segmentData)) {
      lineVertices.push(group.getObjectByName(markerName).position.clone())
    }
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(lineVertices);
    const lineMaterial = new THREE.LineBasicMaterial({color: 0x000000});
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
