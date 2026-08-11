<script setup lang="ts">
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { PostPageHeaderProps } from '@/types'

defineOptions({ name: 'PostPageHeader' })

const props = defineProps<PostPageHeaderProps>()
const emit = defineEmits<{
  create: []
  refresh: []
}>()

const { t } = useLocale()
</script>

<template>
  <header class="post-list-heading">
    <div>
      <h2 id="post-list-title">{{ props.title }}</h2>
      <p>{{ props.description }}</p>
    </div>
    <div class="post-page-actions">
      <NButton
        v-if="props.permissions.create"
        v-permission="'system:post:add'"
        type="primary"
        @click="emit('create')"
      >
        <template #icon>
          <NIcon><AddOutline /></NIcon>
        </template>
        {{ t('post.action.create') }}
      </NButton>
      <NButton
        v-if="props.permissions.list"
        v-permission="'system:post:list'"
        quaternary
        circle
        :loading="props.refreshLoading"
        :aria-label="t('post.refresh')"
        :title="t('post.refresh')"
        @click="emit('refresh')"
      >
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
      </NButton>
      <span class="post-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.post-list-heading,
.post-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.post-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.post-list-heading h2,
.post-list-heading p,
.post-total {
  margin: 0;
}

.post-list-heading h2 {
  font-size: 16px;
}

.post-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.post-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.post-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 720px) {
  .post-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .post-page-actions {
    justify-content: flex-start;
  }
}
</style>
