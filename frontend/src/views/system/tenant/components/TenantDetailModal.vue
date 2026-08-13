<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { TenantDetailModalProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'TenantDetailModal' })

const props = defineProps<TenantDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('tenant.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="tenant-detail-modal"
    :title="t('tenant.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NEmpty v-if="!props.item" :description="t('tenant.empty')" />
    <NDescriptions v-else bordered :column="2" label-placement="left" size="small">
      <NDescriptionsItem :label="t('tenant.column.code')">{{ props.item.code }}</NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.column.name')">{{ props.item.name }}</NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.column.status')">
        <NTag :type="props.item.status === '1' ? 'success' : 'default'" size="small">
          {{ props.item.status === '1' ? t('tenant.status.enabled') : t('tenant.status.disabled') }}
        </NTag>
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.column.version')">{{
        props.item.version
      }}</NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.column.description')" :span="2">
        {{ displayValue(props.item.description) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.detail.createTime')">
        {{ formatDateTime(props.item.create_time, { fallback: t('tenant.noValue') }) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('tenant.detail.updateTime')">
        {{ formatDateTime(props.item.update_time, { fallback: t('tenant.noValue') }) }}
      </NDescriptionsItem>
    </NDescriptions>
  </NModal>
</template>

<style lang="scss">
.n-card.tenant-detail-modal {
  width: min(680px, calc(100vw - 32px));
}
</style>
