<script setup lang="ts">
import { computed } from 'vue'
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { RoleDataScope, RoleDetail } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'RoleDetailModal' })

interface RoleDetailModalProps {
  show: boolean
  loading: boolean
  item: RoleDetail | null
}

const props = defineProps<RoleDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const dataScopeLabel = computed(() => {
  const value = props.item?.data_scope
  switch (value as RoleDataScope | undefined) {
    case '1':
      return t('role.dataScope.all')
    case '2':
      return t('role.dataScope.custom')
    case '3':
      return t('role.dataScope.current')
    case '4':
      return t('role.dataScope.currentAndBelow')
    default:
      return t('role.dataScope.self')
  }
})
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="role-detail-modal"
    :title="t('role.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item" :description="t('role.form.noOptions')" />
      <template v-else>
        <NDescriptions bordered :column="2" label-placement="left" size="small">
          <NDescriptionsItem :label="t('role.column.name')">{{
            props.item.name
          }}</NDescriptionsItem>
          <NDescriptionsItem :label="t('role.column.code')">{{
            props.item.code
          }}</NDescriptionsItem>
          <NDescriptionsItem :label="t('role.column.description')" :span="2">
            {{ props.item.description || t('role.noValue') }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('role.column.dataScope')">{{
            dataScopeLabel
          }}</NDescriptionsItem>
          <NDescriptionsItem :label="t('role.column.status')">
            <NTag :type="props.item.status === '1' ? 'success' : 'default'" size="small">
              {{ props.item.status === '1' ? t('role.status.enabled') : t('role.status.disabled') }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('role.column.updateTime')" :span="2">
            {{ formatDateTime(props.item.update_time, { fallback: t('role.noValue') }) }}
          </NDescriptionsItem>
        </NDescriptions>
        <div class="role-detail-groups">
          <div>
            <span>{{ t('role.detail.menuCount') }}</span>
            <strong>{{ props.item.menu_ids.length }}</strong>
          </div>
          <div>
            <span>{{ t('role.detail.departmentCount') }}</span>
            <strong>{{ props.item.dept_ids.length }}</strong>
          </div>
          <div>
            <span>{{ t('role.detail.fieldPermissions') }}</span>
            <strong>{{ props.item.field_permission_codes.length }}</strong>
          </div>
        </div>
      </template>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.role-detail-modal {
  width: min(620px, calc(100vw - 32px));
}

.role-detail-groups {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.role-detail-groups > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--app-color-border);
  border-radius: 6px;
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.role-detail-groups strong {
  color: var(--app-color-text);
  font-size: 16px;
}

@media (width <= 560px) {
  .role-detail-groups {
    grid-template-columns: 1fr;
  }
}
</style>
