<script setup lang="ts">
import { computed } from 'vue'
import { NDescriptions, NDescriptionsItem, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { MenuDetail, MenuType } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'MenuDetailModal' })

interface MenuDetailModalProps {
  show: boolean
  loading: boolean
  item: MenuDetail | null
}

const props = defineProps<MenuDetailModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const { t } = useLocale()

const typeLabel = computed(() => {
  const value = props.item?.menu_type
  if (!value) {
    return t('menuManagement.noValue')
  }

  const labels: Record<MenuType, string> = {
    C: t('menuManagement.type.router'),
    F: t('menuManagement.type.button'),
    L: t('menuManagement.type.link'),
    I: t('menuManagement.type.iframe'),
  }
  return labels[value]
})

const display = (value: string | number | null | undefined): string =>
  value === null || value === undefined || value === ''
    ? t('menuManagement.noValue')
    : String(value)

const flagLabel = (value: '0' | '1' | null | undefined): string =>
  value === '1'
    ? t('menuManagement.flag.yes')
    : value === '0'
      ? t('menuManagement.flag.no')
      : t('menuManagement.noValue')

const statusLabel = (value: '0' | '1' | undefined): string =>
  value === '1' ? t('menuManagement.status.enabled') : t('menuManagement.status.disabled')

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="menu-detail-modal"
    :title="t('menuManagement.detailTitle')"
    @update:show="handleShowUpdate"
  >
    <NSpin :show="props.loading">
      <NDescriptions v-if="props.item" bordered :column="2" label-placement="left">
        <NDescriptionsItem :label="t('menuManagement.form.name')">
          {{ props.item.menu_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.type')">
          <NTag size="small">{{ typeLabel }}</NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.parent')">
          {{ display(props.item.parent_id) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.path')">
          {{ display(props.item.menu_path) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.component')">
          {{ display(props.item.component) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.permission')">
          {{ display(props.item.perms) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.icon')">
          {{ display(props.item.icon) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.sort')">
          {{ display(props.item.sort) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.cache')">
          {{ flagLabel(props.item.is_cache) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.hidden')">
          {{ flagLabel(props.item.is_hidden) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.status')">
          {{ statusLabel(props.item.status) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.linkUrl')">
          {{ display(props.item.link_url) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.form.remark')" :span="2">
          {{ display(props.item.remark) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.detail.createTime')">
          {{ formatDateTime(props.item.create_time, { fallback: t('menuManagement.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('menuManagement.detail.updateTime')">
          {{ formatDateTime(props.item.update_time, { fallback: t('menuManagement.noValue') }) }}
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.menu-detail-modal {
  width: min(760px, calc(100vw - 32px));
}
</style>
