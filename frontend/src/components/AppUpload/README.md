# AppUpload 使用文档

`AppUpload` 是基于 Naive UI `NUpload` 的通用文件上传组件。它统一文件列表双向绑定、默认上传触发器、拖拽模式、文件大小校验、上传生命周期事件和上传实例方法，但不请求 API、不拼接上传地址，也不保存业务文件数据。

## 基础用法

```vue
<script setup lang="ts">
import { ref } from 'vue'

import AppUpload from '@/components/AppUpload/index.vue'
import type { AppUploadFileList, AppUploadValidationError } from '@/types'

const files = ref<AppUploadFileList>([])
const handleValidationError = (payload: AppUploadValidationError): void => {
  void payload
}
</script>

<template>
  <AppUpload
    v-model:file-list="files"
    action="/api/v1/files/upload"
    accept=".pdf,.png,.jpg"
    :max="5"
    :max-size="10 * 1024 * 1024"
    tip="单个文件不超过 10 MB"
    @validation-error="handleValidationError"
  />
</template>
```

示例中的 `action` 仅表示组件支持 Naive UI 的请求参数，实际页面必须替换为当前后端已核实的上传接口；也可以通过 `custom-request` 接入页面或领域层已经封装的请求。

## Props

组件继承 Naive UI `UploadProps` 的请求、列表、按钮和展示配置，以下是二次封装新增或改名后的配置：

| 属性              | 类型                    | 说明                                                          |
| ----------------- | ----------------------- | ------------------------------------------------------------- |
| `fileList`        | `AppUploadFileList`     | 受控文件列表，配合 `v-model:file-list` 使用。                 |
| `defaultFileList` | `AppUploadFileList`     | 非受控模式的初始文件列表。                                    |
| `dragger`         | `boolean`               | 使用拖拽上传触发器，默认为 `false`。                          |
| `buttonText`      | `string`                | 默认触发按钮或拖拽区域文案，默认为“选择文件”。                |
| `tip`             | `string`                | 上传控件下方的提示文案。                                      |
| `maxSize`         | `number`                | 单个文件最大字节数；不传表示不做前端大小限制。                |
| `sizeErrorText`   | `string`                | 大小校验失败文案，支持 `{size}` 占位符。                      |
| `beforeUpload`    | `AppUploadBeforeUpload` | 文件大小校验通过后的上传前异步拦截。返回 `false` 会阻止上传。 |
| `beforeRemove`    | `AppUploadBeforeRemove` | 删除前异步拦截。返回 `false` 会阻止删除。                     |

其余 `accept`、`action`、`customRequest`、`headers`、`data`、`multiple`、`max`、`listType`、`showFileList`、`disabled` 等配置继续遵循 Naive UI `NUpload` 合同。

## Events

- `update:fileList(fileList)`：文件列表变化，用于 `v-model:file-list`。
- `change(payload)`：文件选择或状态变化。
- `remove(payload)`：删除通过 `beforeRemove` 后触发。
- `finish(payload)` / `error(payload)` / `retry(payload)`：上传完成、失败和重试。
- `download(file)` / `preview(file, detail)`：下载和预览操作。
- `validation-error(payload)`：组件前端校验失败，目前包含 `reason: 'size'`、实际文件和限制大小。

`onFinish`、`onError`、`onRetry`、`onDownload` 和 `onPreview` Props 可用于保留 Naive UI 原生回调的返回值语义；页面也可以使用上述事件处理展示和业务状态。

## Slots

- 默认插槽：替换默认选择按钮或拖拽区域内容。
- `tip`：替换 `tip` 文案区域。

## 暴露方法

通过模板 ref 可以调用：

- `open()`：打开文件选择器。
- `submit(options?)`：提交待上传文件。
- `clear()`：清空上传实例并发出空文件列表更新。

## 边界

文件扩展名、MIME 和大小校验只改善交互体验，不能替代后端的类型检查、病毒扫描、权限校验和存储安全策略。组件不读取 Token，也不直接调用 `@/api`、Alova、`fetch` 或 Axios。
