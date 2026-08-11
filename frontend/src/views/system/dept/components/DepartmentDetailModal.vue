<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { DepartmentDetailModalProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'DepartmentDetailModal' })

const props = defineProps<DepartmentDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('department.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="department-detail-modal"
    :title="t('department.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item" :description="t('department.empty')" />
      <NDescriptions v-else bordered :column="2" label-placement="left" size="small">
        <NDescriptionsItem :label="t('department.form.name')">
          {{ props.item.dept_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.parent')">
          {{ props.parentName }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.leader')">
          {{ displayValue(props.item.leader) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.phone')">
          {{ displayValue(props.item.phone) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.email')" :span="2">
          {{ displayValue(props.item.email) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.sort')">
          {{ props.item.order_num }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.form.status')">
          <NTag :type="props.item.status === '1' ? 'success' : 'default'" size="small">
            {{
              props.item.status === '1'
                ? t('department.status.enabled')
                : t('department.status.disabled')
            }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.detail.createTime')">
          {{ formatDateTime(props.item.create_time, { fallback: t('department.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('department.detail.updateTime')">
          {{ formatDateTime(props.item.update_time, { fallback: t('department.noValue') }) }}
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.department-detail-modal {
  width: min(700px, calc(100vw - 32px));
}
</style>
