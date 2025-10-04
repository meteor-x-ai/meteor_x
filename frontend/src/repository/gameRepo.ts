import {backPath} from "@/repository/backendPath.ts";
import { io } from "socket.io-client"

const gameRepo = {
    async getCode() {
        try {
            const socket = io(`${backPath}`, {
                withCredentials: true,
                transports: ["websocket", "polling"]
            });

            const res = await fetch(`${backPath}/coop/create`, {
                method: "POST",
                credentials: "include"
            })

            const data = await res.json()

            socket.emit("join_lobby", { roomId: data.roomId })

            return {code: data.code, socket: socket}
        } catch (error) {
            console.error(error);
        }
    }
}

export default gameRepo