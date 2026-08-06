# MessageCenter

`MessageCenter` 是消息中心的无状态展示组件，负责消息分类、列表、空状态、加载状态和错误重试交互。

## Props

- `items`：已经由 API parser 校验过的 `MessageItem[]`。
- `activeTab`：当前消息类型，取值为 `system`、`approval` 或 `alarm`。
- `tabUnreadCounts`：各消息类型的未读数量。
- `loading`、`error`：请求状态。
- `compact`：是否使用顶栏弹层的紧凑列表样式。
- `showFooter`：是否显示“查看全部消息”和刷新操作。

## Emits

- `update:activeTab`：切换消息类型。
- `select`：点击一条消息。
- `refresh`：请求刷新。
- `viewAll`：进入完整消息中心。

组件不直接访问 API、不保存业务状态；请求、已读状态和路由跳转由 `src/hooks/` 与 Pinia Store 编排。
