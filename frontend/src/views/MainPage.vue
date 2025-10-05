<template>

    <Particles />

    <div class="progress--bar">
        <div
            class="progress--bar__fill"
            :style="{ height: progress + '%' }"
        />
    </div>

    <div class="page" ref="pageRef">
        <header class="banner banner--header">
            <span class="banner--name">Meteor<span class="primary--text">X</span></span>

            <nav class="banner--nav">
                <router-link
                    class="router-link"
                    :to="{name: 'map-page'}"
                >
                    <span class="router-link__number">01</span> Map
                </router-link>
                <router-link
                    class="router-link"
                    :to="{name: 'game-page'}"
                >
                    <span class="router-link__number">02</span> Game
                </router-link>
                <a
                    class="router-link"
                    href="https://github.com/deniSSTK"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="router-link__number">03</span> Repo
                </a>
                <router-link
                    class="router-link"
                    :to="{name: 'login-page'}"
                >
                    <span class="router-link__number">04</span> Login
                </router-link>
            </nav>
        </header>

        <div class="content">
            <div class="info--container">
                <h5>Meteor<span class="primary--text">X</span></h5>
                <span class="info__description">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut facere inventore iure minima modi omnis quaerat, rerum saepe ullam! Atque autem dolore expedita, fugit labore nisi perspiciatis quaerat sint voluptas!</span>
            </div>

            <div class="buttons-container">
                <router-link
                    class="button"
                    :to="{name: 'map-page'}"
                >
                    Map
                </router-link>
                <router-link
                    class="button"
                    :to="{name: 'game-page'}"
                >
                    Game
                </router-link>
            </div>

            <MySwiper
                :images="savePlanetGameImages"
            />

            <span class="line" />

            <div class="info--container">
                <h5>Save Planet <span class="primary--text">Game</span></h5>
                <span class="info__description">Random meteors are approaching! Choose the right card to save your planet.</span>
            </div>

            <div class="cards--container">
                <Card
                    image-url="/game-card/ROCKET.png"
                    title="Rocket Card"
                    description="Launch it to smash meteors out of your way!"
                    color="red"
                />
                <Card
                    image-url="/game-card/BUNKER.png"
                    title="Bunker Card"
                    description="Dive in when the clock is ticking and danger looms."
                    color="green"
                />
                <Card
                    image-url="/game-card/EVACUATION.png"
                    title="Evacuation Card"
                    description="Plan ahead and escape before chaos strikes."
                    color="orange"
                />
                <Card
                    image-url="/game-card/IGNORE.png"
                    title="Ignore Card"
                    description="Let it pass—sometimes the best move is inaction."
                    color="purple"
                />
            </div>

            <div class="buttons-container">
                <router-link
                    class="button"
                    :to="{name: 'game-page'}"
                >
                    Play!
                </router-link>
            </div>

            <span class="line" />

            <div class="info--container">
                <h5>Save Planet <span class="primary--text">Coop</span></h5>
                <span class="info__description">Team up in a <span class="primary--text">4-player</span> coop! When random meteors strike, everyone holds a unique card—choose wisely to protect the planet.</span>
            </div>

            <MySwiper
                :images="savePlanetCoopImages"
            />

            <span class="line" />

            <div class="info--container">
                <h5>Create Meteor <span class="primary--text">Sandbox</span></h5>
                <span class="info__description">Design <span class="primary--text">your own meteors</span> and see the consequences hit the planet!</span>
            </div>

            <div class="cards--container">
                <!--TODO change images-->
                <Card
                    image-url="/change"
                    title="AI Meteor Generator"
                    description="Unleash meteors created by AI and test your planet's defenses."
                    color="red"
                />
                <Card
                    image-url="/change"
                    title="AI Casualty Counter"
                    description="Let AI calculate potential casualties from incoming meteors."
                    color="green"
                />
                <Card
                    image-url="/change"
                    title="Timeline Inspection"
                    description="Preview the destruction at 30 minutes, 1 hour, and 2 hours intervals."
                    color="orange"
                />
                <Card
                    image-url="/change"
                    title="And Much More"
                    description="Teleport to any user, use real meteor data, enter watch mode, and explore additional features."
                    color="purple"
                />
            </div>

            <div class="info--container">
                <span class="info__description">Map <span class="primary--text">screenshots</span>:</span>
            </div>

            <MySwiper
                :images="createMeteorSandboxImages"
            />

            <span class="line" />

            <div class="info--container">
                <h5>Our <span class="primary--text">Team</span></h5>
                <span class="info__description">Meet our team behind the meteors—design, simulate, and watch the chaos!</span>
            </div>

            <div class="cards--container">
                <!--TODO change images-->
                <Card
                    image-url="/landing/members/denis.jpg"
                    title="Denis Tkachenko"
                    description="Team Lead, Main Idea, Full Stack, Design"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://github.com/deniSSTK"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <GitHub />
                            </a>
                            <a
                                class="description--link"
                                href="https://www.linkedin.com/in/denis-tkachenko-b7a801327/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <LinkedIn />
                            </a>
                            <a
                                class="description--link"
                                href="https://t.me/DenisTk1"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Telegram />
                            </a>
                        </div>
                    </template>
                </Card>
                <Card
                    image-url="/landing/members/yarik.jpg"
                    title="Yaroslav Sorochan"
                    description="Backend, AI tools, Design, DevOps"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://github.com/soroqn1"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <GitHub />
                            </a>
                            <a
                                class="description--link"
                                href="https://www.linkedin.com/in/yaroslav-sorochan-8098231b1/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <LinkedIn />
                            </a>
                            <a
                                class="description--link"
                                href="https://t.me/soroqn"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Telegram />
                            </a>
                        </div>
                    </template>
                </Card>
                <Card
                    image-url="/landing/members/maksim-old.jpg"
                    title="Maxim Geruk"
                    description="Speaker, Design, Presentation"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://www.instagram.com/maxim.geruk/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Instagram />
                            </a>
                        </div>
                    </template>
                </Card>
                <Card
                    image-url="/landing/members/yarik-junior.png"
                    title="Yaroslav Kalashnyk"
                    description="9 years old member, Main Game Logic on python"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://github.com/YarOK1"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <GitHub />
                            </a>
                        </div>
                    </template>
                </Card>
                <Card
                    image-url="/landing/members/maksim.jpg"
                    title="Maksim Balatsky"
                    description="Layout Login/Sign up pages, Game background"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://github.com/Maksimk9245"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <GitHub />
                            </a>
                            <a
                                class="description--link"
                                href="https://www.linkedin.com/in/maksym-balatskyi-ab3b67328/"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <LinkedIn />
                            </a>
                            <a
                                class="description--link"
                                href="https://t.me/MaksimkaBl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Telegram />
                            </a>
                        </div>
                    </template>
                </Card>
                <Card
                    image-url="/landing/members/artur.jpg"
                    title="Artur Mauboroda"
                    description="Random meteor functionality, Teleport to user location fixes"
                    color="primary"
                >
                    <template #description>
                        <div class="description--link__container">
                            <a
                                class="description--link"
                                href="https://github.com/artur-ai"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <GitHub />
                            </a>
                        </div>
                    </template>
                </Card>
            </div>
        </div>

        <footer class="banner">
            <nav class="banner--nav">
                <a
                    class="router-link"
                    href="https://www.spaceappschallenge.org/2025/find-a-team/meteorx/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="router-link__number">2025</span> NASA Space Apps Challenge
                </a>
                <a
                    class="router-link"
                    href="https://github.com/deniSSTK"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="router-link__number">Our</span> Repo
                </a>
                <a
                    class="router-link"
                    href="https://vuejs.org/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="router-link__number">Vue</span>.js
                </a>
                <a
                    class="router-link"
                    href="https://ai.google.dev/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <span class="router-link__number">Google</span> Gemini
                </a>
            </nav>
        </footer>
    </div>
</template>

<script setup lang="ts">
import {nextTick, onMounted, onUnmounted, ref} from "vue";

import "@/css/main-page.scss";

import Card from "@components/Card.vue";
import MySwiper from "@components/MySwiper.vue";
import Particles from "@components/Particles.vue";

import GitHub from "@components/icons/GitHub.vue";
import LinkedIn from "@components/icons/LinkedIn.vue";
import Telegram from "@components/icons/Telegram.vue";

//@ts-ignore
import 'swiper/css'; import 'swiper/css/autoplay';
import Instagram from "@components/icons/Instagram.vue";

const savePlanetGameImages: string[] = [
    'map.png',
    'game.png',
]

const savePlanetCoopImages: string[] = [
    'game.png', //todo change to login screenshots
    'coop.png',
    'room.png',
    'game.png', //todo change to game screenshots
]

const createMeteorSandboxImages: string[] = [
    //TODO change images
    'game.png',
    'coop.png',
]

const progress = ref<number>(0);
const pageRef = ref<HTMLElement | null>(null);

function loadImages(list: string[]) {
    list.forEach(src => {
        const img = new Image();
        img.src = '/landing/' + src;
    })
}

function computeDocHeight(container: HTMLElement): number {
    return Math.max(0, container.scrollHeight - container.clientHeight);
}

function updateProgress() {
    if (!pageRef.value) return;

    const scrollTop = pageRef.value.scrollTop;
    const docHeight = computeDocHeight(pageRef.value);

    if (docHeight <= 0) {
        progress.value = 0;
        return;
    }

    const pct = (scrollTop / docHeight) * 100;
    progress.value = Math.min(100, Math.max(0, Math.round(pct)));
}

onMounted(async () => {
    await nextTick();

    if (pageRef.value) {
        setTimeout(updateProgress, 200);
        pageRef.value.addEventListener('scroll', updateProgress, { passive: true });
    }

    loadImages(savePlanetGameImages);
    loadImages(savePlanetCoopImages);
});

onUnmounted(() => {
    if (pageRef.value) {
        pageRef.value.removeEventListener('scroll', updateProgress);
    }
});
</script>