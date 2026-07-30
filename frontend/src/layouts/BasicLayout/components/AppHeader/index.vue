<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
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
import { useTheme } from '@/hooks/useTheme'
import { clearAuthenticatedRoutes } from '@/router'
import { useAuthStore, useTabsStore } from '@/stores'

defineOptions({ name: 'AppHeader' })

const props = defineProps<{ sidebarCollapsed: boolean }>()
const emit = defineEmits<{
  'update:sidebarCollapsed': [value: boolean]
}>()

const router = useRouter()
const auth = useAuthStore()
const tabsStore = useTabsStore()
const message = useMessage()
const { isDarkMode, toggleTheme } = useTheme()

const isFullscreen = ref(false)
const userInitial = computed(() => auth.displayName.slice(0, 1).toUpperCase())
const userAvatar = computed(() => auth.currentUser?.user.avatar ?? undefined)
const userRole = computed(() => auth.currentUser?.roles[0]?.name || '系统管理员')
const userMenuOptions = [
  { label: '个人中心', key: 'profile' },
  { label: '系统设置', key: 'settings' },
  { type: 'divider', key: 'divider' },
  { label: '退出登录', key: 'logout' },
]

const updateFullscreenState = (): void => {
  isFullscreen.value = Boolean(document.fullscreenElement)
}

const toggleSidebar = (): void => {
  emit('update:sidebarCollapsed', !props.sidebarCollapsed)
}

const toggleFullscreen = async (): Promise<void> => {
  if (!document.fullscreenEnabled) {
    message.warning('当前浏览器不支持全屏')
    return
  }

  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen()
    } else {
      await document.documentElement.requestFullscreen()
    }
  } catch {
    message.error('全屏切换失败，请检查浏览器权限')
  }
}

const handleUserMenu = async (key: string | number): Promise<void> => {
  const menuKey = String(key)
  if (menuKey === 'profile') {
    if (router.hasRoute('profile')) {
      await router.push({ name: 'profile' })
      return
    }

    message.info('个人中心页面暂未配置')
    return
  }

  if (menuKey === 'settings') {
    if (router.hasRoute('config')) {
      await router.push({ name: 'config' })
      return
    }

    message.info('系统设置菜单暂未授权')
    return
  }

  if (menuKey !== 'logout') {
    return
  }

  try {
    await auth.signOut()
  } catch {
    // 退出接口失败时，Store 仍会清理本地会话并回到登录页。
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
        :aria-label="props.sidebarCollapsed ? '展开菜单' : '收起菜单'"
        :title="props.sidebarCollapsed ? '展开菜单' : '收起菜单'"
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
        <input type="search" placeholder="搜索功能..." aria-label="搜索功能" />
      </label>
    </div>

    <div class="header-breadcrumb">
      <AppBreadcrumb />
    </div>

    <div class="header-actions">
      <button
        type="button"
        class="header-icon-button notification-button"
        aria-label="通知"
        title="通知"
      >
        <NIcon :size="18"><NotificationsOutline /></NIcon>
        <span class="notification-dot" aria-hidden="true" />
      </button>
      <span class="header-divider" aria-hidden="true" />
      <button
        type="button"
        class="header-icon-button fullscreen-toggle"
        :aria-label="isFullscreen ? '退出全屏' : '进入全屏'"
        :title="isFullscreen ? '退出全屏' : '进入全屏'"
        @click="toggleFullscreen"
      >
        <span aria-hidden="true">{{ isFullscreen ? '⤢' : '⛶' }}</span>
      </button>
      <button
        type="button"
        class="header-icon-button theme-toggle"
        :aria-label="isDarkMode ? '切换亮色模式' : '切换暗色模式'"
        :title="isDarkMode ? '切换亮色模式' : '切换暗色模式'"
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
        <button type="button" class="user-trigger" aria-haspopup="menu" title="打开用户菜单">
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
