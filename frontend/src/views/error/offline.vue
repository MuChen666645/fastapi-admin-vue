<script setup lang="ts">
import animationData from '@/assets/lottie/error/no-signal.json'
import ErrorStatePage from './components/ErrorStatePage.vue'

defineOptions({ name: 'OfflineView' })
</script>

<template>
  <ErrorStatePage
    code="OFFLINE"
    title-key="error.offline.title"
    description-key="error.offline.description"
    :animation-data="animationData"
  />
</template>
