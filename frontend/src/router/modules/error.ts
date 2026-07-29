import type { RouteRecordRaw } from 'vue-router'

import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'

export const errorRoutes: RouteRecordRaw[] = [
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenView,
    meta: {
      title: '鏃犳潈闄愯闂?',
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
      title: '椤甸潰涓嶅瓨鍦?',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
]
