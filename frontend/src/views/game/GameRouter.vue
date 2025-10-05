<template>
    <div id="app">
        <div class="planets">
            <img src="/earth-planet.png" class="planet earth" alt=""/>
            <img src="/jupiter-planet.png" class="planet jupiter" alt=""/>
        </div>
        <Particles />
        <router-view></router-view>
    </div>
</template>

<script setup lang="ts">
import "@/css/game-router.css";
import Particles from "@components/Particles.vue";
</script>