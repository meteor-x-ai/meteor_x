<template>
    <div class="game--mode__page">
        <div class="game--mode__button--container">
            <span class="game--mode__title">Save Planet</span>
            <template v-if="currentMode === 'select'">
                <div class="button__container">
                    <router-link :to="{name: 'game-solo-mode'}" class="game--mode__button">Solo</router-link>
                    <button
                        class="game--mode__button"
                        @click="currentMode = 'coop'"
                        :disabled="!currentUser"
                    >
                        Coop
                    </button>
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
                    <button class="game--mode__button" @click="joinRoom" :disabled="roomCodeInput.length !== 4">Join</button>
                    <button class="game--mode__button" @click="currentMode = 'create'">Create</button>
                </div>
            </template>
            <template v-else-if="currentMode === 'create'">
                <div v-if="roomInfo.code">Code: {{roomInfo.code}}</div>
                <span v-else>Code: <span class="code--loading">loading...</span></span>
                <span v-if="roomInfo.code">Users ↓</span>
                <div
                    class="user--container"
                    :class="{'current': user.id === currentUser?.id}"
                    @click="removeUser(user.id)"
                    v-for="(user, i) in users"
                >
                    {{i+1}}.{{user.username}}
                </div>
                <div class="button__container">
                    <button class="game--mode__button" @click="handleReturn">Cancel</button>
                    <button
                        class="game--mode__button"
                        v-if="roomInfo.id"
                        :disabled="users.length !== 4"
                    >
                        Start
                    </button>
                </div>
            </template>
            <template v-else-if="currentMode === 'room'">
                <span>Code: {{roomInfo.code}}</span>
                <span>Users ↓</span>
                <div
                    class="user--container"
                    :class="{'current': user.id === currentUser?.id}"
                    @click="removeUser(user.id)"
                    v-for="(user, i) in users"
                >
                    {{i+1}}.{{user.username}}
                </div>
            </template>
        </div>
        <teleport to="body">
            <div
                class="login--info--container"
                v-if="!pendingAuth"
                :class="{'unauthenticated': !currentUser}"
            >
                <div v-if="currentUser?.username">{{currentUser.username}}</div>
                <router-link
                    v-else
                    :to="{
                        name: 'login-page',
                        query: {
                            redirect: 'game'
                        }
                    }"
                >
                    unauthenticated
                </router-link>
            </div>
        </teleport>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-mode-page.css"
import {onBeforeMount, onUnmounted, reactive, ref, watch} from "vue";
import {useRoute, useRouter} from "vue-router";
import {io, Socket} from "socket.io-client";
import {BACK_PATH_WS} from "@/repository/backendPath.ts";
import {eGameRoomChangedTypes} from "@/enums/gameEnums.ts";
import authRepo from "@/repository/authRepo.ts";
import type {iUser} from "@/models/user-models.ts";

const route = useRoute();
const router = useRouter();

type modes = 'select' | 'coop' | 'create' | 'room'

const currentMode = ref<modes>('select')
const currentUser = ref<iUser | null>(null);

const socket = ref<Socket | null>(null);
const users = ref<iUser[]>([])

const roomInfo = reactive<{
    code: string,
    id: string,
}>({
    code: "",
    id: ""
})
const roomCodeInput = ref<string>("")

const pendingAuth = ref<boolean>(true);

const changeQueryMode = () => {
    const newQuery = { ...route.query };

    if (currentMode.value === 'select') {
        delete newQuery.mode;
    } else {
        newQuery.mode = currentMode.value;
    }
    if (currentMode.value !== 'room' && currentMode.value !== 'create') {
        delete newQuery.code;
    }

    router.replace({
        path: route.path,
        query: newQuery
    })
}

const initializeSocket = () => {
    if (socket.value) {
        return socket.value;
    }

    const newSocket = io(BACK_PATH_WS, {
        withCredentials: true,
        transports: ["websocket"],
        reconnection: true,
        reconnectionAttempts: 3,
        reconnectionDelay: 1000
    });

    newSocket.on("room_changed", (data) => {
        switch (data.type) {
            case eGameRoomChangedTypes.USER_ADDED:
                if (data.userId === currentUser.value?.id) return;
                users.value.push({
                    id: data.userId,
                    username: data.username
                });
                break;
            default:
                console.warn("Room changed unsupported:", data)
        }
    });

    newSocket.on("connect_error", (err) => {
        console.error("Socket connection error:", err);
    });

    newSocket.on("error", (err) => {
        console.error("Socket error:", err);
    });

    socket.value = newSocket;
    return newSocket;
};

const cleanupSocket = () => {
    if (socket.value) {
        socket.value.removeAllListeners();
        socket.value.disconnect();
        socket.value = null;
        users.value = [];
        roomInfo.code = "";
        roomInfo.id = "";
    }
};

const handleReturn = () => {
    cleanupSocket();
    currentMode.value = 'coop';
};

const codeManipulations = async () => {
    if (currentMode.value === "create" && !socket.value) {
        if (false) {
            //TODO connect by code from query
        } else {
            try {
                const newSocket = initializeSocket();

                newSocket.on("connect", () => {
                    newSocket.emit("join_room");
                });

                newSocket.on("room_created", async (data) => {
                    roomInfo.id = data.roomId;
                    roomInfo.code = data.code;
                    users.value = [{
                        username: `${currentUser.value?.username} (You)`,
                        id: currentUser.value?.id || ''
                    }]
                    await router.replace({
                        path: route.path,
                        query: {
                            ...route.query,
                            code: data.code
                        }
                    })
                });

                newSocket.on("lobby_update", (data) => {
                    console.log("Lobby update:", data);
                });

            } catch (error) {
                console.error("Error creating room:", error);
            }
        }
    } else if (currentMode.value === 'room') {

    } else {
        roomInfo.code = ""
    }
}

const joinRoom = async () => {
    try {
        const newSocket = initializeSocket();

        newSocket.on("connect", () => {
            newSocket.emit("join_existing_room", { code: roomCodeInput.value });
        });

        newSocket.on("room_joined", (data) => {
            console.log(data)
            users.value = data.users;
            roomInfo.id = data.roomId;
            console.log(data.code)
            roomInfo.code = data.code;
            currentMode.value = 'room';
        });

    } catch (error) {
        console.error("Error joining room:", error);
    }
}

const removeUser = (id: string) => {
    console.log(id)
}

watch(currentMode, () => {
    changeQueryMode();
    codeManipulations();
})

onBeforeMount(async () => {
    currentUser.value = await authRepo.auth();

    if (currentUser.value && (route.query.mode === 'coop' || route.query.mode === 'create')) {
        currentMode.value = route.query.mode as modes;
    }

    changeQueryMode();
    await codeManipulations();

    pendingAuth.value = false
})

onUnmounted(() => {
    cleanupSocket();
});
</script>