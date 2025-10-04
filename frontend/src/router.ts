import { createRouter, createWebHistory } from 'vue-router'
import MapView from "./views/MapView.vue";
import MainPage from "@/views/MainPage.vue";
import GameModeSelect from "@/views/game/GameModeSelect.vue";
import GamePage from "@/views/game/GamePage.vue";
import GameRouter from "@/views/game/GameRouter.vue";
import LoginPage from "@/views/LoginPage.vue";
import SignupView from "@/views/SignupView.vue";

const routes = [
    {
        path: '/',
        name: 'main-page',
        component: MainPage,
    },
    {
        path: '/map',
        name: 'map-page',
        component: MapView
    },
    {
        path: '/login',
        name: 'login-page',
        component: LoginPage
    },
    {
        path: '/signup',
        name: 'signup-page',
        component: SignupView
    },
    {
        path: '/game',
        name: 'game-page',
        component: GameRouter,
        redirect: {name: 'game-mode-select'},
        children: [
            {
                path: '',
                name: 'game-mode-select',
                component: GameModeSelect,
            },
            {
                path: 'solo',
                name: 'game-solo-mode',
                component: GamePage
            },
            {
                path: 'coop/:roomId',
                name: 'game-coop-mode',
                component: GamePage
            }
        ]
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
