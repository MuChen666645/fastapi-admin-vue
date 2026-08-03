import { RouterView } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import BasicLayout from '@/layouts/BasicLayout/index.vue'
import ChangePasswordView from '@/views/change-password/index.vue'
import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'
import OfflineView from '@/views/error/offline.vue'
import ServerErrorView from '@/views/error/500.vue'
import SystemConfigView from '@/views/system/config/index.vue'

export const protectedRoutes: RouteRecordRaw[] = [
  {
    path: '/change-password',
    name: 'change-password',
    component: ChangePasswordView,
    meta: {
      title: '修改密码',
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
      title: '管理后台',
      menu: false,
      hideBreadcrumb: true,
      requiresAuth: true,
    },
    children: [
      {
        path: 'system/settings',
        name: 'system-settings',
        component: SystemConfigView,
        meta: {
          title: '系统设置',
          menu: false,
          hideBreadcrumb: false,
          requiresAuth: true,
          noCache: false,
          icon: 'SettingsOutline',
          menuType: 'C',
          link: null,
        },
      },
      {
        path: 'demo',
        name: 'demo',
        component: RouterView,
        redirect: { name: 'default-pages' },
        meta: {
          title: '演示',
          menu: true,
          hideBreadcrumb: false,
          requiresAuth: true,
          noCache: false,
          icon: 'GridOutline',
          menuType: 'C',
          link: null,
        },
        children: [
          {
            path: 'default-pages',
            name: 'default-pages',
            component: RouterView,
            redirect: { name: 'default-page-forbidden' },
            meta: {
              title: '缺省页',
              menu: true,
              hideBreadcrumb: false,
              requiresAuth: true,
              noCache: false,
              icon: 'AlertCircleOutline',
              menuType: 'C',
              link: null,
            },
            children: [
              {
                path: '403',
                name: 'default-page-forbidden',
                component: ForbiddenView,
                meta: {
                  title: '403 无权限',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'ShieldCheckmarkOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: '404',
                name: 'default-page-not-found',
                component: NotFoundView,
                meta: {
                  title: '404 页面不存在',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'DocumentTextOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: '500',
                name: 'default-page-server-error',
                component: ServerErrorView,
                meta: {
                  title: '500 服务异常',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'ServerOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: 'offline',
                name: 'default-page-offline',
                component: OfflineView,
                meta: {
                  title: '网络离线',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'CloudOfflineOutline',
                  menuType: 'C',
                  link: null,
                },
              },
            ],
          },
        ],
      },
    ],
  },
]
