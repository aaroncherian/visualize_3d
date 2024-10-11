import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSkeletonStore = defineStore('skeleton', () => {
    // State
    const trackerToFetch = ref('');

    // Action to trigger fetching data from a specific source
    const triggerDataFetch = (tracker) => {
        trackerToFetch.value = tracker;
    };

    // Reset the fetch source
    const resetFetchTracker = () => {
        trackerToFetch.value = '';
    };

    return {
        trackerToFetch,
        triggerDataFetch,
        resetFetchTracker,
    };
});