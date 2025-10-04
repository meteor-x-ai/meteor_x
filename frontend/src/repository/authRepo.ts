import {BACK_PATH_API} from "@/repository/backendPath.ts";

const authRepo = {
    async login(username: string, password: string): Promise<string | null> {
        try {
            const res = await fetch(`${BACK_PATH_API}/login`, {
                method: "POST",
                body: JSON.stringify({ username, password }),
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            });

            if (res.status === 200) {
                return (await res.json()).userId;
            }

            return null;
        } catch (error) {
            console.error(error);
            return null;
        }
    },

    async signup(username: string, password: string): Promise<string | null> {
        try {
            const res = await fetch(`${BACK_PATH_API}/signup`, {
                method: "POST",
                body: JSON.stringify({ username, password }),
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            })

            if (res.status === 200) {
                return (await res.json()).userId;
            }

            return null;
        } catch (error) {
            console.error(error);
            return null;
        }
    },

    async auth(): Promise<string | null> {
        try {
            const res = await fetch(`${BACK_PATH_API}/auth`, {
                method: "GET",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
            })

            if (res.status === 200) {
                return (await res.json()).userId;
            }

            return null;
        } catch (error) {
            console.error(error);
            return null;
        }
    }
};

export default authRepo;