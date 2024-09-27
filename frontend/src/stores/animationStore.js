import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAnimationStore = defineStore('animation', () => {

    const currentFrameNumber = ref(null);
    const numFrames = ref(0);
    const isPlaying = ref(false);
    const fps = ref(30);

    const setFrameNumber = (newFrameNumber) => {
        currentFrameNumber.value = newFrameNumber;
    };

    const setNumFrames = (newNumFrames) => {
        numFrames.value = newNumFrames;
    }

    const setIsPlaying = (playing) => {
        isPlaying.value = playing;
    }

    const setFps = (newFps) => {
        fps.value = newFps;
    }

    return {
        currentFrameNumber,
        numFrames,
        isPlaying,
        fps,
        setFrameNumber,
        setNumFrames,
        setIsPlaying,
        setFps
    };
    });