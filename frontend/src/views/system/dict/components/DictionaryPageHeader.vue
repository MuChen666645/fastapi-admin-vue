<script setup lang="ts">
import { computed, ref } from 'vue'
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

defineOptions({ name: 'DictionaryPageHeader' })

interface DictionaryPageHeaderProps {
  kind: 'type' | 'data'
  total: string
  refreshLoading: boolean
  exportLoading?: boolean
  importLoading?: boolean
}

const props = withDefaults(defineProps<DictionaryPageHeaderProps>(), {
  exportLoading: false,
  importLoading: false,
})
const emit = defineEmits<{
  create: []
  refresh: []
  export: []
  import: [file: File]
}>()

const { t } = useLocale()
const uploadRef = ref<AppUploadExposed | null>(null)

const title = computed(() => (props.kind === 'type' ? t('dict.type.title') : t('dict.data.title')))
const description = computed(() =>
  props.kind === 'type' ? t('dict.type.description') : t('dict.data.description'),
)
const createText = computed(() =>
  props.kind === 'type' ? t('dict.type.action.create') : t('dict.data.action.create'),
)
const showFileActions = computed(() => props.kind === 'type')

const handleFileChange = (payload: AppUploadChangePayload): void => {
  const file = payload.file.file
  uploadRef.value?.clear()
  if (file) {
    emit('import', file)
  }
}
</script>

<template>
  <header class="dict-list-heading">
    <div>
      <h2 :id="`${props.kind}-dict-list-title`">{{ title }}</h2>
      <p>{{ description }}</p>
    </div>
    <div class="dict-page-actions">
      <NButton v-permission="'system:dict:add'" type="primary" @click="emit('create')">
        <template #icon
          ><NIcon><AddOutline /></NIcon
        ></template>
        {{ createText }}
      </NButton>
      <AppUpload
        v-if="showFileActions"
        ref="uploadRef"
        :default-upload="false"
        :show-file-list="false"
        :max="1"
        accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        :disabled="props.importLoading || props.exportLoading"
        @change="handleFileChange"
      >
        <NButton
          v-permission="'system:dict:add'"
          secondary
          :loading="props.importLoading"
          :disabled="props.exportLoading"
        >
          <template #icon
            ><NIcon><CloudUploadOutline /></NIcon
          ></template>
          {{ t('dict.action.import') }}
        </NButton>
      </AppUpload>
      <NButton
        v-if="showFileActions"
        v-permission="'system:dict:list'"
        secondary
        :loading="props.exportLoading"
        :disabled="props.importLoading"
        @click="emit('export')"
      >
        <template #icon
          ><NIcon><CloudDownloadOutline /></NIcon
        ></template>
        {{ t('dict.action.export') }}
      </NButton>
      <NButton
        v-permission="'system:dict:list'"
        quaternary
        circle
        :loading="props.refreshLoading"
        :aria-label="t('dict.refresh')"
        :title="t('dict.refresh')"
        @click="emit('refresh')"
      >
        <template #icon
          ><NIcon><RefreshOutline /></NIcon
        ></template>
      </NButton>
      <span class="dict-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.dict-list-heading,
.dict-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dict-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.dict-list-heading h2,
.dict-list-heading p,
.dict-total {
  margin: 0;
}

.dict-list-heading h2 {
  font-size: 16px;
}

.dict-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.dict-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.dict-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.dict-page-actions :deep(.app-upload) {
  display: inline-flex;
}

@media (width <= 720px) {
  .dict-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .dict-page-actions {
    justify-content: flex-start;
  }
}
</style>
