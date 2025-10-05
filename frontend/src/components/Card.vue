<template>
    <div class="card" :class="color">
        <div class="container">
            <img :src="imageUrl" :alt="imageUrl.split('/').pop()!.replace('.jpg', '')"/>
            <span :class="color">{{title}}</span>
        </div>
       <div class="description--container">
           <slot name="description" />
           <span class="description">{{description}}</span>
       </div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    title: string;
    imageUrl: string;
    description: string;
    color: 'green' | 'red' | 'orange' | 'purple' | 'primary';
}>()
</script>