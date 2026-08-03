<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  ContractOutline,
  ExpandOutline,
  MenuOutline,
  MoonOutline,
  NotificationsOutline,
  SearchOutline,
  ShieldCheckmarkOutline,
  SunnyOutline,
} from '@vicons/ionicons5'
import { NAvatar, NDropdown, NIcon, NLayoutHeader, useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

import AppBreadcrumb from '@/components/AppBreadcrumb/index.vue'
import { useLocale } from '@/hooks'
import { useTheme } from '@/hooks/useTheme'
import { clearAuthenticatedRoutes } from '@/router'
import { useAuthStore, useTabsStore } from '@/stores'

defineOptions({ name: 'AppHeader' })

const props = defineProps<{
  sidebarCollapsed: boolean
  showBreadcrumb: boolean
}>()
const emit = defineEmits<{
  'update:sidebarCollapsed': [value: boolean]
}>()

const router = useRouter()
const auth = useAuthStore()
const tabsStore = useTabsStore()
const message = useMessage()
const { isDarkMode, toggleTheme } = useTheme()
const { t } = useLocale()

const isFullscreen = ref(false)
const userInitial = computed(() => auth.displayName.slice(0, 1).toUpperCase())
const userAvatar = computed(() => auth.currentUser?.user.avatar ?? undefined)
const userRole = computed(() => auth.currentUser?.roles[0]?.name || t('app.user.role.admin'))
const userMenuOptions = computed(() => [
  { label: t('app.user.profile'), key: 'profile' },
  { label: t('app.user.settings'), key: 'settings' },
  { type: 'divider', key: 'divider' },
  { label: t('app.user.logout'), key: 'logout' },
])

const updateFullscreenState = (): void => {
  isFullscreen.value = Boolean(document.fullscreenElement)
}

const toggleSidebar = (): void => {
  emit('update:sidebarCollapsed', !props.sidebarCollapsed)
}

const toggleFullscreen = async (): Promise<void> => {
  if (!document.fullscreenEnabled) {
    message.warning(t('app.message.fullscreenUnsupported'))
    return
  }

  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen()
    } else {
      await document.documentElement.requestFullscreen()
    }
  } catch {
    message.error(t('app.message.fullscreenFailed'))
  }
}

const handleUserMenu = async (key: string | number): Promise<void> => {
  const menuKey = String(key)
  if (menuKey === 'profile') {
    if (router.hasRoute('profile')) {
      await router.push({ name: 'profile' })
      return
    }

    message.info(t('app.message.profileUnavailable'))
    return
  }

  if (menuKey === 'settings') {
    if (router.hasRoute('system-settings')) {
      await router.push({ name: 'system-settings' })
      return
    }

    message.info(t('app.message.settingsUnavailable'))
    return
  }

  if (menuKey !== 'logout') {
    return
  }

  try {
    await auth.signOut()
  } finally {
    tabsStore.reset()
    clearAuthenticatedRoutes()
    await router.replace({ name: 'login' })
  }
}

onMounted(() => {
  document.addEventListener('fullscreenchange', updateFullscreenState)
})

onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', updateFullscreenState)
})
</script>

<template>
  <NLayoutHeader class="app-header">
    <div class="header-left">
      <button
        type="button"
        class="header-icon-button sidebar-toggle"
        :aria-label="props.sidebarCollapsed ? t('app.sidebar.open') : t('app.sidebar.collapse')"
        :title="props.sidebarCollapsed ? t('app.sidebar.open') : t('app.sidebar.collapse')"
        @click="toggleSidebar"
      >
        <NIcon :size="19"><MenuOutline /></NIcon>
      </button>
      <div class="brand">
        <span class="brand-logo" aria-hidden="true">
          <NIcon :size="19"><ShieldCheckmarkOutline /></NIcon>
        </span>
        <strong>FastAPI Admin</strong>
        <span class="brand-version">v1.0</span>
      </div>
      <label class="header-search">
        <NIcon :size="15" aria-hidden="true"><SearchOutline /></NIcon>
        <input type="search" :placeholder="t('app.search')" :aria-label="t('app.search')" />
      </label>
    </div>

    <div v-if="props.showBreadcrumb" class="header-breadcrumb">
      <AppBreadcrumb />
    </div>

    <div class="header-actions">
      <button
        type="button"
        class="header-icon-button notification-button"
        :aria-label="t('app.notifications')"
        :title="t('app.notifications')"
      >
        <NIcon :size="18"><NotificationsOutline /></NIcon>
        <span class="notification-dot" aria-hidden="true" />
      </button>
      <span class="header-divider" aria-hidden="true" />
      <button
        type="button"
        class="header-icon-button fullscreen-toggle"
        :aria-label="isFullscreen ? t('app.fullscreen.exit') : t('app.fullscreen.enter')"
        :title="isFullscreen ? t('app.fullscreen.exit') : t('app.fullscreen.enter')"
        @click="toggleFullscreen"
      >
        <NIcon :size="18" aria-hidden="true">
          <ContractOutline v-if="isFullscreen" />
          <ExpandOutline v-else />
        </NIcon>
      </button>
      <button
        type="button"
        class="header-icon-button theme-toggle"
        :aria-label="isDarkMode ? t('app.theme.light') : t('app.theme.dark')"
        :title="isDarkMode ? t('app.theme.light') : t('app.theme.dark')"
        @click="toggleTheme"
      >
        <NIcon :size="18" aria-hidden="true">
          <SunnyOutline v-if="isDarkMode" />
          <MoonOutline v-else />
        </NIcon>
      </button>

      <NDropdown
        :options="userMenuOptions"
        trigger="click"
        placement="bottom-end"
        @select="handleUserMenu"
      >
        <button type="button" class="user-trigger" aria-haspopup="menu" :title="t('app.user.menu')">
          <NAvatar round :size="32" :src="userAvatar" class="user-avatar">
            {{ userInitial }}
          </NAvatar>
          <span class="user-meta">
            <span class="user-name">{{ auth.displayName }}</span>
            <span class="user-role">{{ userRole }}</span>
          </span>
        </button>
      </NDropdown>
    </div>
  </NLayoutHeader>
</template>
