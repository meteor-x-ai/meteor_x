import type { iMeteorPreset } from "@/models/meteor-models";

export class CasualtyCalculator {
    private meteor: iMeteorPreset;

    constructor(meteor: iMeteorPreset) {
        this.meteor = meteor;
    }

    public estimateCasualties(): number {
        const { mass, speed, angle, location } = this.meteor;

        const speedMS = speed * 1000;
        const energy = 0.5 * mass * speedMS * speedMS;

        const angleFactor = Math.sin((angle * Math.PI) / 180);

        let casualties = (energy / 1e9) * angleFactor;

        if (location === "Open Ocean" || location === "Antarctica") {
            casualties *= 0.01;
        } else if (["Asia", "Europe", "Africa"].includes(location)) {
            casualties *= 1.3;
        }

        casualties = Math.max(0, Math.min(casualties, 8_000_000_000));

        return Math.round(casualties);
    }

    public getCasualtyReport(): string {
        const casualties = this.estimateCasualties();
        return `Орієнтовні жертви: ~${casualties.toLocaleString()} людей`;
    }
}