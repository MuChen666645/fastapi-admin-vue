# 权限指令

`v-permission` 用于控制页面按钮和其他操作入口的可见性。指令复用认证 Store 中的权限列表，未授权元素设置为 `hidden`，权限变化后可以恢复，不会直接移除 Vue 管理的节点。

## 使用方式

单个权限码：

```vue
<NButton v-permission="'system:message:add'">发布消息</NButton>
```

多个权限码默认要求全部满足；需要满足任一权限时使用对象配置：

```vue
<NButton
  v-permission="{
    permissions: ['system:role:list', 'system:role:edit'],
    mode: 'all',
  }"
>
  角色配置
</NButton>
```

指令只负责前端入口展示，API handler 和后端接口仍必须执行权限校验。
