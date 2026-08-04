# RequestMessageBridge 使用文档

`RequestMessageBridge` 将请求传输层的错误消息接入 Naive UI `NMessageProvider`。它本身不显示可见内容，只负责注册和清理全局 Message 回调。

## 挂载方式

组件必须放在 `NMessageProvider` 内：

```vue
<NMessageProvider>
  <RequestMessageBridge />
  <RouterView />
</NMessageProvider>
```

请求层通过 `requestJson` 在请求失败且 `showMessage` 未关闭时调用 `showRequestMessage`，最终由桥接组件调用 `message.error`。

## 使用边界

- 应用根部只挂载一个实例。
- 页面不需要手动调用组件或创建全局 Message 回调。
- 登录、退出等需要 Notification 的场景继续由页面按业务语义处理。
- 组件卸载时会注销回调，避免向已销毁的 Provider 写入消息。

组件没有 Props、Events 或暴露方法。
