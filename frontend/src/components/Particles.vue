<template>
    <vue-particles
        id="tsparticles"
        :options="fgOptions"
    />
</template>

<script setup lang="ts">
const rawStyles = getComputedStyle(document.documentElement)
const styles = {
    black: rawStyles.getPropertyValue("--black"),
    white: rawStyles.getPropertyValue("--white"),
}

const fgOptions = {
    background: { color: { value: styles.black }, opacity: 0 },
    fpsLimit: 144,
    interactivity: {
        events: {
            onClick: { enable: false },
            onHover: { enable: true, mode: "repulse" }
        },
        modes: {
            bubble: { distance: 400, duration: 2, opacity: 0.8, size: 40 },
            push: { quantity: 4 },
            repulse: { distance: 100, duration: .2 }
        }
    },
    particles: {
        color: { value: styles.white },
        links: {
            color: styles.white,
            distance: 100,
            enable: true,
            opacity: 0.5,
            width: 1
        },
        move: { enable: true, speed: 1, outModes: "bounce" },
        number: { density: { enable: true }, value: 80 },
        opacity: { value: 0.3 },
        shape: { type: "circle" },
        size: { value: { min: 1, max: 1.5 } }
    },
    detectRetina: true
};
</script>

<style>
#tsparticles {
    width: 100vw;
    height: 100dvh;

    position: fixed;
    top: 0;
    left: 0;

    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
</style>