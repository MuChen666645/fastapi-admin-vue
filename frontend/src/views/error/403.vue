<script setup lang="ts">
import animationData from '@/assets/lottie/error/permission-upgrade.json'
import ErrorStatePage from './components/ErrorStatePage.vue'

defineOptions({ name: 'ForbiddenView' })
</script>

<template>
  <ErrorStatePage
    code="403"
    title-key="error.forbidden.title"
    description-key="error.forbidden.description"
    :animation-data="animationData"
  />
</template>
