<script setup lang="ts">
import {
  NConfigProvider,
  NDialogProvider,
  NGlobalStyle,
  NLoadingBarProvider,
  NMessageProvider,
  NNotificationProvider,
} from 'naive-ui'
import { RouterView } from 'vue-router'

import RouterLoadingBar from './components/RouterLoadingBar/index.vue'
import { useTheme } from './composables/useTheme'

const { isDarkMode, naiveTheme } = useTheme()
</script>

<template>
  <div class="app-root" :class="{ 'app-root--dark': isDarkMode }">
    <NConfigProvider
      :theme="naiveTheme"
      :theme-overrides="{
        common: {
          primaryColor: '#2f8063',
          primaryColorHover: '#24664f',
          primaryColorPressed: '#1e5844',
          borderRadius: '8px',
        },
      }"
    >
      <NGlobalStyle />
      <NMessageProvider>
        <NDialogProvider>
          <NNotificationProvider>
            <NLoadingBarProvider
              :loading-bar-style="{
                loading: { backgroundColor: '#2f8063' },
                error: { backgroundColor: '#b54747' },
              }"
            >
              <RouterLoadingBar />
              <RouterView />
            </NLoadingBarProvider>
          </NNotificationProvider>
        </NDialogProvider>
      </NMessageProvider>
    </NConfigProvider>
  </div>
</template>
