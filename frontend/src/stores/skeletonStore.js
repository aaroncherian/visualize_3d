import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSkeletonStore = defineStore('skeleton', () => {
    // State
    const fetchSource = ref('');

    // Action to trigger fetching data from a specific source
    const triggerFetch = (source) => {
        fetchSource.value = source;
    };

    // Reset the fetch source
    const resetFetch = () => {
        fetchSource.value = '';
    };

    return {
        fetchSource,
        triggerFetch,
        resetFetch,
    };
});