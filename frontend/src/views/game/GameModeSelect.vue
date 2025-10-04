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
                    <button class="game--mode__button" @click="joinRoom" :disabled="roomCodeInput.length !== 4">Join</button>
                    <button class="game--mode__button" @click="currentMode = 'create'">Create</button>
                </div>
            </template>
            <template v-else-if="currentMode === 'create'">
                <div v-if="createdCoopCode">Code: {{createdCoopCode}}</div>
                <span v-else>Code: <span class="code--loading">loading...</span></span>
                <div>
                    <div v-for="user in users">
                        {{user}}
                    </div>
                </div>
                <div class="button__container">
                    <button class="game--mode__button" @click="currentMode = 'coop'">Return</button>
                </div>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-mode-page.css"
import {onMounted, ref, watch} from "vue";
import {useRoute, useRouter} from "vue-router";
import {io, Socket} from "socket.io-client";
import {BACK_PATH_WS} from "@/repository/backendPath.ts";
import {eGameRoomChangedTypes} from "@/enums/gameEnums.ts";

interface iUser {
    id: string;
    username: string;
}

const route = useRoute();
const router = useRouter();

type modes = 'select' | 'coop' | 'create'

const currentMode = ref<modes>(
    (route.query.mode === 'coop' || route.query.mode === 'create')
        ? route.query.mode
        : 'select'
)

const socket = ref<Socket | null>(null);
const users = ref<iUser[]>([])

const createdCoopCode = ref<string>("")
const createdCoopId = ref<string>("")
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

const initializeSocket = () => {
    if (socket.value?.connected) {
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

// const handleReturn = () => {
//     cleanupSocket();
//     currentMode.value = 'coop';
// };

const codeManipulations = async (mode: modes) => {
    if (mode === "create") {
        console.log("Creating room...");

        try {
            const newSocket = initializeSocket();

            newSocket.on("connect", () => {
                newSocket.emit("join_room");
            });

            newSocket.on("room_created", (data) => {
                createdCoopId.value = data.roomId;
                createdCoopCode.value = data.code;
            });

            newSocket.on("lobby_update", (data) => {
                console.log("Lobby update:", data);
            });

        } catch (error) {
            console.error("Error creating room:", error);
        }
    } else {
        createdCoopCode.value = ""
    }
}

const joinRoom = async () => {
    try {
        console.log(roomCodeInput.value)

        const newSocket = initializeSocket();

        newSocket.on("connect", () => {
            newSocket.emit("join_existing_room", { code: roomCodeInput.value });
        });

        newSocket.on("room_joined", (data) => {
            console.log("Room joined:", data);
        });

        newSocket.on("room_changed", (data) => {
            console.log("room_changed:", data);
        });

    } catch (error) {
        console.error("Error joining room:", error);
    }
}

watch(currentMode, (newMode) => {
    changeQueryMode(newMode);
    codeManipulations(newMode);
})

onMounted(async () => {
    changeQueryMode(currentMode.value);
    codeManipulations(currentMode.value);
})

// onUnmounted(() => {
//     cleanupSocket();
// });
</script>