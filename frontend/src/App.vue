<script setup lang="ts">
import { NLoadingBarProvider } from 'naive-ui'
import { RouterView } from 'vue-router'

import RouterLoadingBar from './components/RouterLoadingBar.vue'
</script>

<template>
  <n-loading-bar-provider
    :loading-bar-style="{
      loading: { backgroundColor: '#18a058' },
      error: { backgroundColor: '#d03050' },
    }"
  >
    <RouterLoadingBar />
    <RouterView />
  </n-loading-bar-provider>
</template>
