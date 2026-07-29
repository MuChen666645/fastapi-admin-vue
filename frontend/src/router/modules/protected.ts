import type { RouteRecordRaw } from 'vue-router'

import BasicLayout from '@/layouts/BasicLayout/index.vue'
import ChangePasswordView from '@/views/change-password/index.vue'

export const protectedRoutes: RouteRecordRaw[] = [
  {
    path: '/change-password',
    name: 'change-password',
    component: ChangePasswordView,
    meta: {
      title: '淇敼瀵嗙爜',
      menu: false,
      hideBreadcrumb: true,
      requiresAuth: true,
      allowPasswordChange: true,
    },
  },
  {
    path: '/',
    name: 'app',
    component: BasicLayout,
    meta: {
      title: '绠＄悊鍚庡彴',
      menu: false,
      hideBreadcrumb: true,
      requiresAuth: true,
    },
  },
]
