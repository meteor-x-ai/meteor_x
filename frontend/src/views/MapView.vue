<template>
    <div class="map--view" id="map">

        <teleport to="body">
            <div v-if="!watchMode" class="meteor--container">
                <div class="meteor--info__container">
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Mass <span class="meteor--info__input--label--text">10-1000000000</span>kg</label>
                        <input
                            placeholder="Input mass"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.mass"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Speed <span class="meteor--info__input--label--text">5-70</span>km/s</label>
                        <input
                            placeholder="Input speed"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.speed"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Angle  <span class="meteor--info__input--label--text">1-180</span></label>
                        <input
                            placeholder="Input angle"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.angle"
                        >
                    </div>
                    <div class="meteor--info__input--container">
                        <label class="meteor--info__input--label">Year</label>
                        <input
                            placeholder="Input year"
                            type="number"
                            class="meteor--info__input"
                            v-model.number="meteor.year"
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
                <button @click="setWatchMode" class="meteor--info__link">
                    <img class="meteor--info__link--img" src="/watch.svg" alt=""> Watch Mode
                </button>
                <button @click="makeScreenshot" class="meteor--info__link">
                    <img class="meteor--info__link--img" src="/screenshot.svg" alt=""> Screenshot
                </button>
                <button @click="clearCirclesAndTarget" class="meteor--info__link">
                    <img class="meteor--info__link--img" src="/clear.svg" alt=""> Clear
                </button>
                <button @click="zoomFullScreen" class="meteor--info__link">
                    <img class="meteor--info__link--img" src="/zoom.svg" alt=""> Zoom
                </button>
                <button @click="moveToUserLocation" class="meteor--info__link">
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
import {computed, nextTick, onMounted, reactive, ref, watch} from "vue";
import "@/css/map-page.css";
import {eMeteorMaterial, eMeteorType, eWeatherType} from "@/enums/meteor-enums.ts";
import type {iCalculatedData, iUserInput} from "@/models/meteor-models.ts";
import {computeCalculated, getZoomForRadius} from "@/services/meteorMathService.ts";

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
const firstOpenWatchMode = ref<boolean>(true)
const currentZoom = ref<number>(SETTINGS_DEFAULT_ZOOM_COUNT)
const meteor = reactive<iUserInput>({
    //user input
    mass: 1e7,
    speed: 20,
    angle: 45,
    year: 2025,
    type: eMeteorType.STONY,
    material: eMeteorMaterial.IRON,
    weather: eWeatherType.CLEAR,
    //target location
    latitude: 40,
    longitude: -100
});
const showMap = computed(() => currentZoom.value >= 8)
const canMeteor = computed(() =>
    meteor.mass !== null && Number(meteor.mass) > 0 &&
    meteor.speed !== null && Number(meteor.speed) > 0 &&
    meteor.angle !== null && Number(meteor.angle) > 0 &&
    meteor.type !== null &&
    meteor.material !== null &&
    meteor.weather !== null &&
    meteor.year >= 1 &&
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
    calculatedData.value = computeCalculated(meteor)

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
            }).setView(map.value!.getCenter(), SETTINGS_DEFAULT_ZOOM_COUNT);

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