import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAnimationStore = defineStore('animation', () => {

    const currentFrameNumber = ref(0);

    const setFrameNumber = (newFrameNumber) => {
        currentFrameNumber.value = newFrameNumber;
    };

    return {
        currentFrameNumber,
        setFrameNumber,
    };
    });