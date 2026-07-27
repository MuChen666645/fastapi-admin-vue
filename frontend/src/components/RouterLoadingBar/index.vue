<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useLoadingBar } from 'naive-ui'
import { useRouter } from 'vue-router'

defineOptions({ name: 'RouterLoadingBar' })

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

const waitForInitialNavigation = async (): Promise<void> => {
  loadingBar.start()

  try {
    await router.isReady()
    loadingBar.finish()
  } catch {
    loadingBar.error()
  }
}

void waitForInitialNavigation()

onBeforeUnmount(() => {
  removeBeforeEach()
  removeAfterEach()
  removeOnError()
})
</script>

<template>
  <span aria-hidden="true" />
</template>
