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

export interface iCalculatedData {
    craterDepth: number;
    kineticEnergy: number;
    baseCraterRadius: number;
    angleCoefficient: number;
    weatherCoefficient: number;
}