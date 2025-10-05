<template>
    <div class="popup" @click.prevent>
        <img
            class="leave--button"
            @click="closePopup"
            src="/leave.svg"
            alt="Leave"
        />

        <div class="popup--input__container" @click.stop>
            <input
                class="popup--component popup--input"
                v-model="inputPrompt"
                :disabled="pending"
                :class="{'apply': generatedMeteor}"
            >
            <div class="popup--button__container">
                <button
                    class="popup--component popup--button"
                    @click="setMeteor"
                    :disabled="pending"
                >
                    {{pending ? 'Loading...' : 'Generate'}}
                </button>
                <button
                    v-if="generatedMeteor && !pending"
                    class="popup--component popup--button"
                    @click="applyMeteor"
                >
                    Apply
                </button>
            </div>
        </div>

        <div v-if="generatedMeteor && !pending" class="generated--container">
            <div v-for="(value, key) in generatedMeteor" class="generated-item">
                <span class="key">{{key}}:</span>
                <span class="value">{{value}}</span>
            </div>
        </div>
    </div>

</template>

<script setup lang="ts">
import type {iMeteor} from "@/models/meteor-models.ts";
import "@/css/popup-ai.css"
import {ref} from "vue";
import {BACK_PATH_API} from "@/repository/backendPath.ts";
import gsap from 'gsap'

const props = defineProps<{
    meteorValue: iMeteor,
    closeCallBack: () => void,
}>()

const emit = defineEmits<{
    apply: [meteor: iMeteor]
}>()

const pending = ref<boolean>(false)
const inputPrompt = ref<string>("")
const generatedMeteor = ref<iMeteor | null>(null)

const setMeteor = async () => {
    try {
        pending.value = true
        generatedMeteor.value = null

        const res = await fetch(`${BACK_PATH_API}/prompt?prompt=${inputPrompt.value}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json",
            }
        })

        if (!res.ok) {
            console.error(res.statusText)
            return;
        }

        const rawData = await res.json();
        generatedMeteor.value = JSON.parse(rawData).data
        if(generatedMeteor.value) {
            generatedMeteor.value.year = 2025
        }
    } catch (e) {
        console.error(e)
    } finally {
        inputPrompt.value = ''
        pending.value = false
    }
}

const applyMeteor = () => {
    if (generatedMeteor.value) {
        emit('apply', generatedMeteor.value)
        closePopup()
    }
}

const closePopup = () => {
    gsap.to('.popup', {
        opacity: 0,
        duration: .2,
        onComplete: () => {
            props.closeCallBack()
        }
    })
}
</script>