<script setup lang="ts">
import { CheckmarkCircleOutline, CloseCircleOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { UserStatus } from '@/types'

defineOptions({ name: 'UserBatchActions' })

interface UserBatchActionsProps {
  selectedCount: number
  loading: boolean
}

const props = defineProps<UserBatchActionsProps>()

const emit = defineEmits<{
  status: [status: UserStatus]
  delete: []
}>()

const { t } = useLocale()
</script>

<template>
  <div v-if="props.selectedCount > 0" class="user-batch-actions" aria-live="polite">
    <span class="user-batch-actions__count">
      {{ t('user.batchSelected').replace('{count}', String(props.selectedCount)) }}
    </span>
    <NButton
      v-permission="'system:user:edit'"
      secondary
      size="small"
      :loading="props.loading"
      :disabled="props.loading"
      @click="emit('status', '1')"
    >
      <template #icon>
        <NIcon><CheckmarkCircleOutline /></NIcon>
      </template>
      {{ t('user.action.batchEnable') }}
    </NButton>
    <NButton
      v-permission="'system:user:edit'"
      secondary
      size="small"
      :loading="props.loading"
      :disabled="props.loading"
      @click="emit('status', '0')"
    >
      <template #icon>
        <NIcon><CloseCircleOutline /></NIcon>
      </template>
      {{ t('user.action.batchDisable') }}
    </NButton>
    <NButton
      v-permission="'system:user:remove'"
      secondary
      type="error"
      size="small"
      :loading="props.loading"
      :disabled="props.loading"
      @click="emit('delete')"
    >
      <template #icon>
        <NIcon><TrashOutline /></NIcon>
      </template>
      {{ t('user.action.batchDelete') }}
    </NButton>
  </div>
</template>

<style lang="scss" scoped>
.user-batch-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  padding: 10px 12px;
  border: 1px solid var(--app-color-border);
  border-radius: 6px;
  background: var(--app-color-surface-muted);
}

.user-batch-actions__count {
  margin-right: auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 640px) {
  .user-batch-actions {
    align-items: stretch;
    flex-wrap: wrap;
  }

  .user-batch-actions__count {
    flex: 1 0 100%;
  }
}
</style>
