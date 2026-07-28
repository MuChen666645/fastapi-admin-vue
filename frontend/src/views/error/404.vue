<script setup lang="ts">
defineOptions({ name: 'NotFoundView' })
</script>

<template>
  <main class="error-page grid min-h-screen">
    <div class="error-code">404</div>
    <h1>页面不存在</h1>
    <p>请从服务端授权的菜单重新进入。</p>
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
