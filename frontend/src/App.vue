<script setup lang="ts">
import { computed, watch } from 'vue'
import {
  NConfigProvider,
  NDialogProvider,
  NGlobalStyle,
  NLoadingBarProvider,
  NMessageProvider,
  NNotificationProvider,
} from 'naive-ui'
import { RouterView } from 'vue-router'

import GlobalLoading from './components/GlobalLoading/index.vue'
import RouterLoadingBar from './components/RouterLoadingBar/index.vue'
import WatermarkOverlay from './components/WatermarkOverlay/index.vue'
import { useDocumentTitle } from './hooks/useDocumentTitle'
import { useTheme } from './hooks/useTheme'
import { usePreferencesStore } from './stores'
import { findAccentColor } from './utils/preferences'

const { isDarkMode, naiveTheme } = useTheme()
const preferences = usePreferencesStore()
useDocumentTitle()

const activeAccent = computed(() => findAccentColor(preferences.accentColor))
const themeOverrides = computed(() => {
  const primaryColor = isDarkMode.value ? activeAccent.value.dark : activeAccent.value.light
  const primaryColorHover = isDarkMode.value ? activeAccent.value.dark : activeAccent.value.hover

  return {
    common: {
      primaryColor,
      primaryColorHover,
      primaryColorPressed: primaryColorHover,
      borderRadius: `${preferences.radiusScale * 16}px`,
    },
  }
})

const loadingBarStyle = computed(() => ({
  loading: {
    backgroundColor: isDarkMode.value ? activeAccent.value.dark : activeAccent.value.light,
  },
  error: { backgroundColor: '#b54747' },
}))

const syncDocumentTheme = (): void => {
  if (typeof document === 'undefined') {
    return
  }

  const root = document.documentElement
  const radius = preferences.radiusScale * 16
  const primary = isDarkMode.value ? activeAccent.value.dark : activeAccent.value.light
  root.classList.toggle('app-theme-dark', isDarkMode.value)
  root.classList.toggle('app-root--color-weak', preferences.colorWeakMode)
  root.classList.toggle('app-root--grayscale', preferences.grayscaleMode)
  root.style.setProperty(
    '--app-color-primary',
    isDarkMode.value ? activeAccent.value.dark : activeAccent.value.light,
  )
  root.style.setProperty(
    '--app-color-primary-dark',
    isDarkMode.value ? activeAccent.value.dark : activeAccent.value.hover,
  )
  root.style.setProperty(
    '--app-color-primary-soft',
    `color-mix(in srgb, ${primary} 12%, var(--app-color-surface))`,
  )
  root.style.setProperty('--app-font-size', `${preferences.fontSize}px`)
  root.style.setProperty('--app-radius-xs', `${radius * 0.5}px`)
  root.style.setProperty('--app-radius-sm', `${radius * 0.75}px`)
  root.style.setProperty('--app-radius-md', `${radius}px`)
  root.style.setProperty('--app-radius-lg', `${radius * 1.25}px`)
  root.style.setProperty('--app-radius-xl', `${radius * 1.5}px`)
}

watch(
  () => [
    isDarkMode.value,
    preferences.accentColor,
    preferences.radiusScale,
    preferences.fontSize,
    preferences.colorWeakMode,
    preferences.grayscaleMode,
  ],
  syncDocumentTheme,
  { immediate: true },
)
</script>

<template>
  <div class="app-root" :class="{ 'app-root--dark': isDarkMode }">
    <NConfigProvider :theme="naiveTheme" :theme-overrides="themeOverrides">
      <NGlobalStyle />
      <NMessageProvider>
        <NDialogProvider>
          <NNotificationProvider>
            <NLoadingBarProvider :loading-bar-style="loadingBarStyle">
              <GlobalLoading />
              <RouterLoadingBar />
              <WatermarkOverlay />
              <RouterView />
            </NLoadingBarProvider>
          </NNotificationProvider>
        </NDialogProvider>
      </NMessageProvider>
    </NConfigProvider>
  </div>
</template>
