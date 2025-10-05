import { defineStore } from "pinia";
import { io, Socket } from "socket.io-client";
import { BACK_PATH_WS } from "@/repository/backendPath";
import {eSocketEvent} from "@/enums/gameEnums.ts";

export const useSocketStore = defineStore("socket", {
    state: () => ({
        socket: null as Socket | null,
        connected: false,
    }),
    actions: {
        connect() {
            if (!this.socket) {
                this.socket = io(BACK_PATH_WS, {
                    withCredentials: true,
                    reconnection: true,
                    reconnectionAttempts: 5,
                    reconnectionDelay: 1000,
                });

                this.socket.on(eSocketEvent.CONNECT, () => {
                    this.connected = true;
                    console.log("[socket] connected:", this.socket?.id);
                });

                this.socket.on(eSocketEvent.DISCONNECTED, (reason) => {
                    this.connected = false;
                    console.warn("[socket] disconnected:", reason);
                });

                this.socket.on(eSocketEvent.CONNECT_ERROR, (err) => {
                    console.error("[socket] connection error:", err);
                });

                this.socket.on(eSocketEvent.ERROR, (err) => {
                    console.error("[socket] error:", err);
                });
            }
        },
        disconnect() {
            if (this.socket) {
                this.socket.removeAllListeners();
                this.socket.disconnect();
                this.socket = null;
                this.connected = false;
            }
        },
    },
});
