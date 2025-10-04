import { createRouter, createWebHistory } from 'vue-router'
import MapView from "./views/MapView.vue";

const routes = [
    {
        path: '/map',
        name: 'map-page',
        component: MapView
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/map'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
