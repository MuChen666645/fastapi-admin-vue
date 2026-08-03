<script setup lang="ts">
import { computed, h } from 'vue'
import type { Component } from 'vue'
import { NEmpty, NIcon, NLayoutSider, NMenu } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { useLocale } from '@/hooks'
import { resolveIconComponent } from '@/hooks/useIcon'
import { useAuthStore } from '@/stores'
import type { UserRoute } from '@/types'
import { translateMenuTitle } from '@/utils/i18n'

defineOptions({ name: 'AppSidebar' })

const collapsed = defineModel<boolean>('collapsed', { default: false })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { language, t } = useLocale()

const renderMenuIcon = (icon: Component) =>
  h(NIcon, { class: 'menu-item-icon', component: icon, 'aria-hidden': 'true' })

const toMenuOptions = (routes: UserRoute[], locale: typeof language.value): MenuOption[] => {
  return routes
    .filter((item) => !item.hidden)
    .map((item) => {
      const children = toMenuOptions(item.children, locale)
      const icon = resolveIconComponent(item.meta.icon)

      return {
        key: item.name,
        label: translateMenuTitle(item.meta.title, locale),
        ...(icon ? { icon: () => renderMenuIcon(icon) } : {}),
        ...(children.length > 0 ? { children } : {}),
      }
    })
}

const toStaticMenuOptions = (
  routes: RouteRecordRaw[],
  locale: typeof language.value,
): MenuOption[] =>
  routes
    .filter((item) => {
      const meta = item.meta ?? {}
      return (
        meta.requiresAuth === true &&
        meta.menu === true &&
        meta.dynamic !== true &&
        typeof item.name === 'string'
      )
    })
    .map((item) => {
      const meta = item.meta ?? {}
      const children = toStaticMenuOptions(item.children ?? [], locale)
      const iconName = typeof meta.icon === 'string' ? meta.icon : null
      const icon = resolveIconComponent(iconName)

      return {
        key: String(item.name),
        label: translateMenuTitle(String(meta.title ?? item.name), locale),
        ...(icon ? { icon: () => renderMenuIcon(icon) } : {}),
        ...(children.length > 0 ? { children } : {}),
      }
    })

const staticMenuOptions = computed<MenuOption[]>(() => {
  const appRoute = router.getRoutes().find((item) => item.name === 'app')
  return appRoute ? toStaticMenuOptions(appRoute.children ?? [], language.value) : []
})

const menuOptions = computed(() => {
  const serverMenuOptions = toMenuOptions(auth.routes, language.value)
  const serverMenuKeys = new Set(serverMenuOptions.map((item) => String(item.key)))

  return [
    ...serverMenuOptions,
    ...staticMenuOptions.value.filter((item) => !serverMenuKeys.has(String(item.key))),
  ]
})
const activeMenuKey = computed(() => (route.name ? String(route.name) : null))
const dropdownProps = {
  class: 'sidebar-submenu-dropdown',
  overlap: false,
  showArrow: false,
}
const menuThemeOverrides = {
  peers: {
    Dropdown: {
      borderRadius: 'var(--app-radius-lg)',
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
      <div class="menu-caption">{{ t('sidebar.caption') }}</div>
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
      <NEmpty
        v-if="menuOptions.length === 0"
        class="empty-menu"
        :description="t('sidebar.empty')"
      />
    </div>

    <div class="server-status">
      <strong class="server-status-title">{{ t('sidebar.serverStatus') }}</strong>
      <div class="status-item">
        <div class="status-label">
          <span>{{ t('sidebar.cpu') }}</span
          ><strong>24%</strong>
        </div>
        <div class="status-track"><span class="status-fill status-fill--green" /></div>
      </div>
      <div class="status-item">
        <div class="status-label">
          <span>{{ t('sidebar.memory') }}</span
          ><strong>50%</strong>
        </div>
        <div class="status-track"><span class="status-fill status-fill--yellow" /></div>
      </div>
    </div>
  </NLayoutSider>
</template>
