import { createApp } from 'vue'
import App from './App.vue'
import router from "./router.ts";

import "leaflet/dist/leaflet.css";
import './style.css'
import "@/css/keyframes.css"

const app = createApp(App)

app.use(router)
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