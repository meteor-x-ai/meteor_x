<template>
    <form @submit.prevent="loginWrapper">
        <input required v-model="username" type="text" placeholder="Username" />
        <input required v-model="passwordInput" type="text" placeholder="Password" />
        <button type="submit">submit</button>
        <router-link :to="{name: 'signup-page'}">
            signup
        </router-link>
    </form>
</template>

<script setup lang="ts">
import authRepo from "@/repository/authRepo.ts";
import {ref} from "vue";
import {useRouter} from "vue-router";

const router = useRouter();

const username = ref<string>("")
const passwordInput = ref<string>("")

const loginWrapper = async () => {
    if (await authRepo.login(username.value, passwordInput.value)) {
        await router.push({
            name: 'main-page'
        })
    }
}
</script>