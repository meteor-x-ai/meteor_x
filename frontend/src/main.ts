import { createApp } from 'vue'
import App from './App.vue'
import router from "./router.ts";

import Particles from "@tsparticles/vue3";
import { loadFull } from "tsparticles"
import "leaflet/dist/leaflet.css";
import './main.css'
import "@/css/keyframes.css"
import {createPinia} from "pinia";

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(Particles, {
    init: async (engine) => {
        await loadFull(engine);
    },
});

app.mount('#app')

console.log(" /$$      /$$             /$$                                         /$$   /$$\n" +
    "| $$$    /$$$            | $$                                        | $$  / $$\n" +
    "| $$$$  /$$$$  /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$   /$$$$$$       |  $$/ $$/\n" +
    "| $$ $$/$$ $$ /$$__  $$|_  $$_/   /$$__  $$ /$$__  $$ /$$__  $$       \\  $$$$/ \n" +
    "| $$  $$$| $$| $$$$$$$$  | $$    | $$$$$$$$| $$  \\ $$| $$  \\__/        >$$  $$ \n" +
    "| $$\\  $ | $$| $$_____/  | $$ /$$| $$_____/| $$  | $$| $$             /$$/\\  $$\n" +
    "| $$ \\/  | $$|  $$$$$$$  |  $$$$/|  $$$$$$$|  $$$$$$/| $$            | $$  \\ $$\n" +
    "|__/     |__/ \\_______/   \\___/   \\_______/ \\______/ |__/            |__/  |__/\n" +
    "                                                                               \n" +
    "                                                                               \n" +
    "                                                                               ")