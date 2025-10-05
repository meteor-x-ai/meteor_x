<template>
    <teleport to="body" v-if="!pendingAuth">
        <div
            v-if="currentUser?.username"
            class="login--info--container"
        >
            {{currentUser.username}}
        </div>
        <router-link
            v-else
            class="login--info--container unauthenticated"
            :to="{
                        name: 'login-page',
                        query: {
                            redirect: 'game'
                        }
                    }"
        >
            unauthenticated
        </router-link>
    </teleport>

    <div class="game--mode__page">
        <div class="game--mode__button--container">
            <span class="game--mode__title">Save Planet</span>
            <template v-if="currentMode === eModes.SELECT">
                <div class="button__container">
                    <router-link :to="{name: 'game-solo-mode'}" class="game--mode__button">Solo</router-link>
                    <button
                        class="game--mode__button"
                        @click="currentMode = eModes.COOP"
                        :disabled="!currentUser"
                    >
                        Coop
                    </button>
                </div>
            </template>
            <template v-else-if="currentMode === eModes.COOP">
                <input
                    type="text"
                    maxlength="4"
                    class="game--mode__input"
                    placeholder="Input room code..."
                    v-model="roomCodeInput"
                    @input="roomCodeInput = roomCodeInput.replace(/\D/g, '')"
                >
                <div class="button__container">
                    <button
                        class="game--mode__button"
                        @click="currentMode = eModes.SELECT"
                    >
                        Return
                    </button>
                    <button
                        class="game--mode__button"
                        @click="joinRoom"
                        :disabled="roomCodeInput.length !== 4"
                    >
                        Join
                    </button>
                    <button
                        class="game--mode__button"
                        @click="currentMode = eModes.CREATE"
                    >
                        Create
                    </button>
                </div>
            </template>
            <template v-else-if="currentMode === eModes.CREATE">
                <div v-if="roomInfo.code">Code: {{roomInfo.code}}</div>
                <span v-else>Code: <span class="loading--animation">loading...</span></span>
                <span v-if="roomInfo.code">Users ↓</span>
                <div
                    class="user--container"
                    :class="{'current': user.id === currentUser?.id}"
                    @click="removeUser(user.id)"
                    v-for="(user, i) in users"
                >
                    {{cards[i]}}: {{i+1}}.{{user.username}} <span
                    v-if="removingUserId === user.id"
                    class="loading--animation"
                >
                    removing...
                </span>
                </div>
                <div class="button__container">
                    <button
                        class="game--mode__button"
                        @click="closeRoom"
                    >
                        Cancel
                    </button>
                    <button
                        class="game--mode__button"
                        v-if="roomInfo.id"
                        @click="startGame"
                        :disabled="users.length !== 4"
                    >
                        Start
                    </button>
                </div>
            </template>
            <template v-else-if="currentMode === eModes.ROOM">
                <span>Code: {{roomInfo.code}}</span>
                <span>Users ↓</span>
                <div
                    class="user--container user--container--room"
                    :class="{'current': user.id === currentUser?.id}"
                    v-for="(user, i) in users"
                >
                    {{cards[i]}}: {{i+1}}.{{user.username}}
                </div>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-mode-page.css"
import {onBeforeMount, onUnmounted, reactive, ref, watch} from "vue";
import {useRoute, useRouter} from "vue-router";
import {eGameCardNames, eGameRoomChangedTypes, eModes, eSocketEvent} from "@/enums/gameEnums.ts";
import authRepo from "@/repository/authRepo.ts";
import type {iUser} from "@/models/user-models.ts";
import {useSocketStore} from "@/services/wsService.ts";
import type {Socket} from "socket.io-client";

const route = useRoute();
const router = useRouter();
const socketStore = useSocketStore()

const cards = Object.values(eGameCardNames)

const users = ref<iUser[]>([])
const socket = ref<Socket | null>(null)
const pendingAuth = ref<boolean>(true);
const currentMode = ref<eModes>(eModes.SELECT);
const currentUser = ref<iUser | null>(null);
const roomCodeInput = ref<string>("");
const removingUserId = ref<string>("");

const roomInfo = reactive<{ code: string, id: string }>({code: "", id: ""})

const changeQueryMode = async () => {
    const newQuery = { ...route.query };

    if (currentMode.value === eModes.SELECT) {
        delete newQuery.mode;
    } else {
        newQuery.mode = currentMode.value;
    }
    if (currentMode.value !== eModes.ROOM && currentMode.value !== eModes.CREATE) {
        delete newQuery.code;
    }

    await router.replace({
        path: route.path,
        query: newQuery
    })
}

const initializeSocket = () => {
    if (!socketStore.socket?.connected) socketStore.connect()
    socket.value = socketStore.socket

    if (socket.value === null) return

    socket.value.on(eSocketEvent.ROOM_CHANGED, (data) => {
        switch (data.type) {
            case eGameRoomChangedTypes.USER_ADDED:
                if (data.userId === currentUser.value?.id) return;
                users.value.push({
                    id: data.userId,
                    username: data.username
                });
                break;
            case eGameRoomChangedTypes.USER_REMOVED:
                if (data.userId === currentUser.value?.id) {
                    socketStore.disconnect()
                    currentMode.value = eModes.COOP;
                    users.value = []
                    break;
                }
                if (removingUserId.value) removingUserId.value = '';
                users.value = users.value.filter(u => u.id !== data.userId);
                break;
            default:
                console.warn("Room changed unsupported type:", data)
        }
    });

    socket.value.on(eSocketEvent.GAME_REDIRECT, async (data) => {
        if (data) {
            await router.push({
                name: 'game-coop-mode',
                params: {
                    roomCode: roomInfo.code
                }
            })
        }
    })

    socket.value.on(eSocketEvent.ROOM_CLOSED, () =>{
        socketStore.socket?.disconnect();
        roomInfo.id = ""
        currentMode.value = eModes.COOP;
    })
};

const codeManipulations = async () => {
    if (currentMode.value === eModes.CREATE && !socketStore.socket) {
        if (false) {
            //TODO connect by code from query
        } else {
            try {
                initializeSocket()
                if (socket.value === null) return

                socket.value.on(eSocketEvent.CONNECT, () => {
                    socket.value!.emit(eSocketEvent.JOIN_ROOM);
                });

                socket.value.on(eSocketEvent.ROOM_CREATED, async (data) => {
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

            } catch (error) {
                console.error("Error creating room:", error);
            }
        }
    } else if (currentMode.value === eModes.ROOM) {
        return
    }
    else {
        roomInfo.code = ""
    }
}

const joinRoom = async () => {
    try {
        initializeSocket()
        if (socket.value === null) return

        socket.value.on(eSocketEvent.CONNECT, () => {
            socket.value!.emit(eSocketEvent.JOIN_EXISTING_ROOM, { code: roomCodeInput.value });
        });

        socket.value.on(eSocketEvent.ROOM_JOINED, (data) => {
            users.value = data.users;
            roomInfo.id = data.roomId;
            roomInfo.code = data.code;
            currentMode.value = eModes.ROOM;
        });

    } catch (error) {
        console.error("Error joining room:", error);
    }
}

const removeUser = (targetUserId: string) => {
    if (socket.value?.connected && targetUserId !== currentUser.value?.id) {
        removingUserId.value = targetUserId;
        socket.value.emit(eSocketEvent.REMOVE_USER, {
            targetUserId,
            roomId: roomInfo.id,
        });
    }
}

const startGame = async () => {
    if (!socket.value?.connected) return;
    socket.value.emit(eSocketEvent.START_GAME, { roomId: roomInfo.id });
}

const closeRoom = () => {
    if (socket.value?.connected) {
        socket.value.emit(eSocketEvent.CLOSE_ROOM, { roomId: roomInfo.id });
    }
}

watch(currentMode, async () => {
    await changeQueryMode();
    await codeManipulations();
})

onBeforeMount(async () => {
    currentUser.value = await authRepo.auth();

    if (currentUser.value && (route.query.mode === eModes.COOP || route.query.mode === eModes.CREATE)) {
        currentMode.value = route.query.mode as eModes;
    }

    await changeQueryMode();
    await codeManipulations();

    pendingAuth.value = false
})

onUnmounted(() => {
    socket.value = null
});
</script>