# DictTag

`DictTag` 将字典数据中的 `dict_value` 映射为 `dict_label`，使用 Naive UI `NTag` 展示。组件只负责展示，不请求接口、不读取 Store，也不决定权限。

组件由字典插件全局注册，业务组件通常不需要手工导入。

## Props

| Prop        | 类型                                                          | 默认值      | 说明                             |
| ----------- | ------------------------------------------------------------- | ----------- | -------------------------------- |
| `options`   | `ReadonlyArray<DictDataListItem>`                             | `[]`        | `useDict` 返回的字典项。         |
| `value`     | `string \| number \| ReadonlyArray<string \| number> \| null` | `undefined` | 要映射的单值或多值。             |
| `type`      | `default \| primary \| info \| success \| warning \| error`   | `default`   | 所有已匹配标签的 Naive UI 类型。 |
| `size`      | `tiny \| small \| medium \| large`                            | `small`     | 标签尺寸。                       |
| `bordered`  | `boolean`                                                     | `true`      | 是否显示边框。                   |
| `round`     | `boolean`                                                     | `false`     | 是否使用圆角标签。               |
| `showValue` | `boolean`                                                     | `true`      | 未匹配时是否回退显示原值。       |

组件没有 Emits、Slots 和公开方法。空值不渲染内容；多值会去重，已匹配项按后端字典排序展示，未匹配项在尾部显示。

## 使用示例

```vue
<script setup lang="ts">
import { useDict } from '@/hooks'

const { sys_user_sex } = useDict('sys_user_sex')
</script>

<template>
  <DictTag :options="sys_user_sex" value="0" type="info" />
</template>
```

`useDict` 会在组件挂载后加载数据。缓存命中（包括已缓存的空数组）时不会重复请求；需要主动刷新时使用注入到 Vue 的 `$dict.refresh('sys_user_sex')`，退出登录和字典管理写操作会清理相关缓存。
