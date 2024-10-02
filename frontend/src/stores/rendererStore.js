import { defineStore } from 'pinia';
import { shallowRef } from 'vue';

export const useRendererStore = defineStore('rendererStore', () => {

    const renderer = shallowRef(null);
    const scene = shallowRef(null);
    const camera = shallowRef(null);

    // Function to set the renderer
    const setRenderer = (newRenderer) => {
        renderer.value = newRenderer;
    }

    const setScene = (newScene) => { scene.value = newScene}

    const setCamera = (newCamera) => { camera.value = newCamera}

    return {
        scene,
        camera,
        renderer,
        setScene,
        setCamera,
        setRenderer,
    };
});
