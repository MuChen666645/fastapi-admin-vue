<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NAvatar, NDropdown, NLayoutHeader, useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

import AppBreadcrumb from '@/components/AppBreadcrumb/index.vue'
import { useTheme } from '@/composables/useTheme'
import { clearAuthenticatedRoutes } from '@/router'
import { useAuthStore } from '@/stores'

defineOptions({ name: 'AppHeader' })

const props = defineProps<{ sidebarCollapsed: boolean }>()
const emit = defineEmits<{
  'update:sidebarCollapsed': [value: boolean]
}>()

const router = useRouter()
const auth = useAuthStore()
const message = useMessage()
const { isDarkMode, toggleTheme } = useTheme()

const isFullscreen = ref(false)
const userInitial = computed(() => auth.displayName.slice(0, 1).toUpperCase())
const userAvatar = computed(() => auth.currentUser?.user.avatar ?? undefined)
const userRole = computed(() => auth.currentUser?.roles[0]?.name || '已登录用户')
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
    // 退出接口失败时，本地会话仍已由 Store 清理，继续回到登录页。
  } finally {
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
  <NLayoutHeader bordered class="app-header">
    <div class="header-left">
      <button
        type="button"
        class="header-icon-button sidebar-toggle"
        :aria-label="props.sidebarCollapsed ? '展开菜单' : '收缩菜单'"
        :title="props.sidebarCollapsed ? '展开菜单' : '收缩菜单'"
        @click="toggleSidebar"
      >
        <span aria-hidden="true">☰</span>
      </button>
      <div class="header-breadcrumb">
        <AppBreadcrumb />
      </div>
    </div>

    <div class="header-actions">
      <button
        type="button"
        class="header-icon-button fullscreen-toggle"
        :aria-label="isFullscreen ? '退出全屏' : '进入全屏'"
        :title="isFullscreen ? '退出全屏' : '进入全屏'"
        @click="toggleFullscreen"
      >
        <span aria-hidden="true">⛶</span>
      </button>
      <button
        type="button"
        class="header-icon-button theme-toggle"
        :aria-label="isDarkMode ? '切换亮色模式' : '切换暗色模式'"
        :title="isDarkMode ? '切换亮色模式' : '切换暗色模式'"
        @click="toggleTheme"
      >
        <span aria-hidden="true">{{ isDarkMode ? '☀' : '☾' }}</span>
      </button>

      <NDropdown
        :options="userMenuOptions"
        trigger="click"
        placement="bottom-end"
        @select="handleUserMenu"
      >
        <button type="button" class="user-trigger" aria-haspopup="menu" title="打开用户菜单">
          <NAvatar round :size="34" :src="userAvatar" class="user-avatar">
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

<style scoped>
.app-header {
  display: flex;
  min-height: 64px;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  color: var(--app-color-text);
  background: var(--app-color-surface);
  border-bottom: 1px solid var(--app-color-border);
}

.header-left,
.header-actions,
.user-trigger {
  display: flex;
  align-items: center;
}

.header-left {
  min-width: 0;
  gap: 20px;
}

.header-actions {
  gap: 8px;
}

.header-breadcrumb {
  min-width: 0;
}

.header-breadcrumb :deep(.app-breadcrumb) {
  margin: 0;
}

.header-icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  padding: 0;
  place-items: center;
  color: var(--app-color-text-muted);
  border: 0;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  font-size: 19px;
  line-height: 1;
}

.header-icon-button:hover,
.header-icon-button:focus-visible {
  color: var(--app-color-primary);
  background: var(--app-color-surface-muted);
  outline: none;
}

.fullscreen-toggle {
  font-size: 21px;
}

.theme-toggle {
  font-size: 20px;
}

.user-trigger {
  gap: 10px;
  padding: 4px 0 4px 8px;
  color: var(--app-color-text);
  border: 0;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.user-trigger:focus-visible {
  border-radius: 6px;
  outline: 2px solid var(--app-color-primary);
  outline-offset: 2px;
}

.user-avatar {
  color: #fff;
  background: #2f6df6;
  font-size: 13px;
  font-weight: 700;
}

.user-meta {
  display: grid;
  min-width: 92px;
  gap: 2px;
}

.user-name,
.user-role {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-name {
  font-size: 13px;
}

.user-role {
  color: var(--app-color-text-muted);
  font-size: 11px;
}

.user-arrow {
  color: var(--app-color-text-muted);
  font-size: 17px;
}

@media (width <= 768px) {
  .app-header {
    padding: 0 14px;
  }

  .header-left {
    gap: 10px;
  }

  .header-actions {
    gap: 2px;
  }

  .user-meta,
  .user-arrow {
    display: none;
  }

  .user-trigger {
    padding-left: 4px;
  }
}
</style>
