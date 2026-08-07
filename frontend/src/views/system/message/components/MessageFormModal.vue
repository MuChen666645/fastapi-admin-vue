<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type {
  AppFormField,
  MessageDeliveryChannel,
  MessageFormMode,
  MessageFormModel,
} from '@/types'

defineOptions({ name: 'MessageFormModal' })

interface MessageFormModalProps {
  show: boolean
  mode: MessageFormMode
  model: MessageFormModel
  loading: boolean
}

const props = defineProps<MessageFormModalProps>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: MessageFormModel]
  reset: []
}>()

const { t } = useLocale()

const messageTypeOptions = computed(() => [
  { label: t('message.type.system'), value: 'system' as const },
  { label: t('message.type.approval'), value: 'approval' as const },
  { label: t('message.type.alarm'), value: 'alarm' as const },
])

const formStatusOptions = computed(() => [
  { label: t('message.status.enabled'), value: '1' as const },
  { label: t('message.status.disabled'), value: '0' as const },
])

const channelOptions = computed<Array<{ label: string; value: MessageDeliveryChannel }>>(() => [
  { label: t('message.form.channel.inbox'), value: 'inbox' },
  { label: t('message.form.channel.webhook'), value: 'webhook' },
  { label: t('message.form.channel.email'), value: 'email' },
  { label: t('message.form.channel.sms'), value: 'sms' },
])

const fields = computed<ReadonlyArray<AppFormField<MessageFormModel>>>(() => [
  {
    key: 'message_title',
    path: 'message_title',
    label: t('message.form.title'),
    required: true,
    requiredMessage: t('message.form.titlePlaceholder'),
    componentProps: { placeholder: t('message.form.titlePlaceholder') },
  },
  {
    key: 'message_type',
    path: 'message_type',
    label: t('message.form.type'),
    type: 'select',
    required: true,
    requiredMessage: t('message.form.typePlaceholder'),
    componentProps: {
      options: messageTypeOptions.value,
      placeholder: t('message.form.typePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('message.form.status'),
    type: 'select',
    required: true,
    requiredMessage: t('message.form.statusPlaceholder'),
    componentProps: {
      options: formStatusOptions.value,
      placeholder: t('message.form.statusPlaceholder'),
    },
  },
  {
    key: 'publish_time',
    path: 'publish_time',
    label: t('message.form.publishTime'),
    type: 'date',
    componentProps: { type: 'datetime', clearable: true },
  },
  {
    key: 'message_content',
    path: 'message_content',
    label: t('message.form.content'),
    type: 'textarea',
    required: true,
    requiredMessage: t('message.form.contentPlaceholder'),
    componentProps: {
      rows: 6,
      placeholder: t('message.form.contentPlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'recipient_user_ids',
    path: 'recipient_user_ids',
    label: t('message.form.recipientIds'),
    hidden: () => props.mode !== 'create',
    feedback: t('message.form.recipientIdsHelp'),
    componentProps: { placeholder: t('message.form.recipientIdsPlaceholder') },
    span: '1 s:2',
  },
  {
    key: 'delivery_channels',
    path: 'delivery_channels',
    label: t('message.form.channels'),
    type: 'select',
    hidden: () => props.mode !== 'create',
    required: true,
    requiredMessage: t('message.form.channels'),
    rules: [
      { type: 'array', required: true, message: t('message.form.channels'), trigger: 'change' },
    ],
    componentProps: { multiple: true, options: channelOptions.value },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => {
  emit('update:show', value)
}

const handleCancel = (): void => {
  emit('update:show', false)
}

const handleReset = (): void => {
  emit('reset')
}

const handleSubmit = (model: MessageFormModel): void => {
  emit('submit', model)
}
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="message-modal"
    :title="props.mode === 'create' ? t('message.createTitle') : t('message.editTitle')"
    :mask-closable="false"
    @update:show="handleShowUpdate"
    @after-leave="handleReset"
  >
    <!-- @vue-generic {MessageFormModel} -->
    <AppForm
      :model="props.model"
      :fields="fields"
      :loading="props.loading"
      :show-reset="false"
      :layout="{
        labelPlacement: 'top',
        columns: '1 s:2',
        responsive: 'screen',
        xGap: 16,
        yGap: 4,
      }"
      @submit="handleSubmit"
    >
      <template #actions="{ loading: actionLoading, submit }">
        <NButton attr-type="button" :disabled="actionLoading" @click="handleCancel">
          {{ t('message.form.cancel') }}
        </NButton>
        <NButton
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('message.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.message-modal {
  width: min(760px, calc(100vw - 32px));
}
</style>
