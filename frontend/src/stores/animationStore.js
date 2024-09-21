import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAnimationStore = defineStore('animation', () => {

    const currentFrameNumber = ref(null);
    const numFrames = ref(0);

    const setFrameNumber = (newFrameNumber) => {
        currentFrameNumber.value = newFrameNumber;
    };

    const setNumFrames = (newNumFrames) => {
        numFrames.value = newNumFrames;
    }

    return {
        currentFrameNumber,
        numFrames,
        setFrameNumber,
        setNumFrames,
    };
    });