<template>
    <div class="swiper--container">
        <swiper
            ref="swiperRef"
            :modules="[Autoplay]"
            :autoplay="{ delay: 3000, disableOnInteraction: false }"
            loop
            @swiper="onSwiperInit"
            class="mySwiper"
        >
            <swiper-slide v-for="(img, i) in images" :key="i">
                <img :src="`/landing/${img}`" :alt="img.replace('.png', '')" />
            </swiper-slide>
        </swiper>

        <div class="buttons-container">
            <button class="button" @click="toggleAutoplay">{{ isPlaying ? '⏸' : '▶' }}</button>
        </div>
    </div>
</template>

<script setup lang="ts">
import {Autoplay} from "swiper/modules";
import {Swiper, SwiperSlide} from "swiper/vue";
import {ref} from "vue";

defineProps<{
    images: string[]
}>()

const swiperRef = ref<any>(null)
const isPlaying = ref(true)
let swiperInstance: any = null

const onSwiperInit = (swiper: any) => {
    swiperInstance = swiper
    isPlaying.value = swiper.autoplay.running
}

const toggleAutoplay = () => {
    if (!swiperInstance) return
    if (isPlaying.value) swiperInstance.autoplay.stop()
    else swiperInstance.autoplay.start()
    isPlaying.value = !isPlaying.value
}
</script>