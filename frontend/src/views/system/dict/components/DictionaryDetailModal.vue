<script setup lang="ts">
import { computed } from 'vue'
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { DictDataDetail, DictTypeDetail, DictionaryStatus } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'DictionaryDetailModal' })

type DictionaryDetailItem = DictTypeDetail | DictDataDetail

interface DictionaryDetailModalProps {
  show: boolean
  loading: boolean
  kind: 'type' | 'data'
  item: DictionaryDetailItem | null
}

const props = defineProps<DictionaryDetailModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const { t } = useLocale()

const typeItem = computed<DictTypeDetail | null>(() =>
  props.kind === 'type' && props.item ? (props.item as DictTypeDetail) : null,
)
const dataItem = computed<DictDataDetail | null>(() =>
  props.kind === 'data' && props.item ? (props.item as DictDataDetail) : null,
)

const display = (value: string | number | null | undefined): string =>
  value === null || value === undefined || value === '' ? t('dict.noValue') : String(value)

const statusLabel = (value: DictionaryStatus): string =>
  value === '1' ? t('dict.status.enabled') : t('dict.status.disabled')

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="dict-detail-modal"
    :title="props.kind === 'type' ? t('dict.type.detailTitle') : t('dict.data.detailTitle')"
    @update:show="handleShowUpdate"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('dict.noValue')" />
      <NDescriptions v-else-if="props.item" bordered :column="2" label-placement="left">
        <template v-if="typeItem">
          <NDescriptionsItem :label="t('dict.type.form.name')">
            {{ typeItem.dict_name }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.type.form.code')">
            {{ typeItem.dict_type }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.type.form.status')">
            <NTag size="small">{{ statusLabel(typeItem.status) }}</NTag>
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.type.form.remark')">
            {{ display(typeItem.remark) }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.detail.createTime')">
            {{ formatDateTime(typeItem.create_time, { fallback: t('dict.noValue') }) }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.detail.updateTime')">
            {{ formatDateTime(typeItem.update_time, { fallback: t('dict.noValue') }) }}
          </NDescriptionsItem>
        </template>
        <template v-else-if="dataItem">
          <NDescriptionsItem :label="t('dict.data.form.sort')">
            {{ dataItem.dict_sort }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.data.form.type')">
            {{ dataItem.dict_type }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.data.form.label')">
            {{ dataItem.dict_label }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.data.form.value')">
            {{ dataItem.dict_value }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.data.form.status')">
            <NTag size="small">{{ statusLabel(dataItem.status) }}</NTag>
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.data.form.remark')">
            {{ display(dataItem.remark) }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.detail.createTime')">
            {{ formatDateTime(dataItem.create_time, { fallback: t('dict.noValue') }) }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('dict.detail.updateTime')">
            {{ formatDateTime(dataItem.update_time, { fallback: t('dict.noValue') }) }}
          </NDescriptionsItem>
        </template>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.dict-detail-modal {
  width: min(720px, calc(100vw - 32px));
}
</style>
