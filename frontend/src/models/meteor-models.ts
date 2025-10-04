import {eMeteorMaterial, eMeteorType, type eWeatherType} from "@/enums/meteor-enums.ts";

export interface iUserInput {
    year: number;
    mass: number;
    speed: number;
    angle: number;
    latitude: number;
    longitude: number;
    type: eMeteorType;
    weather: eWeatherType;
    material: eMeteorMaterial;
}

export interface iRadiusOverTime {
    radius: number;
    time: number;
}

export interface iCalculatedData {
    kineticEnergy: number;
    baseCraterRadius: number;
    craterDepth: number;
    angleCoefficient: number;
    weatherCoefficient: number;
    radiusOverTime: iRadiusOverTime[];
}