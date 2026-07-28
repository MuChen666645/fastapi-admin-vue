<script setup lang="ts">
defineOptions({ name: 'ForbiddenView' })
</script>

<template>
  <main class="error-page grid min-h-screen">
    <div class="error-code">403</div>
    <h1>没有访问权限</h1>
    <p>当前账号没有可访问的菜单，请联系管理员配置角色权限。</p>
  </main>
</template>

<style scoped>
.error-page {
  place-content: center;
  padding: 24px;
  text-align: center;
  background: var(--app-color-page);
}

.error-code {
  color: var(--app-color-primary);
  font-size: 72px;
  font-weight: 800;
  line-height: 1;
}

.error-page h1 {
  margin: 20px 0 8px;
  color: var(--app-color-text);
  font-size: 24px;
}

.error-page p {
  margin: 0;
  color: var(--app-color-text-muted);
}
</style>
