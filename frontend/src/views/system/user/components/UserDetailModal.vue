<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { UserDetail } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'UserDetailModal' })

interface UserDetailModalProps {
  show: boolean
  loading: boolean
  item: UserDetail | null
  departmentNames: Readonly<Record<number, string>>
}

const props = defineProps<UserDetailModalProps>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const { t } = useLocale()

const displayValue = (value: string | number | null): string =>
  value === null || value === '' ? t('user.noValue') : String(value)

const formatTimestamp = (value: string | null): string =>
  value ? formatDateTime(value, { fallback: t('user.noValue') }) : t('user.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="user-detail-modal"
    :title="t('user.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('user.empty')" />
      <NDescriptions v-else-if="props.item" bordered :column="2" label-placement="left">
        <NDescriptionsItem :label="t('user.column.username')">
          {{ props.item.user.username }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.nickname')">
          {{ displayValue(props.item.user.nickname) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.phone')">
          {{ displayValue(props.item.user.phone) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.email')">
          {{ displayValue(props.item.user.email) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.department')">
          {{
            props.departmentNames[props.item.user.dept_id ?? 0] ??
            displayValue(props.item.user.dept_id)
          }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.status')">
          <NTag :type="props.item.user.status === '1' ? 'success' : 'default'" size="small">
            {{
              props.item.user.status === '1' ? t('user.status.enabled') : t('user.status.disabled')
            }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.column.createTime')">
          {{ formatTimestamp(props.item.user.create_time) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.detail.posts')">
          {{ props.item.posts.map((post) => post.post_name).join('、') || t('user.noValue') }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('user.detail.roles')" :span="2">
          {{ props.item.roles.map((role) => role.name).join('、') || t('user.noValue') }}
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.user-detail-modal {
  width: min(640px, calc(100vw - 32px));
}
</style>
