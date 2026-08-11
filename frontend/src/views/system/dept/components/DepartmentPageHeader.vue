<script setup lang="ts">
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { DepartmentPageHeaderProps } from '@/types'

defineOptions({ name: 'DepartmentPageHeader' })

const props = defineProps<DepartmentPageHeaderProps>()
const emit = defineEmits<{
  create: []
  refresh: []
}>()

const { t } = useLocale()
</script>

<template>
  <header class="department-list-heading">
    <div>
      <h2 id="department-list-title">{{ props.title }}</h2>
      <p>{{ props.description }}</p>
    </div>
    <div class="department-page-actions">
      <NButton
        v-if="props.permissions.create"
        v-permission="'system:dept:add'"
        type="primary"
        size="medium"
        @click="emit('create')"
      >
        <template #icon>
          <NIcon><AddOutline /></NIcon>
        </template>
        {{ t('department.action.create') }}
      </NButton>
      <NButton
        v-if="props.permissions.list"
        v-permission="'system:dept:list'"
        quaternary
        circle
        size="medium"
        :loading="props.refreshLoading"
        :aria-label="t('department.refresh')"
        :title="t('department.refresh')"
        @click="emit('refresh')"
      >
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
      </NButton>
      <span class="department-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.department-list-heading,
.department-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.department-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.department-list-heading h2,
.department-list-heading p,
.department-total {
  margin: 0;
}

.department-list-heading h2 {
  font-size: 16px;
}

.department-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.department-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.department-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 720px) {
  .department-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .department-page-actions {
    justify-content: flex-start;
  }
}
</style>
