import type {iCalculatedData, iUserInput} from "@/models/meteor-models.ts";
import {eWeatherType} from "@/enums/meteor-enums.ts";

const getZoomForRadius = (radiusMeters: number): number => {
    const zoom = 16 - Math.log2(radiusMeters / 1000);
    return Math.min(Math.max(5, zoom), 18);
}

const computeCalculated = (u: iUserInput): iCalculatedData => {
    // km/s -> m/s
    const v = u.speed * 1000;
    // kg
    const m = u.mass;
    const kineticEnergy = 0.5 * m * v ** 2;

    const thetaRad = (u.angle * Math.PI) / 180;
    const angleCoefficient = Math.max(0.3, Math.sin(thetaRad));

    const weatherMap: Record<eWeatherType, number> = {
        [eWeatherType.CLEAR]: 1.0,
        [eWeatherType.SNOW]: 0.99,
        [eWeatherType.RAIN]: 0.97,
        [eWeatherType.STORM]: 0.95,
    };
    const weatherCoefficient = weatherMap[u.weather];

    const a = 0.0015874010519682004;
    const baseCraterRadius = a * Math.pow(kineticEnergy, 1/3) * angleCoefficient * weatherCoefficient;

    const craterDepth = 0.2 * baseCraterRadius;

    return { kineticEnergy, baseCraterRadius, craterDepth, angleCoefficient, weatherCoefficient };
}

export {
    getZoomForRadius,
    computeCalculated,
}