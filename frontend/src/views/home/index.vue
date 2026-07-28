<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NGrid, NGridItem, NList, NListItem, NText } from 'naive-ui'

import type { UserRoute } from '@/types/api'
import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'HomeView' })

const auth = useAuthStore()

const visibleRoutes = computed(() => {
  const flattenRoutes = (routes: UserRoute[]): UserRoute[] =>
    routes.flatMap((route) => [route, ...flattenRoutes(route.children)])

  return flattenRoutes(auth.routes).filter((route) => !route.hidden)
})

const userStatus = computed(() => (String(auth.currentUser?.user.status) === '1' ? '正常' : '受限'))
</script>

<template>
  <section class="home-page grid gap-4">
    <NCard bordered class="welcome-card">
      <div class="welcome-copy">
        <NText class="welcome-kicker">工作台概览</NText>
        <NText tag="h1" class="welcome-title" strong>欢迎回来，{{ auth.displayName }}</NText>
        <NText depth="3" class="welcome-description">
          当前页面与菜单、权限和用户信息均来自 FastAPI 服务端。
        </NText>
      </div>
      <div class="welcome-badge">会话正常</div>
    </NCard>

    <NGrid x-gap="16" y-gap="16" cols="1 640:3" responsive="screen" class="summary-grid">
      <NGridItem>
        <NCard bordered class="summary-card">
          <NText depth="3">可访问菜单</NText>
          <NText class="summary-value" strong>{{ visibleRoutes.length }}</NText>
          <NText depth="3">由后端角色动态下发</NText>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard bordered class="summary-card">
          <NText depth="3">权限编码</NText>
          <NText class="summary-value" strong>{{ auth.permissions.length }}</NText>
          <NText depth="3">完整编码匹配</NText>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard bordered class="summary-card">
          <NText depth="3">账号状态</NText>
          <NText class="summary-value summary-value-status" strong>{{ userStatus }}</NText>
          <NText depth="3">{{ auth.currentUser?.user.username }}</NText>
        </NCard>
      </NGridItem>
    </NGrid>

    <NCard bordered title="当前授权菜单" class="route-card">
      <NList v-if="visibleRoutes.length" hoverable>
        <NListItem v-for="item in visibleRoutes" :key="item.name">
          <div class="route-item">
            <div>
              <NText strong>{{ item.meta.title }}</NText>
              <NText depth="3" class="route-path">{{ item.path }}</NText>
            </div>
            <span class="route-name">{{ item.name }}</span>
          </div>
        </NListItem>
      </NList>
      <NText v-else depth="3">暂无可见菜单</NText>
    </NCard>
  </section>
</template>

<style>
.welcome-card,
.summary-card,
.route-card {
  border-radius: 10px;
}

.welcome-card .n-card__content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 30px;
}

.welcome-copy {
  display: grid;
  gap: 8px;
}

.welcome-kicker {
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.welcome-title {
  margin: 0;
  color: var(--app-color-text);
  font-size: 30px;
}

.welcome-description {
  line-height: 1.7;
}

.welcome-badge {
  flex: 0 0 auto;
  padding: 6px 10px;
  color: var(--app-color-success);
  border-radius: 999px;
  background: rgb(40 120 86 / 9%);
  font-size: 12px;
  font-weight: 700;
}

.summary-card .n-card__content {
  display: grid;
  gap: 8px;
  min-height: 142px;
  padding: 20px;
}

.summary-value {
  color: var(--app-color-text);
  font-size: 32px;
  line-height: 1;
}

.summary-value-status {
  color: var(--app-color-success);
  font-size: 26px;
}

.route-card .n-card-header {
  padding: 20px 22px 16px;
}

.route-card .n-card__content {
  padding: 0 22px 14px;
}

.route-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.route-path {
  display: block;
  margin-top: 5px;
  font-size: 12px;
}

.route-name {
  color: var(--app-color-primary);
  font-size: 12px;
}

@media (width <= 640px) {
  .welcome-card .n-card__content {
    display: grid;
    gap: 18px;
    padding: 22px;
  }

  .welcome-title {
    font-size: 26px;
  }

  .route-item {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }
}
</style>
