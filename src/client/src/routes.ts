import { createMemoryHistory, createRouter } from 'vue-router'
import MapView from "./components/MapView.vue";
import DashboardView from "./components/DashboardView.vue";

const routes = [
    { path: '/map', name: 'map', component: MapView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/', component: MapView },
];

export const router = createRouter({
    history: createMemoryHistory(),
    routes,
});