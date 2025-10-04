<template>
    <form @submit.prevent="signupWrapper">
        <input required v-model="username" type="text" placeholder="Username" />
        <input required v-model="passwordInput" type="text" placeholder="Password" />
        <button type="submit">submit</button>
        <router-link :to="{name: 'login-page'}">
            login
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

const signupWrapper = async () => {
    if (await authRepo.signup(username.value, passwordInput.value)) {
        await router.push({
            name: 'main-page'
        })
    }
}
</script>