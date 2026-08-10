import { RouterView } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import BasicLayout from '@/layouts/BasicLayout/index.vue'
import ChangePasswordView from '@/views/change-password/index.vue'
import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'
import OfflineView from '@/views/error/offline.vue'
import ServerErrorView from '@/views/error/500.vue'
import FormDemoView from '@/views/demo/form/index.vue'
import HooksDemoView from '@/views/demo/hooks/index.vue'
import SearchFormDemoView from '@/views/demo/search-form/index.vue'
import SystemConfigView from '@/views/system/config/index.vue'
import DictionaryDataView from '@/views/system/dict/data.vue'
import UtilsDemoView from '@/views/demo/utils/index.vue'

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
        path: 'system/dict/data',
        name: 'system-dict-data',
        component: DictionaryDataView,
        meta: {
          title: '字典数据',
          menu: false,
          hideBreadcrumb: false,
          requiresAuth: true,
          noCache: false,
          icon: 'ListOutline',
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
            path: 'features',
            name: 'demo-features',
            component: RouterView,
            redirect: { name: 'demo-form' },
            meta: {
              title: '功能',
              menu: true,
              hideBreadcrumb: false,
              requiresAuth: true,
              noCache: false,
              icon: 'ConstructOutline',
              menuType: 'C',
              link: null,
            },
            children: [
              {
                path: 'form',
                name: 'demo-form',
                component: FormDemoView,
                meta: {
                  title: '表单',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'CreateOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: 'search-form',
                name: 'demo-search-form',
                component: SearchFormDemoView,
                meta: {
                  title: '搜索表单',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'SearchOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: 'hooks',
                name: 'demo-hooks',
                component: HooksDemoView,
                meta: {
                  title: 'Hooks',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'GitBranchOutline',
                  menuType: 'C',
                  link: null,
                },
              },
              {
                path: 'utils',
                name: 'demo-utils',
                component: UtilsDemoView,
                meta: {
                  title: '工具函数',
                  menu: true,
                  hideBreadcrumb: false,
                  requiresAuth: true,
                  noCache: false,
                  icon: 'CodeSlashOutline',
                  menuType: 'C',
                  link: null,
                },
              },
            ],
          },
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
