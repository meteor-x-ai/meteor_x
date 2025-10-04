import {BACK_PATH_API} from "@/repository/backendPath.ts";

const gameRepo = {
    async getCode() {
        try {
            const res = await fetch(`${BACK_PATH_API}/coop/create`, {
                method: "POST",
                credentials: "include"
            })

            return await res.json()
        } catch (error) {
            console.error(error);
        }
    }
}

export default gameRepo