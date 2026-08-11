<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { PostDetailModalProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'PostDetailModal' })

const props = defineProps<PostDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('post.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="post-detail-modal"
    :title="t('post.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('post.empty')" />
      <NDescriptions
        v-else-if="props.item"
        bordered
        :column="2"
        label-placement="left"
        size="small"
      >
        <NDescriptionsItem :label="t('post.form.code')">
          {{ props.item.post_code }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.form.name')">
          {{ props.item.post_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.form.sort')">
          {{ props.item.post_sort }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.form.status')">
          <NTag :type="props.item.status === '1' ? 'success' : 'default'" size="small">
            {{ props.item.status === '1' ? t('post.status.enabled') : t('post.status.disabled') }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.form.remark')" :span="2">
          {{ displayValue(props.item.remark) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.detail.createTime')">
          {{ formatDateTime(props.item.create_time, { fallback: t('post.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('post.detail.updateTime')">
          {{ formatDateTime(props.item.update_time, { fallback: t('post.noValue') }) }}
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.post-detail-modal {
  width: min(700px, calc(100vw - 32px));
}
</style>
