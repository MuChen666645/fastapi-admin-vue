<script setup lang="ts">
import { ref } from 'vue'
import {
  AddOutline,
  CloudDownloadOutline,
  CloudUploadOutline,
  RefreshOutline,
} from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'

import AppUpload from '@/components/AppUpload/index.vue'
import { useLocale } from '@/hooks'
import type { AppUploadChangePayload, AppUploadExposed } from '@/types'

defineOptions({ name: 'RolePageHeader' })

interface RolePageHeaderProps {
  title: string
  description: string
  total: string
  refreshLoading: boolean
  exportLoading: boolean
  importLoading: boolean
}

const props = defineProps<RolePageHeaderProps>()
const emit = defineEmits<{
  create: []
  refresh: []
  export: []
  import: [file: File]
}>()

const { t } = useLocale()
const uploadRef = ref<AppUploadExposed | null>(null)

const handleFileChange = (payload: AppUploadChangePayload): void => {
  const file = payload.file.file
  uploadRef.value?.clear()
  if (file) {
    emit('import', file)
  }
}
</script>

<template>
  <header class="role-list-heading">
    <div>
      <h2 id="role-list-title">{{ props.title }}</h2>
      <p>{{ props.description }}</p>
    </div>
    <div class="role-page-actions">
      <NButton
        v-permission="'system:role:add'"
        type="primary"
        size="medium"
        @click="emit('create')"
      >
        <template #icon
          ><NIcon><AddOutline /></NIcon
        ></template>
        {{ t('role.action.create') }}
      </NButton>
      <AppUpload
        ref="uploadRef"
        :default-upload="false"
        :show-file-list="false"
        :max="1"
        accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        :disabled="props.importLoading || props.exportLoading"
        @change="handleFileChange"
      >
        <NButton
          v-permission="'system:role:add'"
          secondary
          size="medium"
          :loading="props.importLoading"
          :disabled="props.exportLoading"
        >
          <template #icon
            ><NIcon><CloudUploadOutline /></NIcon
          ></template>
          {{ t('role.action.import') }}
        </NButton>
      </AppUpload>
      <NButton
        v-permission="'system:role:list'"
        secondary
        size="medium"
        :loading="props.exportLoading"
        :disabled="props.importLoading"
        @click="emit('export')"
      >
        <template #icon
          ><NIcon><CloudDownloadOutline /></NIcon
        ></template>
        {{ t('role.action.export') }}
      </NButton>
      <NButton
        v-permission="'system:role:list'"
        quaternary
        circle
        size="medium"
        :loading="props.refreshLoading"
        :aria-label="t('role.refresh')"
        :title="t('role.refresh')"
        @click="emit('refresh')"
      >
        <template #icon
          ><NIcon><RefreshOutline /></NIcon
        ></template>
      </NButton>
      <span class="role-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.role-list-heading,
.role-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.role-list-heading h2,
.role-list-heading p,
.role-total {
  margin: 0;
}

.role-list-heading h2 {
  font-size: 16px;
}

.role-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.role-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.role-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.role-page-actions :deep(.app-upload) {
  display: inline-flex;
}

@media (width <= 720px) {
  .role-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .role-page-actions {
    justify-content: flex-start;
  }
}
</style>
