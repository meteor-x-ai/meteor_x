<template>
    <div class="game--mode__page">
        <div v-if="gameCardsList.length === 4" class="card--container">
            <div v-for="card in gameCardsList" :key="card.name" class="card--item">
                <div class="card--name">{{ card.name }}</div>
                <img class="card--image" :src="`/game-card/${card.name}.webp`" alt="" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import "@/css/game-page.css"

enum eGameCardNames {
    ROCKET = "ROCKET",
    IGNORE = "IGNORE",
    EVACUATION = "EVACUATION",
    BUNKER = "BUNKER"
}

interface iGameCard {
    name: eGameCardNames
    userId?: string
}

const route = useRoute()
const soloMode = route.name === "game-solo-mode"
const gameCardsList = ref<iGameCard[]>([])


onMounted(() => {
    if (soloMode) {
        gameCardsList.value = Object.values(eGameCardNames).map(name => ({ name }))
    }
})
</script>

