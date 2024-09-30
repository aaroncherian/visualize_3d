import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useRendererStore = defineStore('rendererStore', () => {

    const renderer = ref(null);

    // Function to set the renderer
    const setRenderer = (newRenderer) => {
        renderer.value = newRenderer;
    }

    return {
        renderer,
        setRenderer
    };
});
