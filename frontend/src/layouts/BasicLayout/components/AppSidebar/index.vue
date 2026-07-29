<script setup lang="ts">
import { computed, h } from 'vue'
import { NEmpty, NIcon, NLayoutSider, NMenu, NText } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import type { UserRoute } from '@/types'
import { useAuthStore } from '@/stores'
import { resolveMenuIcon } from '@/router/menu-icons'

defineOptions({ name: 'AppSidebar' })

const collapsed = defineModel<boolean>('collapsed', { default: false })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const toMenuOptions = (routes: UserRoute[]): MenuOption[] => {
  return routes
    .filter((item) => !item.hidden)
    .map((item) => {
      const children = toMenuOptions(item.children)
      return {
        key: item.name,
        label: item.meta.title,
        icon: () => renderMenuIcon(item.meta.icon),
        ...(children.length > 0 ? { children } : {}),
      }
    })
}

const menuOptions = computed(() => toMenuOptions(auth.routes))
const activeMenuKey = computed(() => (route.name ? String(route.name) : null))
const userInitial = computed(() => auth.displayName.slice(0, 1).toUpperCase())

const renderMenuIcon = (iconKey: string | null) =>
  h(
    NIcon,
    { class: 'menu-item-icon', 'aria-hidden': 'true' },
    { default: () => h(resolveMenuIcon(iconKey)) },
  )

const handleMenuSelect = (key: string | number): void => {
  if (String(key) === activeMenuKey.value) {
    return
  }

  void router.push({ name: String(key) })
}
</script>

<template>
  <NLayoutSider
    bordered
    :width="244"
    :collapsed="collapsed"
    :collapsed-width="64"
    :native-scrollbar="false"
    collapse-mode="width"
    class="app-sidebar"
  >
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">FA</div>
      <div class="brand-copy">
        <NText class="brand-title" strong>FastAPI Admin</NText>
        <NText class="brand-subtitle" depth="3">服务端权限工作台</NText>
      </div>
    </div>

    <div class="sidebar-profile">
      <div class="profile-avatar" aria-hidden="true">{{ userInitial }}</div>
      <div class="profile-copy">
        <NText class="profile-name" strong>{{ auth.displayName }}</NText>
        <NText class="profile-role" depth="3">
          {{ auth.currentUser?.roles[0]?.name || '已登录用户' }}
        </NText>
      </div>
    </div>

    <div class="menu-caption">授权菜单</div>
    <NMenu
      :value="activeMenuKey"
      :options="menuOptions"
      :indent="20"
      :accordion="false"
      @update:value="handleMenuSelect"
    />
    <NEmpty v-if="menuOptions.length === 0" class="empty-menu" description="暂无授权菜单" />
  </NLayoutSider>
</template>

<style>
.app-sidebar {
  min-height: 100vh;
  color: var(--app-color-sidebar-text);
  background: var(--app-color-sidebar);
  border-right: 1px solid var(--app-color-sidebar-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 72px;
  padding: 0 22px;
  border-bottom: 1px solid var(--app-color-sidebar-border);
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  place-items: center;
  color: var(--app-color-sidebar-accent-text);
  border-radius: 8px;
  background: var(--app-color-sidebar-accent);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-copy,
.profile-copy {
  min-width: 0;
}

.menu-item-icon {
  display: inline-grid;
  width: 20px;
  height: 20px;
  place-items: center;
  color: currentcolor;
  font-size: 14px;
  line-height: 1;
}

.app-sidebar.n-layout-sider--collapsed .brand {
  justify-content: center;
  padding: 0;
}

.app-sidebar.n-layout-sider--collapsed .brand-copy,
.app-sidebar.n-layout-sider--collapsed .sidebar-profile,
.app-sidebar.n-layout-sider--collapsed .menu-caption {
  display: none;
}

.app-sidebar.n-layout-sider--collapsed .n-menu-item-content {
  justify-content: center;
  margin-right: 10px;
  margin-left: 10px;
}

.brand-title,
.profile-name {
  display: block;
  color: var(--app-color-sidebar-text);
}

.brand-subtitle,
.profile-role {
  display: block;
  margin-top: 3px;
  color: var(--app-color-sidebar-muted);
  font-size: 12px;
}

.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 16px;
  padding: 12px;
  border: 1px solid var(--app-color-sidebar-border);
  border-radius: 8px;
  background: var(--app-color-sidebar-hover);
}

.profile-avatar {
  display: grid;
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  place-items: center;
  color: var(--app-color-sidebar-accent-text);
  border-radius: 50%;
  background: var(--app-color-sidebar-accent);
  font-size: 14px;
  font-weight: 800;
}

.menu-caption {
  padding: 0 22px 10px;
  color: var(--app-color-sidebar-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.empty-menu {
  padding: 24px 16px;
  color: var(--app-color-sidebar-muted);
}

.app-sidebar .n-menu-item-content {
  margin: 2px 12px;
  color: var(--app-color-sidebar-text);
  border-radius: 6px;
}

.app-sidebar .n-menu-item-content--selected {
  color: var(--app-color-sidebar-text);
  background: var(--app-color-sidebar-selected);
}

.app-sidebar .n-menu-item-content:hover {
  background: var(--app-color-sidebar-hover);
}

.app-sidebar .n-menu-item-content-header {
  color: inherit;
}
</style>
