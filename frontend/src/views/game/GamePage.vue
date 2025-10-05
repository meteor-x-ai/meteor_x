<template>
    <teleport to="body">
        <div v-if="!gameStarted" class="timer--container">
            <span id="timer" />
        </div>
    </teleport>

    <teleport to="body" v-if="gameStarted && lifeCount === 0">
        <div class="total--count__wrapper">
            <div class="total--count__container">
                <h1>Lose</h1>
                <span>Total success: <span class="value">{{successCount}}</span></span>
                <span>Total card uses:</span>
                <ol>
                    <li>Rocket - <span class="value">{{cardUsesCount.rocket}}</span></li>
                    <li>Ignore - <span class="value">{{cardUsesCount.ignore}}</span></li>
                    <li>Evacuation - <span class="value">{{cardUsesCount.evacuation}}</span></li>
                    <li>Bunker - <span class="value">{{cardUsesCount.bunker}}</span></li>
                </ol>
                <router-link :to="{name: 'game-mode-select'}" class="total--count__wrapper--button return">
                    Return to game menu
                </router-link>
            </div>
        </div>
    </teleport>

    <div
        class="try--container"
        :class="{
            'try--success': successTry,
            'try--fail': successTry === false
        }"
    />

    <div
        v-if="gameStarted"
        :class="`life--count__container ${lifeCountLvl}`"
    />

    <div class="game--mode__page">
        <div class="meteor--enemy__container" v-if="gameStarted && currentMeteor">
<!--            <img src="/meteor-enemy.svg" alt="">-->
            <div class="meteor--enemy__description">
               <span
                   v-for="(value, key) in currentMeteor"
               >
                   {{key.replace('_', ' ').toLowerCase()}}: {{value.toString().replace("_", '').toLowerCase()}}
               </span>
            </div>
        </div>

        <div v-if="gameStarted && gameCardsList.length === 4" class="card--container">
            <div
                class="card--item"
                v-for="card in gameCardsList"
                @click="cardCLickDispatcher(card)"
                :class="{'card--item__disabled': !currentMeteor || pendingCardValidation}"
            >
                <div class="card--name">{{card.name}}</div>
                <img class="card--image" :src="`/game-card/${card.name}.png`" alt="">
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import {computed, onMounted, reactive, ref} from "vue";
import {useRoute} from "vue-router";
import {eGameCardNames, eGameSocketEvent} from "@/enums/gameEnums.ts";
import type {iGameMeteor} from "@/models/meteor-models.ts";
import {type Socket} from "socket.io-client";
import {BACK_PATH_API} from "@/repository/backendPath.ts";

import "@/css/game-page.scss"
import {useSocketStore} from "@/services/wsService.ts";

interface iGameCard {
    name: eGameCardNames
    userId?: string
    userName?: string
}

const route = useRoute()
const soloMode = route.name === "game-solo-mode"

type lifeCountLvlTypes = 'low' | 'mid' | 'full'

const SETTINGS_START_LIFE_COUNT = 3;

const lifeCount = ref<number>(0);
const successTry = ref<boolean | null>(null);
const gameStarted = ref<boolean>(false);
const successCount = ref<number>(0);
const gameCardsList = ref<iGameCard[]>([]);
const currentMeteor = ref<iGameMeteor | null>(null);
const pendingCardValidation = ref<boolean>(false);

const socket = ref<Socket | null>(null);

const socketStore = useSocketStore()

const cardUsesCount = reactive({
    rocket: 0,
    ignore: 0,
    evacuation: 0,
    bunker: 0
})

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

async function checkCardSuccess(card: iGameCard): Promise<boolean> {
    if (!currentMeteor.value) return false;

    const res = await fetch(`${BACK_PATH_API}/validate-card`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "accept": "application/json"
        },
        body: JSON.stringify({
            generated_scenario: currentMeteor.value.generated_scenario,
            chosen_card: card.name
        })
    })

    const data = await res.json();
    return data.is_correct
}

const startGame = async () => {
    for (let i = 3; i > 0; i--) {
        const textElement = document.getElementById('timer')
        if (textElement) textElement.textContent = i.toString()
        await sleep(1000)
    }

    lifeCount.value = SETTINGS_START_LIFE_COUNT
    gameStarted.value = true;
}

const cardCLickDispatcher = async (card: iGameCard) => {
    if (!currentMeteor.value || pendingCardValidation.value) return;

    pendingCardValidation.value = true

    cardUsesCount[card.name.toLowerCase() as keyof typeof cardUsesCount]++

    if (soloMode) {
        const success = await checkCardSuccess(card)
        successTry.value = success

        currentMeteor.value = null;

        if (success) {
            successCount.value++
        } else {
            lifeCount.value--
        }

        await new Promise<void>(resolve => {
            setTimeout(() => {
                successTry.value = null;
                resolve()
            }, 1000)
        })

        currentMeteor.value = await generateMeteor()
    } else {

    }
    pendingCardValidation.value = false
}

const lifeCountLvl = computed<lifeCountLvlTypes>(() => {
    switch (lifeCount.value) {
        case 1: return 'low'
        case 2: return 'mid'
        case 3: return 'full'
        default: return 'full'
    }
})

const initializeSocket = () => {
    if (!socketStore.socket?.connected) socketStore.connect()
    socket.value = socketStore.socket

    if (socket.value === null) return

    socket.value.emit(eGameSocketEvent.EMIT.JOIN_GAME, {
        roomCode: route.params.roomCode,
    });

    socket.value.on(eGameSocketEvent.ON.GAME_READY, (data) => {
        console.log("GAME_READY: ", data);
    })

    socket.value.on(eGameSocketEvent.ON.GAME_WAIT_ROOM, (data) => {
        console.log("GAME_WAIT_ROOM: ", data);
    })
}

const generateMeteor = async (): Promise<iGameMeteor | null> => {
    try {
        const res = await fetch(`${BACK_PATH_API}/generate-meteor`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            }
        })

        return await res.json() as iGameMeteor
    } catch (e) {
        console.error('Error while fetching /generate-meteor: ', e)
        return null
    }
}

onMounted(async () => {
    if (soloMode) {
        gameCardsList.value = Object.values(eGameCardNames).map(name => ({ name }))

        currentMeteor.value = await generateMeteor()
        await startGame()
    } else {
        initializeSocket()
    }
})
</script>

