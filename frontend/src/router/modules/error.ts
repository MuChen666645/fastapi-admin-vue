import type { RouteRecordRaw } from 'vue-router'

import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'

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
