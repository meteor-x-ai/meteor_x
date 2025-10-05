<template>
    <div class="map--view" id="map">

        <PopupAI
            v-if="showAiPopup"
            :meteor-value="meteor"
            :close-call-back="() => showAiPopup = false"
            @apply="(newMeteor) => meteor = newMeteor"
        />

        <teleport to="body">
            <div v-if="!watchMode" class="meteor--container">
                <div class="meteor--info__container">
                    <div class="meteor--info__input--container" >
                        <label class="meteor--info__input--label" >Mass <span class="meteor--info__input--label--text">kg</span></label>
                        <input
                            placeholder="Input mass"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.mass"
                            @input="validateInput('mass')"
                            @keydown="preventNegative"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Speed <span class="meteor--info__input--label--text">km/s</span></label>
                        <input
                            placeholder="Input speed"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.speed"
                            @input="validateInput('speed')"
                            @keydown="preventNegative"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Angle  <span class="meteor--info__input--label--text">1-180</span></label>
                        <input
                            placeholder="Input angle"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.angle"
                            @input="validateInput('angle')"
                            @keydown="preventNegative"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Year</label>
                        <input
                            placeholder="Input year"
                            type="number"
                            class="meteor--info__input"
                            v-model="meteor.year"
                            @input="() => validateInput ('year')"
                            @keydown="preventNegative"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Type</label>
                        <select class="meteor--info__input" v-model="meteor.type">
                            <option v-for="type in meteorTypes" :value="type">
                                {{type.replace(/-/g, " ")}}
                            </option>
                        </select>
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Material</label>
                        <select class="meteor--info__input" v-model="meteor.material">
                            <option v-for="type in meteorMaterial" :value="type">
                                {{type}}
                            </option>
                        </select>
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Weather</label>
                        <select class="meteor--info__input" v-model="meteor.weather">
                            <option v-for="type in meteorWeather" :value="type">
                                {{type}}
                            </option>
                        </select>
                    </div>
                    <button :disabled="!canMeteor" @click="meteorClick" class="meteor--info__button">
                        Meteor!
                    </button>
                </div>
            </div>
        </teleport>

        <teleport to="body">
            <div v-if="!watchMode" class="meteor--tools__container">
                <router-link :to="{name: 'main-page'}" class="meteor--info__link">
                    <img class="meteor--info__link--img" src="/home.svg" alt=""> Menu
                </router-link>
                <div class="meteor--info__link-glow-wrapper">
                    <button
                        class="meteor--info__link meteor--info__link--animation"
                        @click="showAiPopup = true"
                    >
                        <img class="meteor--info__link--img" src="/ai.svg" alt="AI"> Generate
                    </button>
                </div>
                <button
                    class="meteor--info__link"
                    @click="setWatchMode"
                >
                    <img class="meteor--info__link--img" src="/watch.svg" alt=""> Watch Mode
                </button>
                <button
                    class="meteor--info__link"
                    @click="makeScreenshot"
                >
                    <img class="meteor--info__link--img" src="/screenshot.svg" alt=""> Screenshot
                </button>
                <button
                    class="meteor--info__link"
                    @click="clearCirclesAndTarget"
                >
                    <img class="meteor--info__link--img" src="/clear.svg" alt=""> Clear
                </button>
                <button
                    class="meteor--info__link"
                    @click="zoomFullScreen"
                >
                    <img class="meteor--info__link--img" src="/zoom.svg" alt=""> Zoom
                </button>
                <button
                    class="meteor--info__link"
                    @click="moveToUserLocation"
                >
                    <img class="meteor--info__link--img" src="/user-location.svg" alt=""> Your Location
                </button>
            </div>
        </teleport>

        <teleport to="body">
            <div class="meteor--active__settings" v-if="calculatedData">
                <button
                    v-for="step in calculatedData?.radiusOverTime"
                    :key="step.time"
                    @click="showRadius(step.time)"
                    class="meteor--info__link"
                    :class="{ 'no-active': activeRadiusTime && activeRadiusTime !== step.time }"
                >
                    {{ (step.time / 60) }} min
                </button>
                <button @click="showAllRadii" class="meteor--info__link">
                    Show All
                </button>
            </div>
        </teleport>

        <teleport to="body">
            <div v-if="showMap" class="minimap--container">
                <span>Mini map</span>
                <div id="miniMap"></div>
            </div>
        </teleport>

    </div>
</template>

<script setup lang="ts">
import L from "leaflet"
import {computed, nextTick, onMounted, ref, watch} from "vue";
import "@/css/map-page.css";
import {eMeteorMaterial, eMeteorType, eWeatherType} from "@/enums/meteor-enums.ts";
import type {iCalculatedData, iMeteor} from "@/models/meteor-models.ts";
import {computeCalculated, getZoomForRadius} from "@/services/meteorMathService.ts";
import PopupAI from "@components/PopupAI.vue";

const SETTINGS_ZOOM_ANIMATION_DURATION: number = 1.5
const SETTINGS_DEFAULT_ZOOM_COUNT: number = 5
const SETTINGS_DEFAULT_LATITUDE: L.LatLng = new L.LatLng(40, -100);

const map = ref<L.Map | null>(null)
const miniMap = ref<L.Map | null>(null)
const miniBoundsRect = ref<L.Rectangle | null>(null);
const marker = ref<L.Marker | null>(null)
const circles: L.Circle[] = []
const calculatedData = ref<iCalculatedData | null>(null)
const activeRadiusTime = ref<number | null>(null)

const watchMode = ref<boolean>(false)
const showAiPopup = ref<boolean>(false)
const currentZoom = ref<number>(SETTINGS_DEFAULT_ZOOM_COUNT)
const firstOpenWatchMode = ref<boolean>(true)

const meteor = ref<iMeteor>({
    mass: 1e7,
    speed: 20,
    angle: 45,
    year: 2025,
    type: eMeteorType.STONY,
    material: eMeteorMaterial.IRON,
    weather: eWeatherType.CLEAR,
    latitude: 40,
    longitude: -100
})

type NumericField = 'mass' | 'speed' | 'angle' | 'year';

function validateInput(field: NumericField) {
    const value = meteor.value[field];
    let s = String(value ?? '');
    s = s.replace(/\D/g, '');
    s = s.replace(/^0+/, '');
    meteor.value[field] = s ? Number(s) : 0;
}

function preventNegative(e: KeyboardEvent) {
    if (e.key === '-') e.preventDefault();
}

const showMap = computed(() => currentZoom.value >= 11)
const canMeteor = computed(() =>
    meteor.value.mass !== null && Number(meteor.value.mass) >= 0 &&
    meteor.value.speed !== null && Number(meteor.value.speed) >= 0 &&
    meteor.value.angle !== null && Number(meteor.value.angle) >= 0 &&
    meteor.value.type !== null &&
    meteor.value.material !== null &&
    meteor.value.weather !== null &&
    meteor.value.year >= 1 &&
    marker.value !== null &&
    map.value !== null
)

const meteorTypes = Object.values(eMeteorType)
const meteorMaterial = Object.values(eMeteorMaterial)
const meteorWeather = Object.values(eWeatherType)
const customIcon = L.icon({
    iconUrl: '/target.svg',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});

const zoomFullScreen = () => {
    if (!map.value) return;

    if (marker.value) {
        const latlng = marker.value.getLatLng();
        map.value.flyTo(latlng, SETTINGS_DEFAULT_ZOOM_COUNT, {
            animate: true,
            duration: SETTINGS_ZOOM_ANIMATION_DURATION
        });
    } else {
        const center = map.value.getCenter();
        map.value.flyTo(center, 6, {
            animate: true,
            duration: SETTINGS_ZOOM_ANIMATION_DURATION
        });
    }
}

const moveToUserLocation = () => {
    if (!map.value) return;

    map.value.locate({ setView: false, maxZoom: SETTINGS_DEFAULT_ZOOM_COUNT})
        .on("locationfound", (e: L.LocationEvent) => {
            map.value!.flyTo(e.latlng, 13, {
                animate: true,
                duration: SETTINGS_ZOOM_ANIMATION_DURATION
            });
        })
        .on("locationerror", () => {
            map.value!.flyTo(SETTINGS_DEFAULT_LATITUDE, SETTINGS_DEFAULT_ZOOM_COUNT, {
                animate: true,
                duration: SETTINGS_ZOOM_ANIMATION_DURATION
            });
        });
}

const clearCircles = () => {
    circles.forEach(circle => map.value!.removeLayer(circle));
    circles.length = 0;
}

const clearCirclesAndTarget = () => {
    clearCircles()
    calculatedData.value = null
    if (marker.value) {
        marker.value.remove()
        marker.value = null
    }
}

const meteorClick = async () => {
    clearCircles();
    activeRadiusTime.value = null
    calculatedData.value = computeCalculated(meteor.value)

    if (calculatedData.value === null) return;

    const craterRadius = calculatedData.value.baseCraterRadius

    const latlng = marker.value?.getLatLng();
    const numCircles = 3;
    if (!latlng || !map.value) return;

    const zoom = getZoomForRadius(craterRadius * numCircles);

    if (marker.value && map.value) {
        const latlng = marker.value.getLatLng();
        map.value.flyTo(latlng, zoom, {
            animate: true,
            duration: SETTINGS_ZOOM_ANIMATION_DURATION
        });
    }

    setTimeout(() => {
        const radii = calculatedData.value!.radiusOverTime.map(r => r.radius);

        radii.forEach(radius => {
            const circle = L.circle([latlng.lat, latlng.lng], {
                radius: radius,
                color: 'red',
                fillColor: 'orange',
                fillOpacity: 0.2,
                weight: 2,
                dashArray: '5, 5'
            }).addTo(map.value as L.Map);
            circles.push(circle);
        });
        activeRadiusTime.value = null
    }, SETTINGS_ZOOM_ANIMATION_DURATION * 1000);
}

const setWatchMode = () => {
    if (firstOpenWatchMode.value) {
        firstOpenWatchMode.value = false;
        window.alert("Press Escape to exit watch mode");
    }
    watchMode.value = true;
}

const makeScreenshot = () => {

}

const setupMiniBounds = () => {
    if (!miniMap.value) return;

    const bounds = map.value!.getBounds();

    if (!miniBoundsRect.value) {
        miniBoundsRect.value = L.rectangle(bounds, {
            color: "red",
            weight: 2,
            fillOpacity: 0.1,
            dashArray: "5,5"
        }).addTo(miniMap.value as L.Map);
    } else {
        miniBoundsRect.value.setBounds(bounds);
    }
}

const showRadius = (timeSec: number) => {
    clearCircles();
    if (!marker.value || !map.value || !calculatedData.value) return;

    activeRadiusTime.value = timeSec;
    const step = calculatedData.value.radiusOverTime.find(r => r.time === timeSec);
    if (!step) return;

    const latlng = marker.value.getLatLng();
    const circle = L.circle([latlng.lat, latlng.lng], {
        radius: step.radius,
        color: 'red',
        fillColor: 'orange',
        fillOpacity: 0.2,
        weight: 2,
        dashArray: '5,5'
    }).addTo(map.value as L.Map);
    circles.push(circle);
};

const showAllRadii = () => {
    clearCircles();
    if (!marker.value || !map.value || !calculatedData.value) return;

    activeRadiusTime.value = null
    const latlng = marker.value.getLatLng();

    calculatedData.value.radiusOverTime.forEach(step => {
        const circle = L.circle([latlng.lat, latlng.lng], {
            radius: step.radius,
            color: 'red',
            fillColor: 'orange',
            fillOpacity: 0.2,
            weight: 2,
            dashArray: '5,5'
        }).addTo(map.value as L.Map);
        circles.push(circle);
    });
};

watch(showMap, async (newValue) => {
    if (newValue) {
        await nextTick(() => {
            if (!map.value) return;

            miniMap.value = L.map("miniMap", {
                zoomControl: false,
                attributionControl: false,
                dragging: false,
                scrollWheelZoom: false,
                doubleClickZoom: false,
                boxZoom: false,
                keyboard: false,
                tapHold: false,
                touchZoom: false
            }).setView(map.value!.getCenter(), 8);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "",
            }).addTo(miniMap.value as L.Map);

            miniMap.value.invalidateSize();

            setupMiniBounds()
        });
    } else {
        if (miniMap.value) {
            miniMap.value.remove();
            miniMap.value = null;
            miniBoundsRect.value = null;
        }
    }
})

onMounted(() => {
    map.value = L.map("map", {
        attributionControl: false,
    }).setView(SETTINGS_DEFAULT_LATITUDE, SETTINGS_DEFAULT_ZOOM_COUNT);

    if (map.value === null) return;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "",
    }).addTo(map.value as L.Map);

    map.value.on("click", (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;

        if (marker.value) {
            marker.value.setLatLng([lat, lng]);
        } else {
            marker.value = L.marker([lat, lng], { icon: customIcon }).addTo(map.value as L.Map);
        }
    });

    map.value.on("zoom", () => {
        if (map!.value) {
            currentZoom.value = map.value.getZoom()
        }
    });

    map.value.on("move", () => {
        if (miniMap.value) {
            const center = map.value!.getCenter();
            miniMap.value.setView(center, miniMap.value.getZoom(), {
                animate: false,
            });
        }
    });

    map.value!.on("move zoom", () => {
        setupMiniBounds()
    });
});

onMounted(() => {
    addEventListener("keydown", (e: KeyboardEvent) => {
        if (e.key === "Escape") {
            if (watchMode.value) {
                watchMode.value = false;
            }
        }
    })
})
</script>