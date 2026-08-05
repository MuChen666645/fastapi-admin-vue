import type { UploadFileInfo, UploadInst, UploadProps, UploadSettledFileInfo } from 'naive-ui'

type AppUploadHandledProp =
  | 'fileList'
  | 'defaultFileList'
  | 'onUpdate:fileList'
  | 'onChange'
  | 'onRemove'
  | 'onFinish'
  | 'onError'
  | 'onRetry'
  | 'onBeforeUpload'
  | 'onDownload'
  | 'onPreview'

export type AppUploadFileList = UploadFileInfo[]
export type AppUploadBeforeUpload = NonNullable<UploadProps['onBeforeUpload']>
export type AppUploadBeforeRemove = NonNullable<UploadProps['onRemove']>
export type AppUploadOnFinish = NonNullable<UploadProps['onFinish']>
export type AppUploadOnError = NonNullable<UploadProps['onError']>
export type AppUploadOnRetry = NonNullable<UploadProps['onRetry']>
export type AppUploadOnDownload = NonNullable<UploadProps['onDownload']>
export type AppUploadOnPreview = NonNullable<UploadProps['onPreview']>

export type AppUploadChangePayload = Parameters<NonNullable<UploadProps['onChange']>>[0]
export type AppUploadRemovePayload = Parameters<AppUploadBeforeRemove>[0]
export type AppUploadFinishPayload = Parameters<AppUploadOnFinish>[0]
export type AppUploadErrorPayload = Parameters<AppUploadOnError>[0]
export type AppUploadRetryPayload = Parameters<AppUploadOnRetry>[0]
export type AppUploadPreviewFile = Parameters<AppUploadOnPreview>[0]
export type AppUploadPreviewDetail = Parameters<AppUploadOnPreview>[1]
export type AppUploadDownloadFile = Parameters<AppUploadOnDownload>[0]

export interface AppUploadProps extends /* @vue-ignore */ Omit<UploadProps, AppUploadHandledProp> {
  fileList?: AppUploadFileList
  defaultFileList?: AppUploadFileList
  dragger?: boolean
  buttonText?: string
  tip?: string
  maxSize?: number
  sizeErrorText?: string
  beforeUpload?: AppUploadBeforeUpload
  beforeRemove?: AppUploadBeforeRemove
  onFinish?: AppUploadOnFinish
  onError?: AppUploadOnError
  onRetry?: AppUploadOnRetry
  onDownload?: AppUploadOnDownload
  onPreview?: AppUploadOnPreview
}

export type AppUploadValidationReason = 'size'

export interface AppUploadValidationError {
  file: UploadSettledFileInfo
  reason: AppUploadValidationReason
  maxSize: number
  message: string
}

export interface AppUploadExposed {
  open: UploadInst['openOpenFileDialog']
  submit: UploadInst['submit']
  clear: UploadInst['clear']
}
