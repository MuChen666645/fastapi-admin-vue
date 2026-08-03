import type { RouteRecordRaw } from 'vue-router'

import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'
import OfflineView from '@/views/error/offline.vue'
import ServerErrorView from '@/views/error/500.vue'

export const errorRoutes: RouteRecordRaw[] = [
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenView,
    meta: {
      title: '无权限访问',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
  {
    path: '/500',
    name: 'server-error',
    component: ServerErrorView,
    meta: {
      title: '服务异常',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
  {
    path: '/offline',
    name: 'offline',
    component: OfflineView,
    meta: {
      title: '网络离线',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: '页面不存在',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
]
