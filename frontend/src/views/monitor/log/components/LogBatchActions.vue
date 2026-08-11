<script setup lang="ts">
import { TrashOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { LogBatchActionsProps } from '@/types'

defineOptions({ name: 'LogBatchActions' })

const props = defineProps<LogBatchActionsProps>()
const emit = defineEmits<{ remove: [] }>()
const { t } = useLocale()
</script>

<template>
  <div v-if="props.selectedCount > 0" class="log-batch-actions">
    <span class="log-batch-actions__count">
      {{ t('log.selected').replace('{count}', String(props.selectedCount)) }}
    </span>
    <NButton
      v-permission="'monitor:log:remove'"
      type="error"
      size="small"
      :loading="props.loading"
      :disabled="props.disabled || props.loading"
      @click="emit('remove')"
    >
      <template #icon>
        <NIcon><TrashOutline /></NIcon>
      </template>
      {{ t('log.action.deleteSelected') }}
    </NButton>
  </div>
</template>

<style lang="scss" scoped>
.log-batch-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  padding: 10px 12px;
  border: 1px solid var(--app-color-border);
  border-radius: 6px;
  background: var(--app-color-surface-muted);
}

.log-batch-actions__count {
  margin-right: auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}
</style>
