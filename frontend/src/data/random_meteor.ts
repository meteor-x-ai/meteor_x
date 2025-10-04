import { eMeteorType, eMeteorMaterial, eWeatherType } from "@/enums/meteor-enums";
import type { iMeteorPreset } from "@/models/meteor-models";

export type Material = "STONE" | "IRON" | "MIXED";
export type TypeKind = "STONY" | "IRON" | "STONY_IRON";
export type Weather = "CLEAR" | "RAIN" | "SNOW";

const DENSITY = { STONE: 3500, IRON: 7800, MIXED: 4900 } as const;

const REGIONS = [
    { name: "North America",   lat: [7, 83],    lon: [-168, -52] },
    { name: "South America",   lat: [-56, 13],  lon: [-82, -34] },
    { name: "Europe",          lat: [35, 71],   lon: [-10, 40] },
    { name: "Africa",          lat: [-35, 37],  lon: [-18, 52] },
    { name: "Asia",            lat: [6, 77],    lon: [26, 180] },
    { name: "Australia",       lat: [-44, -10], lon: [112, 154] },
    { name: "Antarctica",      lat: [-90, -60], lon: [-180, 180] },
] as const;

const rnd   = (min: number, max: number) => Math.random() * (max - min) + min;
const rndi  = (min: number, max: number) => Math.floor(rnd(min, max + 1));
const pick  = <T,>(a: readonly T[]) => a[rndi(0, a.length - 1)];

function pickMaterial(): { material: Material; type: TypeKind } {
    const p = Math.random();
    if (p < 0.85) return { material: "STONE", type: "STONY" };
    if (p < 0.97) return { material: "IRON",  type: "IRON"  };
    return { material: "MIXED", type: "STONY_IRON" };
}

function randomGeo() {
    const ocean = Math.random() < 0.71;
    if (ocean) {
        return { latitude: rnd(-80, 80), longitude: rnd(-180, 180), location: "Open Ocean" };
    }
    const r = pick(REGIONS);
    return { latitude: rnd(r.lat[0], r.lat[1]), longitude: rnd(r.lon[0], r.lon[1]), location: r.name };
}

function randomWeather(location: string): Weather {
    const latBiasSnow = (loc: string) => loc === "Antarctica";
    const p = Math.random();
    if (latBiasSnow(location)) {
        if (p < 0.6) return "SNOW";
        return p < 0.8 ? "CLEAR" : "RAIN";
    }
    if (location === "Open Ocean") return p < 0.7 ? "CLEAR" : p < 0.9 ? "RAIN" : "SNOW";
    return p < 0.6 ? "CLEAR" : p < 0.9 ? "RAIN" : "SNOW";
}

function randomSpeed() {
    const mean = 20, sigma = 4.5;
    const gaussian = () => {
        const u = 1 - Math.random(), v = 1 - Math.random();
        return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    };
    const v = mean + sigma * gaussian();
    return Math.min(Math.max(v, 12), 30);
}

const randomAngle = () => Math.round(rnd(12, 68));

function randomYear() {
    const now = new Date().getFullYear();
    return Math.random() < 0.7 ? rndi(-3000, now) : rndi(-2500000000, -1000000);
}

function randomDiameter() {
    const base = Math.exp(rnd(Math.log(0.2), Math.log(200)));
    const rare = Math.random() < 0.02 ? rnd(300, 20000) : 0;
    return Math.round((base + rare) * 100) / 100;
}

function massFrom(diameterM: number, density: number) {
    const r = diameterM / 2;
    const volume = (4 / 3) * Math.PI * r ** 3;
    return volume * density;
}

function estimateCraterDiameter(massKg: number, speedKmS: number, angleDeg: number, material: Material) {
    const speedMS = speedKmS * 1000;
    const energyJ = 0.5 * massKg * speedMS * speedMS;
    const energyMt = energyJ / 4.184e15;

    const likelyAirburst = angleDeg < 20 || massKg < 1.5e7;
    if (likelyAirburst) return 0;

    const matK = material === "IRON" ? 1.25 : material === "MIXED" ? 1.1 : 1.0;
    const D_km = 0.01 * Math.pow(Math.max(energyMt, 0.001), 1 / 3.4) * matK;
    const meters = Math.round(D_km * 1000);

    return Math.max(0, Math.min(meters, 500_000));
}

function convertType(internalType: TypeKind): eMeteorType {
    switch (internalType) {
        case "STONY": return eMeteorType.STONY;
        case "IRON": return eMeteorType.IRON;
        case "STONY_IRON": return eMeteorType.STONY_IRON;
        default: return eMeteorType.STONY;
    }
}

function convertMaterial(internalMaterial: Material): eMeteorMaterial {
    switch (internalMaterial) {
        case "STONE": return eMeteorMaterial.STONE;
        case "IRON": return eMeteorMaterial.IRON;
        case "MIXED": return eMeteorMaterial.MIXED;
        default: return eMeteorMaterial.STONE;
    }
}

function convertWeather(internalWeather: Weather): eWeatherType {
    switch (internalWeather) {
        case "CLEAR": return eWeatherType.CLEAR;
        case "RAIN": return eWeatherType.RAIN;
        case "SNOW": return eWeatherType.SNOW;
        default: return eWeatherType.CLEAR;
    }
}

export function generateRandomMeteor(): iMeteorPreset {
    const { material, type } = pickMaterial();
    const { latitude, longitude, location } = randomGeo();
    const speed = Math.round(randomSpeed() * 100) / 100;
    const angle = randomAngle();
    const diameter = randomDiameter();
    const mass = massFrom(diameter, DENSITY[material]);
    const craterDiameter = estimateCraterDiameter(mass, speed, angle, material);
    const year = randomYear();
    const weather = randomWeather(location);
    const id = Math.random().toString(36).slice(2, 7).toUpperCase();

    const name = `Random Meteor ${id}`;
    const description =
        craterDiameter > 0 ? "Probable ground impact with visible crater" : "Likely high-altitude airburst (no crater)";

    return {
        name,
        year,
        mass: Math.round(mass),
        speed,
        angle,
        latitude: Math.round(latitude * 1000) / 1000,
        longitude: Math.round(longitude * 1000) / 1000,
        location,
        type: convertType(type),
        material: convertMaterial(material),
        weather: convertWeather(weather),
        diameter: Math.round(diameter * 100) / 100,
        craterDiameter,
        description,
    };
}