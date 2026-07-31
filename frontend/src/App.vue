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
import { useTheme } from './hooks/useTheme'

const { isDarkMode, naiveTheme } = useTheme()
const themeOverrides = computed(() => {
  const primaryColor = isDarkMode.value ? '#aeb8f3' : '#6c7ce5'
  const primaryColorHover = isDarkMode.value ? '#8ea1e9' : '#5762e0'

  return {
    common: {
      primaryColor,
      primaryColorHover,
      primaryColorPressed: primaryColorHover,
      borderRadius: '8px',
    },
  }
})

const syncDocumentTheme = (isDark: boolean): void => {
  if (typeof document === 'undefined') {
    return
  }

  document.documentElement.classList.toggle('app-theme-dark', isDark)
}

watch(isDarkMode, syncDocumentTheme, { immediate: true })
</script>

<template>
  <div class="app-root" :class="{ 'app-root--dark': isDarkMode }">
    <NConfigProvider :theme="naiveTheme" :theme-overrides="themeOverrides">
      <NGlobalStyle />
      <NMessageProvider>
        <NDialogProvider>
          <NNotificationProvider>
            <NLoadingBarProvider
              :loading-bar-style="{
                loading: { backgroundColor: isDarkMode ? '#aeb8f3' : '#6c7ce5' },
                error: { backgroundColor: '#b54747' },
              }"
            >
              <GlobalLoading />
              <RouterLoadingBar />
              <RouterView />
            </NLoadingBarProvider>
          </NNotificationProvider>
        </NDialogProvider>
      </NMessageProvider>
    </NConfigProvider>
  </div>
</template>
