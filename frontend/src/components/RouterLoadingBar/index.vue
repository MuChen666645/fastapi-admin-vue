<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useLoadingBar } from 'naive-ui'
import { useRouter } from 'vue-router'

import { usePreferencesStore } from '@/stores'

defineOptions({ name: 'RouterLoadingBar' })

const loadingBar = useLoadingBar()
const router = useRouter()
const preferences = usePreferencesStore()

const removeBeforeEach = router.beforeEach(() => {
  if (preferences.pageTransition) {
    loadingBar.start()
  }
})

const removeAfterEach = router.afterEach(() => {
  loadingBar.finish()
})

const removeOnError = router.onError(() => {
  loadingBar.error()
})

const waitForInitialNavigation = async (): Promise<void> => {
  if (preferences.pageTransition) {
    loadingBar.start()
  }

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
