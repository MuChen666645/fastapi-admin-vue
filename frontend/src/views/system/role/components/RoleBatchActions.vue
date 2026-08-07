<script setup lang="ts">
import { CheckmarkCircleOutline, CloseCircleOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NSpace } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { RoleStatus } from '@/types'

defineOptions({ name: 'RoleBatchActions' })

interface RoleBatchActionsProps {
  selectedCount: number
  loading: boolean
}

const props = defineProps<RoleBatchActionsProps>()
const emit = defineEmits<{ status: [status: RoleStatus] }>()
const { t } = useLocale()
</script>

<template>
  <div v-if="props.selectedCount > 0" class="role-batch-actions">
    <span>{{ t('role.batchSelected').replace('{count}', String(props.selectedCount)) }}</span>
    <NSpace :size="8">
      <NButton
        v-permission="'system:role:edit'"
        secondary
        size="small"
        :loading="props.loading"
        :disabled="props.loading"
        @click="emit('status', '1')"
      >
        <template #icon
          ><NIcon><CheckmarkCircleOutline /></NIcon
        ></template>
        {{ t('role.action.batchEnable') }}
      </NButton>
      <NButton
        v-permission="'system:role:edit'"
        secondary
        size="small"
        :loading="props.loading"
        :disabled="props.loading"
        @click="emit('status', '0')"
      >
        <template #icon
          ><NIcon><CloseCircleOutline /></NIcon
        ></template>
        {{ t('role.action.batchDisable') }}
      </NButton>
    </NSpace>
  </div>
</template>

<style lang="scss" scoped>
.role-batch-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 36px;
  padding: 8px 12px;
  border: 1px solid var(--app-color-border);
  border-radius: 6px;
  background: var(--app-color-surface-soft);
  color: var(--app-color-text-muted);
  font-size: 13px;
}
</style>
