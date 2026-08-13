<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import {
  AddOutline,
  CheckmarkCircleOutline,
  CloseCircleOutline,
  RefreshOutline,
  StarOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import {
  NAlert,
  NButton,
  NDataTable,
  NEmpty,
  NIcon,
  NModal,
  NSelect,
  NSpin,
  NSwitch,
  NTag,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type {
  TenantMember,
  TenantMemberAddFormModel,
  TenantMemberModalProps,
  TenantStatus,
} from '@/types'
import { isProtectedAdminUser } from '@/utils'

defineOptions({ name: 'TenantMemberModal' })

const props = defineProps<TenantMemberModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  'update:add-model': [model: TenantMemberAddFormModel]
  add: []
  refresh: []
  status: [item: TenantMember, status: TenantStatus]
  default: [item: TenantMember]
  remove: [item: TenantMember]
}>()
const { t } = useLocale()

const memberDefaultSwitchThemeOverrides = {
  buttonHeightMedium: '30px',
  buttonWidthMedium: '30px',
  buttonWidthPressedMedium: '30px',
  railHeightMedium: '34px',
  railWidthMedium: '124px',
} as const

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const updateAddModel = (values: Partial<TenantMemberAddFormModel>): void =>
  emit('update:add-model', { ...props.addModel, ...values })

const displayValue = (value: string | null): string => value || t('tenant.noValue')

const isProtectedMember = (item: TenantMember): boolean => isProtectedAdminUser(item.username)

const memberUserIds = computed(() => new Set(props.members.map((item) => item.user_id)))

const userSelectOptions = computed(() =>
  props.userOptions.map((user) => ({
    label: user.nickname ? `${user.username}（${user.nickname}）` : user.username,
    value: user.id,
    disabled: memberUserIds.value.has(user.id),
  })),
)

const renderActions = (item: TenantMember): VNode => {
  const actions: VNode[] = []

  if (props.permissions.memberEdit && !isProtectedMember(item)) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: item.status === '1' ? 'warning' : 'success',
            'aria-label':
              item.status === '1' ? t('tenant.status.disabled') : t('tenant.status.enabled'),
            title: item.status === '1' ? t('tenant.status.disabled') : t('tenant.status.enabled'),
            onClick: () => emit('status', item, item.status === '1' ? '0' : '1'),
          },
          {
            icon: () =>
              h(NIcon, null, {
                default: () => h(item.status === '1' ? CloseCircleOutline : CheckmarkCircleOutline),
              }),
          },
        ),
        'system:tenant:member:edit',
      ),
    )
    if (!item.is_default && item.status === '1') {
      actions.push(
        withPermission(
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              'aria-label': t('tenant.member.default'),
              title: t('tenant.member.default'),
              onClick: () => emit('default', item),
            },
            { icon: () => h(NIcon, null, { default: () => h(StarOutline) }) },
          ),
          'system:tenant:member:edit',
        ),
      )
    }
  }

  if (props.permissions.memberRemove && !isProtectedMember(item)) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: 'error',
            'aria-label': t('tenant.member.action.remove'),
            title: t('tenant.member.action.remove'),
            onClick: () => emit('remove', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
        ),
        'system:tenant:member:remove',
      ),
    )
  }

  return h('div', { class: 'tenant-member-actions' }, actions)
}

const columns = computed<DataTableColumns<TenantMember>>(() => [
  {
    title: t('tenant.member.column.userId'),
    key: 'user_id',
    width: 110,
  },
  {
    title: t('tenant.member.column.username'),
    key: 'username',
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: t('tenant.member.column.nickname'),
    key: 'nickname',
    width: 150,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.nickname),
  },
  {
    title: t('tenant.member.column.status'),
    key: 'status',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { size: 'small', type: item.status === '1' ? 'success' : 'default' },
        {
          default: () =>
            item.status === '1' ? t('tenant.status.enabled') : t('tenant.status.disabled'),
        },
      ),
  },
  {
    title: t('tenant.member.column.default'),
    key: 'is_default',
    width: 110,
    render: (item) =>
      item.is_default
        ? h(
            NTag,
            { size: 'small', type: 'info' },
            { default: () => t('tenant.member.defaultMark') },
          )
        : '-',
  },
  {
    title: t('tenant.member.column.action'),
    key: 'action',
    width: 150,
    fixed: 'right',
    render: renderActions,
  },
])

const rowKey = (item: TenantMember): number => item.user_id
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="tenant-member-modal"
    :title="`${t('tenant.member.title')} - ${props.tenant?.name ?? ''}`"
    :mask-closable="false"
    @update:show="emit('update:show', $event)"
  >
    <div v-if="props.permissions.memberAdd" class="tenant-member-add">
      <NSelect
        size="medium"
        class="tenant-member-user-select"
        :value="props.addModel.user_id"
        :options="userSelectOptions"
        :loading="props.userOptionsLoading"
        :disabled="!props.canSelectUsers"
        clearable
        filterable
        :placeholder="
          props.canSelectUsers
            ? t('tenant.member.userPlaceholder')
            : t('tenant.member.userListDenied')
        "
        @update:value="updateAddModel({ user_id: $event })"
      />
      <NSwitch
        size="medium"
        class="tenant-member-default-switch"
        :theme-overrides="memberDefaultSwitchThemeOverrides"
        :value="props.addModel.is_default"
        @update:value="updateAddModel({ is_default: $event })"
      >
        <template #checked>{{ t('tenant.member.defaultMark') }}</template>
        <template #unchecked>{{ t('tenant.member.default') }}</template>
      </NSwitch>
      <NButton
        v-permission="'system:tenant:member:add'"
        size="medium"
        class="tenant-member-add-button"
        type="primary"
        :disabled="props.loading || props.userOptionsLoading || !props.canSelectUsers"
        @click="emit('add')"
      >
        <template #icon
          ><NIcon><AddOutline /></NIcon
        ></template>
        {{ t('tenant.member.action.add') }}
      </NButton>
    </div>

    <div v-if="props.loading && props.members.length === 0" class="tenant-member-loading">
      <NSpin :show="true" />
    </div>
    <NAlert v-else-if="!props.tenant" type="warning" :show-icon="false">
      {{ t('tenant.member.loadFailed') }}
    </NAlert>
    <NDataTable
      v-else
      :columns="columns"
      :data="props.members"
      :loading="props.loading"
      :scroll-x="790"
      :row-key="rowKey"
      remote
    >
      <template #empty><NEmpty :description="t('tenant.member.empty')" /></template>
    </NDataTable>

    <template #footer>
      <NButton quaternary :disabled="props.loading" @click="emit('refresh')">
        <template #icon
          ><NIcon><RefreshOutline /></NIcon
        ></template>
        {{ t('tenant.member.refresh') }}
      </NButton>
    </template>
  </NModal>
</template>

<style lang="scss">
.n-card.tenant-member-modal {
  width: min(900px, calc(100vw - 32px));
}

.tenant-member-add {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.tenant-member-add .tenant-member-user-select {
  width: min(260px, 100%);
}

.tenant-member-add .tenant-member-default-switch,
.tenant-member-add .tenant-member-add-button {
  height: 34px;
}

.tenant-member-loading {
  display: grid;
  min-height: 200px;
  place-items: center;
}

.tenant-member-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

@media (width <= 560px) {
  .tenant-member-add {
    align-items: stretch;
    flex-direction: column;
  }

  .tenant-member-add .tenant-member-user-select {
    width: 100%;
  }
}
</style>
