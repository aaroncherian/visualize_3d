import './assets/main.css';
import PrimeVue from 'primevue/config';
import 'primevue/resources/primevue.min.css';       // PrimeVue core styles
import 'primeflex/primeflex.css';                   // PrimeFlex for layout
import 'primevue/resources/themes/aura-light-amber/theme.css';


import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

import Chart from 'chart.js/auto'
import annotationPlugin from 'chartjs-plugin-annotation';

Chart.register(annotationPlugin);

const app = createApp(App);
const pinia = createPinia();
// Use PrimeVue without specifying a theme preset
app.use(PrimeVue, {
    chart: {
        plugins: [annotationPlugin]
    }
});app.use(pinia)

app.mount('#app');