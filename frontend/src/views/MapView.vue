<template>
  <div class="map--view" id="map">

    <teleport to="body">
      <div v-if="!watchMode" class="meteor--container">
        <div class="meteor--info__container">

          <div class="meteor--presets__container">
            <div class="meteor--info__input--container">
              <label class="meteor--info__input--label">Meteorites from history</label>
              <div class="dropdown">
                <button class="dropdown-btn" @click="toggleDropdown">
                  {{ selectedPresetName || "Choose meteorite" }}
                  <span class="arrow" :class="{ open: isDropdownOpen }">▼</span>
                </button>

                <ul v-if="isDropdownOpen" class="dropdown-menu">
                  <li
                      v-for="preset in meteorPresets"
                      :key="preset.name"
                      @click="selectPreset(preset)"
                      class="preset-item"
                  >
                    <div class="preset-name">{{ preset.name }}</div>
                    <div class="preset-casualties">Casualties: {{ calculateCasualties(preset).toLocaleString() }}</div>
                  </li>
                </ul>
              </div>
            </div>

            <button @click="generateRandomMeteorFunc" class="meteor--info__button random-meteor-btn">
              🎲 Random Meteorite
            </button>
          </div>

          <div v-if="estimatedCasualties > 0" class="casualties--display">
            <div class="casualties--number">⚠️ Estimated casualties: {{ estimatedCasualties.toLocaleString() }} people</div>
          </div>

          <div class="meteor--info__input--container" >
            <label class="meteor--info__input--label" >Mass <span class="meteor--info__input--label--text">kg</span></label>
            <input
                placeholder="Input mass"
                type="number"
                class="meteor--info__input"
                :class="{'container-error': errors.mass}"
                v-model.number="meteor.mass"
                @input="validateInput('mass', 0,)"
                @keydown="preventNegativeForMassSpeedAngle"
            >
            <div v-if="errors.mass" class="error">{{ errors.mass }}</div>
          </div>
          <div class="meteor--info__input--container">
            <label class="meteor--info__input--label">Speed <span class="meteor--info__input--label--text">km/s</span></label>
            <input
                placeholder="Input speed"
                type="number"
                class="meteor--info__input"
                :class="{'container-error': errors.speed}"
                v-model.number="meteor.speed"
                @input="validateInput('speed', 0)"
                @keydown="preventNegativeForMassSpeedAngle"
            >
          </div>
          <div class="meteor--info__input--container">
            <label class="meteor--info__input--label">Angle  <span class="meteor--info__input--label--text">1-180</span></label>
            <input
                placeholder="Input angle"
                type="number"
                class="meteor--info__input"
                :class="{'container-error': errors.angle}"
                v-model.number="meteor.angle"
                @input="validateInput('angle', 0)"
                @keydown="preventNegativeForMassSpeedAngle"
            >
          </div>
          <div class="meteor--info__input--container">
            <label class="meteor--info__input--label">Year</label>
            <input
                placeholder="Input year"
                type="number"
                class="meteor--info__input"
                :class="{'container-error': errors.year}"
                v-model="meteor.year"
                @input="() => validateInput ('year', -999999999, 2025)"
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
        <button @click="moveToUserLocation" class="meteor--info__link" :disabled="isLocating">
          <img class="meteor--info__link--img" src="/user-location.svg" alt="">
          {{ isLocating ? 'Location determination...' : 'Your Location' }}
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
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {computed, nextTick, onMounted, reactive, ref, watch} from "vue";
import "@/css/map-page.css";
import {eMeteorMaterial, eMeteorType, eWeatherType} from "@/enums/meteor-enums.ts";
import type {iCalculatedData, iUserInput} from "@/models/meteor-models.ts";
import {computeCalculated, getZoomForRadius} from "@/services/meteorMathService.ts";
import { meteorPresets } from "@/data/presets";
import { generateRandomMeteor } from "@/data/random_meteor";
import type { MeteorPreset } from "@/data/random_meteor";

class CasualtyCalculator {
  private meteor: MeteorPreset;

  constructor(meteor: MeteorPreset) {
    this.meteor = meteor;
  }

  public estimateCasualties(): number {
    const { mass, speed, angle, location } = this.meteor;

    const energy = 0.5 * mass * speed * speed;
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
}

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

const isDropdownOpen = ref<boolean>(false)
const selectedPresetName = ref<string>("")
const estimatedCasualties = ref<number>(0)

const watchMode = ref<boolean>(false)
const firstOpenWatchMode = ref<boolean>(true)
const currentZoom = ref<number>(SETTINGS_DEFAULT_ZOOM_COUNT)
const isLocating = ref<boolean>(false)

const meteor = reactive<iUserInput>({
  mass: 1e7,
  speed: 20,
  angle: 45,
  year: 2025,
  type: eMeteorType.STONY,
  material: eMeteorMaterial.IRON,
  weather: eWeatherType.CLEAR,
  latitude: 40,
  longitude: -100
});

type NumericField = 'mass' | 'speed' | 'angle' | 'year';

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
}

const calculateCasualties = (preset: MeteorPreset): number => {
  const calculator = new CasualtyCalculator(preset);
  return calculator.estimateCasualties();
}

const selectPreset = (preset: MeteorPreset) => {
  selectedPresetName.value = preset.name;
  isDropdownOpen.value = false;

  meteor.mass = Number(preset.mass) || 0;
  meteor.speed = Number(preset.speed) || 0;
  meteor.angle = Number(preset.angle) || 0;
  meteor.year = Number(preset.year) || 2025;

  switch(preset.type) {
    case "STONY": meteor.type = eMeteorType.STONY; break;
    case "IRON": meteor.type = eMeteorType.IRON; break;
    case "STONY_IRON": meteor.type = eMeteorType.STONY_IRON; break;
    default: meteor.type = eMeteorType.STONY;
  }

  switch(preset.material) {
    case "STONE": meteor.material = eMeteorMaterial.STONE; break;
    case "IRON": meteor.material = eMeteorMaterial.IRON; break;
    case "MIXED": meteor.material = eMeteorMaterial.MIXED; break;
    default: meteor.material = eMeteorMaterial.STONE;
  }

  switch(preset.weather) {
    case "CLEAR": meteor.weather = eWeatherType.CLEAR; break;
    case "RAIN": meteor.weather = eWeatherType.RAIN; break;
    case "SNOW": meteor.weather = eWeatherType.SNOW; break;
    default: meteor.weather = eWeatherType.CLEAR;
  }

  meteor.latitude = Number(preset.latitude) || 0;
  meteor.longitude = Number(preset.longitude) || 0;

  console.log('Updated meteor values:', {
    type: meteor.type,
    material: meteor.material,
    weather: meteor.weather
  });

  estimatedCasualties.value = calculateCasualties(preset);

  if (map.value) {
    const latlng = new L.LatLng(meteor.latitude, meteor.longitude);

    if (marker.value) {
      marker.value.setLatLng(latlng);
    } else {
      marker.value = L.marker(latlng, { icon: customIcon }).addTo(map.value);
    }

    map.value.flyTo(latlng, 6, {
      animate: true,
      duration: SETTINGS_ZOOM_ANIMATION_DURATION
    });
  }
}




const generateRandomMeteorFunc = () => {
  const randomMeteor = generateRandomMeteor();
  selectedPresetName.value = randomMeteor.name;

  meteor.mass = Number(randomMeteor.mass) || 0;
  meteor.speed = Number(randomMeteor.speed) || 0;
  meteor.angle = Number(randomMeteor.angle) || 0;
  meteor.year = Number(randomMeteor.year) || 2025;

  switch(randomMeteor.type) {
    case "STONY": meteor.type = eMeteorType.STONY; break;
    case "IRON": meteor.type = eMeteorType.IRON; break;
    case "STONY_IRON": meteor.type = eMeteorType.STONY_IRON; break;
    default: meteor.type = eMeteorType.STONY;
  }

  switch(randomMeteor.material) {
    case "STONE": meteor.material = eMeteorMaterial.STONE; break;
    case "IRON": meteor.material = eMeteorMaterial.IRON; break;
    case "MIXED": meteor.material = eMeteorMaterial.MIXED; break;
    default: meteor.material = eMeteorMaterial.STONE;
  }

  switch(randomMeteor.weather) {
    case "CLEAR": meteor.weather = eWeatherType.CLEAR; break;
    case "RAIN": meteor.weather = eWeatherType.RAIN; break;
    case "SNOW": meteor.weather = eWeatherType.SNOW; break;
    default: meteor.weather = eWeatherType.CLEAR;
  }

  meteor.latitude = Number(randomMeteor.latitude) || 0;
  meteor.longitude = Number(randomMeteor.longitude) || 0;

  console.log('Random coordinates:', meteor.latitude, meteor.longitude);
  console.log('Types:', typeof meteor.latitude, typeof meteor.longitude);

  estimatedCasualties.value = calculateCasualties(randomMeteor);

  if (map.value) {
    const latlng = new L.LatLng(meteor.latitude, meteor.longitude);

    if (marker.value) {
      marker.value.setLatLng(latlng);
    } else {
      marker.value = L.marker(latlng, { icon: customIcon }).addTo(map.value);
    }

    map.value.flyTo(latlng, 6, {
      animate: true,
      duration: SETTINGS_ZOOM_ANIMATION_DURATION
    });
  }
}

watch([() => meteor.mass, () => meteor.speed, () => meteor.angle, () => meteor.latitude, () => meteor.longitude], () => {
  if (meteor.mass && meteor.speed && meteor.angle) {
    const tempMeteor: MeteorPreset = {
      name: selectedPresetName.value || "Custom",
      year: meteor.year,
      mass: meteor.mass,
      speed: meteor.speed * 1000,
      angle: meteor.angle,
      latitude: meteor.latitude,
      longitude: meteor.longitude,
      location: "Custom Location",
      type: meteor.type,
      material: meteor.material,
      weather: meteor.weather,
      diameter: 0,
      craterDiameter: 0,
      description: "Custom meteor"
    };

    estimatedCasualties.value = calculateCasualties(tempMeteor);
  }
});

function validateInput(field: NumericField, min: number, max?: number) {
  const value = meteor[field];
  let s = String(value ?? '');

  if (field === 'year') {
    s = s.replace(/[^\d-]/g, '');
    if (s.includes('-')) {
      const parts = s.split('-');
      s = '-' + parts.filter(p => p).join('');
    }
  } else {
    s = s.replace(/\D/g, '');
    s = s.replace(/^0+/, '');
  }

  meteor[field] = s ? Number(s) : 0;

  if (field !== 'year' && meteor[field] < min) {
    errors[field] = `Minimum value ${min}`;
  } else if (field === 'year' && meteor[field] < min) {
    errors[field] = `Minimum value ${min}`;
  } else if (max !== undefined && meteor[field] > max) {
    errors[field] = `Maximum value ${max}`;
  } else {
    errors[field] = '';
  }
}

function preventNegativeForMassSpeedAngle(e: KeyboardEvent) {
  if (e.key === '-') e.preventDefault();
}

const errors = reactive<Record<'mass'|'speed'|'angle'|'year', string>>({
  mass: "",
  speed: "",
  angle: "",
  year: ""
});

const canMeteor = computed(() => {
  const checks = {
    mass: meteor.mass !== null && Number(meteor.mass) >= 0,
    speed: meteor.speed !== null && Number(meteor.speed) >= 0,
    angle: meteor.angle !== null && Number(meteor.angle) >= 0,
    type: meteor.type !== null,
    material: meteor.material !== null,
    weather: meteor.weather !== null,
    year: meteor.year !== null && meteor.year !== undefined,
    latitude: meteor.latitude !== null && meteor.latitude !== undefined,
    longitude: meteor.longitude !== null && meteor.longitude !== undefined,
    latRange: meteor.latitude >= -90 && meteor.latitude <= 90,
    lngRange: meteor.longitude >= -180 && meteor.longitude <= 180,
    mapExists: map.value !== null
  };

  console.log('canMeteor checks:', checks);
  console.log('meteor object:', meteor);

  return Object.values(checks).every(check => check);
})

const showMap = computed(() => currentZoom.value >= 8)

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
  if (!map.value || isLocating.value) return;

  isLocating.value = true;

  if (!navigator.geolocation) {
    console.error('Geolocation is not supported by this browser');
    alert('Your browser does not support location detection');
    isLocating.value = false;
    return;
  }

  const options = {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 300000
  };

  navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const userLocation = new L.LatLng(latitude, longitude);

        console.log(`Found location: ${latitude}, ${longitude}`);

        if (map.value) {
          map.value.flyTo(userLocation, 13, {
            animate: true,
            duration: SETTINGS_ZOOM_ANIMATION_DURATION
          });
        }

        isLocating.value = false;
      },
      (error) => {
        console.error('Error getting geolocation:', error);

        let errorMessage = '';
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Access to geolocation is prohibited. Please allow access in your browser settings.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'No location information available.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Geolocation has timed out.';
            break;
          default:
            errorMessage = 'Unknown location error.';
            break;
        }

        alert(errorMessage);

        const kievLocation = new L.LatLng(50.4501, 30.5234);
        if (map.value) {
          map.value.flyTo(kievLocation, 10, {
            animate: true,
            duration: SETTINGS_ZOOM_ANIMATION_DURATION
          });
        }

        isLocating.value = false;
      },
      options
  );
}

const clearCircles = () => {
  circles.forEach(circle => map.value!.removeLayer(circle));
  circles.length = 0;
}

const clearCirclesAndTarget = () => {
  clearCircles()
  calculatedData.value = null
  estimatedCasualties.value = 0
  selectedPresetName.value = ""
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

  const latlng = new L.LatLng(meteor.latitude, meteor.longitude);

  if (!marker.value && map.value) {
    marker.value = L.marker(latlng, { icon: customIcon }).addTo(map.value);
  } else if (marker.value) {
    marker.value.setLatLng(latlng);
  }

  const numCircles = 3;
  if (!map.value) return;

  const zoom = getZoomForRadius(craterRadius * numCircles);

  if (map.value) {
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

  const latlng = new L.LatLng(meteor.latitude, meteor.longitude);

  if (!map.value || !calculatedData.value) return;

  activeRadiusTime.value = timeSec;
  const step = calculatedData.value.radiusOverTime.find(r => r.time === timeSec);
  if (!step) return;

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

  const latlng = new L.LatLng(meteor.latitude, meteor.longitude);

  if (!map.value || !calculatedData.value) return;

  activeRadiusTime.value = null

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

    meteor.latitude = lat;
    meteor.longitude = lng;
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
      if (isDropdownOpen.value) {
        isDropdownOpen.value = false;
      }
    }
  })

  document.addEventListener('click', (e) => {
    const dropdown = document.querySelector('.dropdown');
    if (dropdown && !dropdown.contains(e.target as Node)) {
      isDropdownOpen.value = false;
    }
  });
})
</script>

<style scoped>

.meteor--presets__container {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 200px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 15px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  color: #333;
  z-index: 2000;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.meteor--presets__container label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  font-size: 12px;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meteor--presets__container input,
.meteor--presets__container select {
  width: 100%;
  padding: 6px 8px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  color: #333;
  outline: none;
  backdrop-filter: blur(5px);
}

.meteor--presets__container input:focus,
.meteor--presets__container select:focus {
  border-color: rgba(0, 0, 0, 0.4);
  background: rgba(255, 255, 255, 0.95);
}

.meteor--presets__container button {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.6);
  color: #333;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(5px);
}

.meteor--presets__container button:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-1px);
}

.dropdown {
  position: relative;
  display: inline-block;
  width: 100%;
}

.dropdown-btn {
  width: 100%;
  padding: 6px 8px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  color: #333;
  cursor: pointer;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
}

.dropdown-btn:hover {
  border-color: rgba(0, 0, 0, 0.4);
  background: rgba(255, 255, 255, 0.8);
}

.arrow {
  margin-left: 10px;
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 0;
  right: 100%;
  z-index: 9999;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 5px 0;
  max-height: 250px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  animation: dropdownFade 0.2s ease;
}

.dropdown.open-up .dropdown-menu {
  top: auto;
  bottom: 100%;
  transform-origin: bottom left;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: scaleY(0.9);
  }
  to {
    opacity: 1;
    transform: scaleY(1);
  }
}

.preset-item {
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.preset-item:last-child {
  border-bottom: none;
}

.preset-item:hover {
  background: rgba(255, 255, 255, 0.8);
}

.preset-name {
  font-weight: 600;
  margin-bottom: 2px;
  color: #333;
}

.preset-casualties {
  font-size: 12px;
  color: #666;
}

.casualties--display {
  background: rgba(255, 243, 205, 0.9);
  border: 1px solid rgba(255, 234, 167, 0.8);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
  text-align: center;
  backdrop-filter: blur(5px);
}

.casualties--number {
  font-weight: 600;
  color: #856404;
  font-size: 14px;
}

.random-meteor-btn {
  margin-top: 10px;
}

.meteor--info__link:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>