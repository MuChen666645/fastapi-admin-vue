<script setup lang="ts">
import { computed } from 'vue'
import { NBreadcrumb, NBreadcrumbItem } from 'naive-ui'
import { RouterLink, useRoute } from 'vue-router'

defineOptions({ name: 'AppBreadcrumb' })

interface BreadcrumbItem {
  key: string
  name: string | symbol | null | undefined
  path: string
  title: string
  isCurrent: boolean
}

const route = useRoute()

const breadcrumbItems = computed<BreadcrumbItem[]>(() =>
  route.matched
    .filter(({ meta }) => Boolean(meta.title) && meta.hideBreadcrumb !== true)
    .map(({ meta, name, path }) => ({
      key: String(name ?? path),
      name,
      path,
      title: String(meta.title),
      isCurrent: path === route.path,
    })),
)
</script>

<template>
  <NBreadcrumb v-if="breadcrumbItems.length" class="app-breadcrumb">
    <NBreadcrumbItem v-for="item in breadcrumbItems" :key="item.key">
      <RouterLink
        v-if="!item.isCurrent && item.name"
        :to="{ name: item.name }"
        class="breadcrumb-link"
      >
        {{ item.title }}
      </RouterLink>
      <span v-else aria-current="page">{{ item.title }}</span>
    </NBreadcrumbItem>
  </NBreadcrumb>
</template>

<style scoped>
.app-breadcrumb {
  margin-bottom: 20px;
}

.breadcrumb-link {
  color: inherit;
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: var(--n-text-color-hover);
}
</style>
