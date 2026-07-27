<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useLoadingBar } from 'naive-ui'
import { useRouter } from 'vue-router'

const loadingBar = useLoadingBar()
const router = useRouter()

const removeBeforeEach = router.beforeEach(() => {
  loadingBar.start()
})

const removeAfterEach = router.afterEach(() => {
  loadingBar.finish()
})

const removeOnError = router.onError(() => {
  loadingBar.error()
})

onBeforeUnmount(() => {
  removeBeforeEach()
  removeAfterEach()
  removeOnError()
})
</script>

<template>
  <span aria-hidden="true" />
</template>
