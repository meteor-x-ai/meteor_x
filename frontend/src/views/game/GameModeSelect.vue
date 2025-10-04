<template>
    <div class="game--mode__page">
        <div class="game--mode__button--container">
            <span class="game--mode__title">Save Planet</span>
            <template v-if="!connectToCoop">
                <div class="button__container">
                    <router-link :to="{name: 'game-solo-mode'}" class="game--mode__button">Solo</router-link>
                    <button class="game--mode__button" @click="connectToCoop = true">Coop</button>
                </div>
            </template>
            <template v-else>
                <input
                    maxlength="15"
                    type="text"
                    class="game--mode__input"
                    placeholder="Create username..."
                    v-model="userNameInput"
                >
                <input
                    type="text"
                    maxlength="4"
                    class="game--mode__input"
                    placeholder="Input room code..."
                    v-model="roomCodeInput"
                    @input="roomCodeInput = roomCodeInput.replace(/\D/g, '')"
                >
                <div class="button__container">
                    <button class="game--mode__button" @click="connectToCoop = false">Return</button>
                    <button class="game--mode__button" :disabled="roomCodeInput.length !== 4">Join</button>
                    <button class="game--mode__button">Create</button>
                </div>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-mode-page.css"
import {ref} from "vue";

const connectToCoop = ref<boolean>(false)

const userNameInput = ref<string>("")
const roomCodeInput = ref<string>("")
</script>