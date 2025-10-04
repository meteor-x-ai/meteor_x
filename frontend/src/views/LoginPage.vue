<template>
    <AuthLayout>
        <div class="login--container">
            <div class="login--box">
                <h2>Login</h2>
                <p class="welcome--text">Welcome back 👋</p>

                <form @submit.prevent="loginWrapper">
                    <input
                        required
                        v-model="username"
                        type="text"
                        placeholder="Username"
                        class="input--field"
                        @input="onUsernameInput"
                    />
                    <div class="password--field">
                        <input
                            required
                            v-model="passwordInput"
                            :type="showPassword ? 'text' :'password'"
                            placeholder="Password"
                            class="input"
                            @input="onPasswordInput"
                        />
                        <button type="button" class="eye--btn" @click="showPassword = !showPassword">
                            <Eye v-if="showPassword" class="eye--icon"></Eye>
                            <EyeOff v-else class="eye--icon"></EyeOff>
                        </button>
                    </div>
                    <button type="submit" class="login--button">Login</button>
                </form>

                <p class="signup--text">
                    Don’t have an account?
                    <router-link :to="{ name: 'signup-page' }" class="link">Sign up</router-link>
                </p>
            </div>
        </div>
    </AuthLayout>
</template>

<script setup lang="ts">
import AuthLayout from "@/views/Auth.vue"
import authRepo from "@/repository/authRepo.ts"
import { ref } from "vue"
import { useRouter } from "vue-router"
import {Eye, EyeOff} from "lucide-vue-next";

const router = useRouter()
const username = ref<string>("")
const passwordInput = ref<string>("")
const showPassword = ref(false)
const loginWrapper = async () => {
    if (await authRepo.login(username.value, passwordInput.value)) {
        await router.push({ name: "main-page" })
    }
}
const onUsernameInput = (e: Event) => {
    const target = e.target as HTMLInputElement
    username.value = target.value.replace(/[^a-zA-Z0-9]/g, "");

}
const onPasswordInput = (e: Event) => {
    const target = e.target as HTMLInputElement
    passwordInput.value = target.value.replace(/[^a-zA-Z0-9]/g, "");

}
</script>
