<script setup lang="ts">
import { computed, h } from 'vue'
import type { Component } from 'vue'
import { NEmpty, NIcon, NLayoutSider, NMenu } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import { resolveIconComponent } from '@/hooks/useIcon'
import { useAuthStore } from '@/stores'
import type { UserRoute } from '@/types'

defineOptions({ name: 'AppSidebar' })

const collapsed = defineModel<boolean>('collapsed', { default: false })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const renderMenuIcon = (icon: Component) =>
  h(NIcon, { class: 'menu-item-icon', component: icon, 'aria-hidden': 'true' })

const toMenuOptions = (routes: UserRoute[]): MenuOption[] => {
  return routes
    .filter((item) => !item.hidden)
    .map((item) => {
      const children = toMenuOptions(item.children)
      const icon = resolveIconComponent(item.meta.icon)

      return {
        key: item.name,
        label: item.meta.title,
        ...(icon ? { icon: () => renderMenuIcon(icon) } : {}),
        ...(children.length > 0 ? { children } : {}),
      }
    })
}

const menuOptions = computed(() => toMenuOptions(auth.routes))
const activeMenuKey = computed(() => (route.name ? String(route.name) : null))
const dropdownProps = {
  class: 'sidebar-submenu-dropdown',
  overlap: false,
  showArrow: false,
}
const menuThemeOverrides = {
  peers: {
    Dropdown: {
      borderRadius: '10px',
      color: 'var(--app-color-surface)',
      optionColorHover: 'var(--app-color-primary)',
      optionColorActive: 'var(--app-color-primary)',
      optionTextColor: 'var(--app-color-text)',
      optionTextColorHover: 'var(--app-color-sidebar-accent-text)',
      optionTextColorActive: 'var(--app-color-sidebar-accent-text)',
      optionTextColorChildActive: 'var(--app-color-sidebar-accent-text)',
      prefixColor: 'var(--app-color-text)',
      suffixColor: 'var(--app-color-text)',
      peers: {
        Popover: {
          borderRadius: '10px',
          color: 'var(--app-color-surface)',
          boxShadow: '0 12px 28px rgb(35 43 86 / 18%)',
        },
      },
    },
  },
}

const handleMenuSelect = (key: string | number): void => {
  if (String(key) === activeMenuKey.value) {
    return
  }

  void router.push({ name: String(key) })
}
</script>

<template>
  <NLayoutSider
    :width="220"
    :collapsed="collapsed"
    :collapsed-width="64"
    :native-scrollbar="false"
    collapse-mode="width"
    class="app-sidebar"
  >
    <div class="sidebar-content">
      <div class="menu-caption">控制台导航</div>
      <NMenu
        :value="activeMenuKey"
        :options="menuOptions"
        :collapsed="collapsed"
        :collapsed-icon-size="20"
        :collapsed-width="64"
        :accordion="false"
        :theme-overrides="menuThemeOverrides"
        dropdown-placement="right-start"
        :dropdown-props="dropdownProps"
        @update:value="handleMenuSelect"
      />
      <NEmpty v-if="menuOptions.length === 0" class="empty-menu" description="暂无授权菜单" />
    </div>

    <div class="server-status">
      <strong class="server-status-title">服务器状态</strong>
      <div class="status-item">
        <div class="status-label"><span>CPU 使用率</span><strong>24%</strong></div>
        <div class="status-track"><span class="status-fill status-fill--green" /></div>
      </div>
      <div class="status-item">
        <div class="status-label"><span>内存 8GB / 16GB</span><strong>50%</strong></div>
        <div class="status-track"><span class="status-fill status-fill--yellow" /></div>
      </div>
    </div>
  </NLayoutSider>
</template>
