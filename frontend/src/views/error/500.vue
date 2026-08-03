<script setup lang="ts">
import animationData from '@/assets/lottie/error/server-error.json'
import ErrorStatePage from './components/ErrorStatePage.vue'

defineOptions({ name: 'ServerErrorView' })
</script>

<template>
  <ErrorStatePage
    code="500"
    title-key="error.server.title"
    description-key="error.server.description"
    :animation-data="animationData"
  />
</template>
