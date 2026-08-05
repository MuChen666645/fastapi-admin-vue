<script setup lang="ts">
import { computed, ref, useAttrs } from 'vue'
import { CloudUploadOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NUpload, NUploadDragger } from 'naive-ui'
import type { UploadInst } from 'naive-ui'

import type {
  AppUploadBeforeRemove,
  AppUploadBeforeUpload,
  AppUploadChangePayload,
  AppUploadDownloadFile,
  AppUploadErrorPayload,
  AppUploadExposed,
  AppUploadFileList,
  AppUploadFinishPayload,
  AppUploadOnDownload,
  AppUploadOnError,
  AppUploadOnFinish,
  AppUploadOnPreview,
  AppUploadOnRetry,
  AppUploadPreviewDetail,
  AppUploadPreviewFile,
  AppUploadProps,
  AppUploadRemovePayload,
  AppUploadRetryPayload,
  AppUploadValidationError,
} from '@/types'

defineOptions({ name: 'AppUpload', inheritAttrs: false })

const props = withDefaults(defineProps<AppUploadProps>(), {
  dragger: false,
  buttonText: '选择文件',
  tip: '',
  sizeErrorText: '文件大小不能超过 {size}',
})

const emit = defineEmits<{
  'update:fileList': [fileList: AppUploadFileList]
  change: [payload: AppUploadChangePayload]
  remove: [payload: AppUploadRemovePayload]
  finish: [payload: AppUploadFinishPayload]
  error: [payload: AppUploadErrorPayload]
  retry: [payload: AppUploadRetryPayload]
  download: [file: AppUploadDownloadFile]
  preview: [file: AppUploadPreviewFile, detail: AppUploadPreviewDetail]
  'validation-error': [payload: AppUploadValidationError]
}>()

const attrs = useAttrs()
const uploadRef = ref<UploadInst | null>(null)
const nativeUploadProps = computed(() => ({ ...attrs }))

const sizeLimit = computed(() => {
  const value = props.maxSize
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null
})

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  const units = ['KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = -1

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }

  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unitIndex]}`
}

const getSizeErrorMessage = (maxSize: number): string =>
  props.sizeErrorText.replace('{size}', formatFileSize(maxSize))

const handleFileListUpdate = (fileList: AppUploadFileList): void => {
  emit('update:fileList', fileList)
}

const handleChange = (payload: AppUploadChangePayload): void => {
  emit('change', payload)
}

const handleBeforeUpload: AppUploadBeforeUpload = async (payload) => {
  const maxSize = sizeLimit.value
  if (maxSize !== null && payload.file.file && payload.file.file.size > maxSize) {
    emit('validation-error', {
      file: payload.file,
      reason: 'size',
      maxSize,
      message: getSizeErrorMessage(maxSize),
    })
    return false
  }

  return props.beforeUpload?.(payload)
}

const handleRemove: AppUploadBeforeRemove = async (payload) => {
  const allowed = await props.beforeRemove?.(payload)
  if (allowed === false) {
    return false
  }

  emit('remove', payload)
  return true
}

const handleFinish: AppUploadOnFinish = (payload) => {
  const nextFile = props.onFinish?.(payload)
  emit('finish', payload)
  return nextFile
}

const handleError: AppUploadOnError = (payload) => {
  const nextFile = props.onError?.(payload)
  emit('error', payload)
  return nextFile
}

const handleRetry: AppUploadOnRetry = async (payload) => {
  const result = await props.onRetry?.(payload)
  emit('retry', payload)
  return result ?? true
}

const handleDownload: AppUploadOnDownload = async (file) => {
  const result = await props.onDownload?.(file)
  emit('download', file)
  return result ?? true
}

const handlePreview: AppUploadOnPreview = (file, detail) => {
  props.onPreview?.(file, detail)
  emit('preview', file, detail)
}

const open = (): void => {
  uploadRef.value?.openOpenFileDialog()
}

const submit: UploadInst['submit'] = (options) => {
  uploadRef.value?.submit(options)
}

const clear = (): void => {
  uploadRef.value?.clear()
  emit('update:fileList', [])
}

defineExpose<AppUploadExposed>({ open, submit, clear })
</script>

<template>
  <div class="app-upload">
    <NUpload
      ref="uploadRef"
      v-bind="nativeUploadProps"
      :file-list="fileList"
      :default-file-list="defaultFileList"
      :on-update:file-list="handleFileListUpdate"
      :on-change="handleChange"
      :on-before-upload="handleBeforeUpload"
      :on-remove="handleRemove"
      :on-finish="handleFinish"
      :on-error="handleError"
      :on-retry="handleRetry"
      :on-download="handleDownload"
      :on-preview="handlePreview"
    >
      <template #default>
        <NUploadDragger v-if="dragger">
          <slot>
            <div class="app-upload__dragger-content">
              <NIcon :size="28" aria-hidden="true"><CloudUploadOutline /></NIcon>
              <span>{{ buttonText }}</span>
            </div>
          </slot>
        </NUploadDragger>
        <slot v-else>
          <NButton attr-type="button" type="primary">
            <template #icon>
              <NIcon><CloudUploadOutline /></NIcon>
            </template>
            {{ buttonText }}
          </NButton>
        </slot>
      </template>
    </NUpload>

    <div v-if="tip || $slots.tip" class="app-upload__tip">
      <slot name="tip">{{ tip }}</slot>
    </div>
  </div>
</template>

<style scoped>
.app-upload {
  min-width: 0;
}

.app-upload__dragger-content {
  display: grid;
  justify-items: center;
  gap: 8px;
  color: var(--app-color-text-muted);
}

.app-upload__tip {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 12px;
  line-height: 1.5;
}
</style>
