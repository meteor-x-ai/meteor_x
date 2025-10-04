import type {iCalculatedData, iUserInput} from "@/models/meteor-models.ts";
import {eWeatherType} from "@/enums/meteor-enums.ts";

const RADIUS_TIMES_IN_SECONDS = [1800, 3600, 7200]

const getZoomForRadius = (radiusMeters: number): number => {
    const zoom = 12 - Math.log2(radiusMeters / 1000);
    return Math.min(Math.max(5, zoom), 18);
}

const getRadiusOverTime = (kineticEnergy: number, angleCoefficient: number, weatherCoefficient: number) => {
    const k = 0.1;
    return RADIUS_TIMES_IN_SECONDS.map(t => {
        const radius = k * Math.pow(kineticEnergy, 1/5) * Math.pow(t, 2/5) * angleCoefficient * weatherCoefficient;
        return { radius, time: t };
    });
}

const computeCalculated = (u: iUserInput): iCalculatedData => {
    const v = u.speed * 1000;
    const m = u.mass;
    const E = 0.5 * m * v ** 2;

    const thetaRad = (u.angle * Math.PI) / 180;
    const angleCoefficient = Math.max(0.3, Math.sin(thetaRad));

    const weatherMap: Record<eWeatherType, number> = {
        [eWeatherType.CLEAR]: 1.0,
        [eWeatherType.SNOW]: 0.99,
        [eWeatherType.RAIN]: 0.97,
        [eWeatherType.STORM]: 0.95,
    };
    const weatherCoefficient = weatherMap[u.weather];

    const baseCraterRadius = 0.0015874 * Math.pow(E, 1/3) * angleCoefficient * weatherCoefficient;

    const radiusOverTime = getRadiusOverTime(E, angleCoefficient, weatherCoefficient);

    const surfaceCoefficient = 1.0;
    const craterDepth = 0.2 * baseCraterRadius * surfaceCoefficient;

    return {
        kineticEnergy: E,
        baseCraterRadius,
        craterDepth,
        angleCoefficient,
        weatherCoefficient,
        radiusOverTime
    };
}

export {
    getZoomForRadius,
    computeCalculated,
    RADIUS_TIMES_IN_SECONDS
}