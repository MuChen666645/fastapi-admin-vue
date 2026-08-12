<script setup lang="ts">
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { ScheduledJobPageHeaderProps } from '@/types'

defineOptions({ name: 'JobPageHeader' })

const props = defineProps<ScheduledJobPageHeaderProps>()
const emit = defineEmits<{ create: []; refresh: [] }>()
const { t } = useLocale()
</script>

<template>
  <header class="job-list-heading">
    <div>
      <h2 id="job-list-title">{{ props.title }}</h2>
      <p>{{ props.description }}</p>
    </div>
    <div class="job-page-actions">
      <NButton
        v-if="props.permissions.create"
        v-permission="'monitor:job:add'"
        type="primary"
        @click="emit('create')"
      >
        <template #icon
          ><NIcon><AddOutline /></NIcon
        ></template>
        {{ t('job.action.create') }}
      </NButton>
      <NButton
        v-if="props.permissions.list"
        v-permission="'monitor:job:list'"
        quaternary
        circle
        :loading="props.refreshLoading"
        :aria-label="t('job.refresh')"
        :title="t('job.refresh')"
        @click="emit('refresh')"
      >
        <template #icon
          ><NIcon><RefreshOutline /></NIcon
        ></template>
      </NButton>
      <span class="job-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.job-list-heading,
.job-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.job-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.job-list-heading h2,
.job-list-heading p,
.job-total {
  margin: 0;
}

.job-list-heading h2 {
  font-size: 16px;
}

.job-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.job-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.job-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 720px) {
  .job-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .job-page-actions {
    justify-content: flex-start;
  }
}
</style>
