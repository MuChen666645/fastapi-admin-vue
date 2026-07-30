<script setup lang="ts">
import { computed } from 'vue'
import { NBreadcrumb, NBreadcrumbItem } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import type { UserRouteMenuType } from '@/types'

defineOptions({ name: 'AppBreadcrumb' })

interface BreadcrumbItem {
  key: string
  name: string | symbol | null | undefined
  path: string
  title: string
  menuType: UserRouteMenuType
  link: string | null
  isCurrent: boolean
}

const readMenuType = (value: unknown): UserRouteMenuType => {
  if (value === 'L' || value === 'I' || value === 'W') {
    return value
  }

  return 'C'
}

const readLink = (value: unknown): string | null =>
  typeof value === 'string' && value.length > 0 ? value : null

const route = useRoute()
const router = useRouter()

const breadcrumbItems = computed<BreadcrumbItem[]>(() =>
  route.matched
    .filter(({ meta }) => Boolean(meta.title) && meta.hideBreadcrumb !== true)
    .map(({ meta, name, path }) => ({
      key: String(name ?? path),
      name,
      path,
      title: String(meta.title),
      menuType: readMenuType(meta.menuType),
      link: readLink(meta.link),
      isCurrent: path === route.path,
    })),
)

const handleBreadcrumbClick = async (item: BreadcrumbItem): Promise<void> => {
  if (item.isCurrent || !item.name) {
    return
  }

  if (item.menuType === 'L' || item.menuType === 'W') {
    if (!item.link || typeof window === 'undefined') {
      return
    }

    let externalUrl: URL
    try {
      externalUrl = new URL(item.link)
    } catch {
      return
    }

    if (
      (externalUrl.protocol !== 'http:' && externalUrl.protocol !== 'https:') ||
      externalUrl.username ||
      externalUrl.password
    ) {
      return
    }

    window.open(externalUrl.href, '_blank', 'noopener,noreferrer')
    return
  }

  const target = { name: item.name }
  const resolvedTarget = router.resolve(target)
  if (resolvedTarget.fullPath === route.fullPath) {
    return
  }

  await router.push(target)
}
</script>

<template>
  <NBreadcrumb v-if="breadcrumbItems.length" class="app-breadcrumb">
    <NBreadcrumbItem v-for="item in breadcrumbItems" :key="item.key">
      <a
        v-if="!item.isCurrent && item.name"
        :href="router.resolve({ name: item.name }).href"
        class="breadcrumb-link"
        @click.prevent="handleBreadcrumbClick(item)"
      >
        {{ item.title }}
      </a>
      <span v-else aria-current="page">{{ item.title }}</span>
    </NBreadcrumbItem>
  </NBreadcrumb>
</template>
