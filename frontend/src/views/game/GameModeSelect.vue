<template>
    <div class="game--mode__page">
        <div class="game--mode__button--container">
            <span class="game--mode__title">Save Planet</span>
            <template v-if="currentMode === 'select'">
                <div class="button__container">
                    <router-link :to="{name: 'game-solo-mode'}" class="game--mode__button">Solo</router-link>
                    <button class="game--mode__button" @click="currentMode = 'coop'">Coop</button>
                </div>
            </template>
            <template v-else-if="currentMode === 'coop'">
                <input
                    type="text"
                    maxlength="4"
                    class="game--mode__input"
                    placeholder="Input room code..."
                    v-model="roomCodeInput"
                    @input="roomCodeInput = roomCodeInput.replace(/\D/g, '')"
                >
                <div class="button__container">
                    <button class="game--mode__button" @click="currentMode = 'select'">Return</button>
                    <button class="game--mode__button" :disabled="roomCodeInput.length !== 4">Join</button>
                    <button class="game--mode__button" @click="currentMode = 'create'">Create</button>
                </div>
            </template>
            <template v-else-if="currentMode === 'create'">
                <div v-if="createdCoopCode">Code: {{createdCoopCode}}</div>
                <span v-else>Code: <span class="code--loading">loading...</span></span>
                <div class="button__container">
                    <button class="game--mode__button" @click="currentMode = 'coop'">Return</button>
                </div>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-mode-page.css"
import {ref, watch} from "vue";
import {useRoute, useRouter} from "vue-router";
import gameRepo from "@/repository/gameRepo.ts";

const route = useRoute();
const router = useRouter();

type modes = 'select' | 'coop' | 'create'

const currentMode = ref<modes>(
    (route.query.mode === 'coop' || route.query.mode === 'create')
        ? route.query.mode
        : 'select'
)

const createdCoopCode = ref<string>("")
const roomCodeInput = ref<string>("")

const changeQueryMode = (mode: modes) => {
    const newQuery = { ...route.query };

    if (mode === 'select') {
        delete newQuery.mode;
    } else {
        newQuery.mode = mode;
    }

    router.replace({
        path: route.path,
        query: newQuery
    })
}

const codeManipulations = async (mode: modes) => {
    if (mode === "create") {
        await gameRepo.getCode()
    } else {
        createdCoopCode.value = ""
    }
}

watch(currentMode, (newMode) => {
    changeQueryMode(newMode);
    codeManipulations(newMode);
})
</script>