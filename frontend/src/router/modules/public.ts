import type { RouteRecordRaw } from 'vue-router'

import LoginView from '@/views/login/index.vue'

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: '登录',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
]
