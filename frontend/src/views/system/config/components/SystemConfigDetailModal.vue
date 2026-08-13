<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { SystemConfigDetailModalProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'SystemConfigDetailModal' })

const props = defineProps<SystemConfigDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('systemConfig.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="system-config-detail-modal"
    :title="t('systemConfig.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('systemConfig.empty')" />
      <NDescriptions
        v-else-if="props.item"
        bordered
        :column="2"
        label-placement="left"
        size="small"
      >
        <NDescriptionsItem :label="t('systemConfig.column.name')">
          {{ props.item.config_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.column.key')">
          {{ props.item.config_key }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.column.type')">
          {{ props.item.config_type }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.column.builtin')">
          <NTag v-if="props.item.is_builtin" size="small" type="info">
            {{ t('systemConfig.action.builtin') }}
          </NTag>
          <span v-else>-</span>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.column.value')" :span="2">
          <pre class="system-config-detail-value">{{ displayValue(props.item.config_value) }}</pre>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.column.remark')" :span="2">
          {{ displayValue(props.item.remark) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.detail.createTime')">
          {{ formatDateTime(props.item.create_time, { fallback: t('systemConfig.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('systemConfig.detail.updateTime')">
          {{ formatDateTime(props.item.update_time, { fallback: t('systemConfig.noValue') }) }}
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.system-config-detail-modal {
  width: min(720px, calc(100vw - 32px));
}

.system-config-detail-value {
  max-height: 200px;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
}
</style>
