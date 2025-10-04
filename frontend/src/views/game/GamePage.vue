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
                <span>Total success: {{successCount}}</span>
                <span>Total card uses:</span>
                <ol>
                    <li>Rocket - {{cardUsesCount.rocket}}</li>
                    <li>Ignore - {{cardUsesCount.ignore}}</li>
                    <li>Evacuation - {{cardUsesCount.evacuation}}</li>
                    <li>Bunker - {{cardUsesCount.bunker}}</li>
                </ol>
                <router-link :to="{name: 'game-mode-select'}" class="game--mode__button return">
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
            <img src="/meteor-enemy.svg" alt="">
            <div class="meteor--enemy__description">
                <span>Distance: {{currentMeteor.distance}}km, Speed: {{currentMeteor.speed}}km\s, Weight: {{currentMeteor.weight}}kg</span>
            </div>
        </div>

        <div v-if="gameStarted && gameCardsList.length === 4" class="card--container">
            <div
                class="card--item"
                v-for="card in gameCardsList"
                @click="cardCLickDispatcher(card)"
                :class="{'card--item__disabled': !currentMeteor}"
            >
                <div class="card--name">{{card.name}}</div>
                <img class="card--image" :src="`/game-card/${card.name}.webp`" alt="">
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-page.css"
import {computed, onMounted, reactive, ref} from "vue";
import {useRoute} from "vue-router";
import {eGameCardNames} from "@/enums/gameEnums.ts";
import type {iGameMeteor} from "@/models/meteor-models.ts";

interface iGameCard {
    name: eGameCardNames;
    userId?: string;
}

const route = useRoute();

const soloMode = route.name === "game-solo-mode"

const SETTINGS_DAMAGE_THRESHOLD = 1e9;
const SETTINGS_CRITICAL_TIME = 60 * 60 * 2.5; //2.5h
const SETTINGS_START_LIFE_COUNT = 3;

const gameCardsList = ref<iGameCard[]>([]);
const gameStarted = ref<boolean>(false);
const currentMeteor = ref<iGameMeteor | null>(null);
const lifeCount = ref<number>(0);
const successTry = ref<boolean | null>(null);
const successCount = ref<number>(0);

const cardUsesCount = reactive({
    rocket: 0,
    ignore: 0,
    evacuation: 0,
    bunker: 0
})

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

function checkCardSuccess(card: iGameCard): boolean | undefined {
    if (!currentMeteor.value) return;

    const timeToImpact = currentMeteor.value.distance / currentMeteor.value.speed;
    const potentialDamage = currentMeteor.value.weight * currentMeteor.value.speed ** 2;

    switch (card.name) {
        case eGameCardNames.ROCKET: return currentMeteor.value.weight < 1_000_000;
        case eGameCardNames.BUNKER: return timeToImpact <= SETTINGS_CRITICAL_TIME;
        case eGameCardNames.IGNORE: return potentialDamage < SETTINGS_DAMAGE_THRESHOLD;
        case eGameCardNames.EVACUATION: return timeToImpact > SETTINGS_CRITICAL_TIME;
        default: return false;
    }
}

const cardCLickDispatcher = async (card: iGameCard) => {
    if (!currentMeteor.value) return;

    cardUsesCount[card.name.toLowerCase() as keyof typeof cardUsesCount]++

    const successfulCards = gameCardsList.value
        .filter(c => checkCardSuccess(c))
        .map(c => c.name)
        .slice(0, 4);

    currentMeteor.value = null;

    const success = successfulCards.includes(card.name)
    successTry.value = success

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

    currentMeteor.value = createMeteor()
}

const createMeteor = (): iGameMeteor => {
    const distance = Math.floor(Math.random() * (500_000 - 50_000) + 50_000);
    const speed = Math.floor(Math.random() * (50 - 10) + 10);
    const weight = Math.floor(Math.random() * (2_000_000 - 100_000) + 100_000);

    const timeToImpact = distance / speed;

    return {
        id: Date.now(),
        distance,
        speed,
        weight,
        timeToImpact
    };
};

const lifeCountLvl = computed(() => {
    switch (lifeCount.value) {
        case 1: return 'low'
        case 2: return 'mid'
        case 3: return 'full'
    }
})

onMounted(async () => {
    if (soloMode) {
        gameCardsList.value = Object.values(eGameCardNames).map(name => ({name}))

        for (let i = 3; i > 0; i--) {
            const textElement = document.getElementById('timer')
            if (textElement) textElement.textContent = i.toString()
            await sleep(1000)
        }

        currentMeteor.value = createMeteor()

        lifeCount.value = SETTINGS_START_LIFE_COUNT
    }
    gameStarted.value = true;
})
</script>