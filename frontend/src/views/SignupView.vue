<template>
    <AuthLayout>
        <div class="login--container">
            <div class="login--box">
                <h2>Sign Up</h2>
                <p class="welcome--text">Create your account ✨</p>

                <form @submit.prevent="signupWrapper">
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
                            :type="showPassword ? 'text' : 'password'"
                            placeholder="Password"
                            @input="onPasswordInput"
                        />
                        <button type="button" class="eye--btn" @click="showPassword = !showPassword">
                            <Eye v-if="showPassword" class="eye--icon"/>
                            <EyeOff v-else class="eye--icon"/>
                        </button>
                    </div>

                    <div class="password--field">
                        <input
                            required
                            v-model="confirmPassword"
                            :type="showConfirmPassword ? 'text' : 'password'"
                            placeholder="Confirm Password"
                            @input="onConfirmPassword"
                        />
                        <button type="button" class="eye--btn" @click="showConfirmPassword = !showConfirmPassword">
                            <Eye v-if="showConfirmPassword" class="eye--icon"/>
                            <EyeOff v-else class="eye--icon"/>
                        </button>
                    </div>

                    <p v-if="submitted && passwordInput!==confirmPassword" class="error--text">
                        Password doesn't match
                    </p>

                    <button type="submit" class="login--button">Sign Up</button>
                </form>

                <p class="signup--text">
                    Already have an account?
                    <router-link :to="{ name: 'login-page' }" class="link">Login</router-link>
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
import { Eye, EyeOff } from 'lucide-vue-next'


const router = useRouter()
const username = ref<string>("")
const passwordInput = ref<string>("")
const confirmPassword = ref<string>("")
const submitted =ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const signupWrapper = async () => {
    submitted.value = true;
    if(passwordInput.value!==confirmPassword.value){
        return
    }
    if (await authRepo.signup(username.value, passwordInput.value)) {
        await router.push({ name: "main-page" })
    }
}
const onUsernameInput = (e: Event) => {
    const target = e.target as HTMLInputElement
    username.value = target.value.replace(/[^a-zA-Z0-9]/g, "")
}
const onPasswordInput= (e: Event) => {
    const target = e.target as HTMLInputElement
    passwordInput.value = target.value.replace(/[^a-zA-Z0-9]/g, "")
}
const onConfirmPassword = (e: Event) => {
    const target = e.target as HTMLInputElement
    confirmPassword.value = target.value.replace(/[^a-zA-Z0-9]/g, "")
}
</script>
