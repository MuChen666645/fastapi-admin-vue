<script setup lang="ts">
import animationData from '@/assets/lottie/error/no-address.json'
import ErrorStatePage from './components/ErrorStatePage.vue'

defineOptions({ name: 'NotFoundView' })
</script>

<template>
  <ErrorStatePage
    code="404"
    title-key="error.notFound.title"
    description-key="error.notFound.description"
    :animation-data="animationData"
  />
</template>
