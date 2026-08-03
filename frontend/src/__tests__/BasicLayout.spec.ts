import { beforeEach, describe, expect, it } from 'vitest'

import { mount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { defineComponent, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { NMenu, NMessageProvider, NNotificationProvider } from 'naive-ui'

import BasicLayout from '../layouts/BasicLayout/index.vue'
import { useLayoutSettingsStore, usePreferencesStore } from '../stores'

const LayoutPage = defineComponent({
  template: '<div data-testid="layout-page">Layout page content</div>',
})

const LayoutTestHost = defineComponent({
  components: { BasicLayout, NMessageProvider, NNotificationProvider },
  template:
    '<NMessageProvider><NNotificationProvider><BasicLayout /></NNotificationProvider></NMessageProvider>',
})

const createLayoutRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        name: 'app',
        component: BasicLayout,
        redirect: { name: 'layout-home' },
        meta: {
          title: '管理后台',
          menu: false,
          hideBreadcrumb: true,
        },
        children: [
          {
            path: 'home',
            name: 'layout-home',
            component: LayoutPage,
            meta: {
              title: '首页',
            },
          },
          {
            path: 'demo',
            name: 'demo',
            component: LayoutPage,
            meta: {
              title: '演示',
              menu: true,
              requiresAuth: true,
              icon: 'GridOutline',
            },
            children: [
              {
                path: 'default-pages',
                name: 'default-pages',
                component: LayoutPage,
                meta: {
                  title: '缺省页',
                  menu: true,
                  requiresAuth: true,
                  icon: 'AlertCircleOutline',
                },
                children: [
                  {
                    path: '403',
                    name: 'default-page-forbidden',
                    component: LayoutPage,
                    meta: { title: '403 无权限', menu: true, requiresAuth: true },
                  },
                  {
                    path: '404',
                    name: 'default-page-not-found',
                    component: LayoutPage,
                    meta: { title: '404 页面不存在', menu: true, requiresAuth: true },
                  },
                  {
                    path: '500',
                    name: 'default-page-server-error',
                    component: LayoutPage,
                    meta: { title: '500 服务异常', menu: true, requiresAuth: true },
                  },
                  {
                    path: 'offline',
                    name: 'default-page-offline',
                    component: LayoutPage,
                    meta: { title: '网络离线', menu: true, requiresAuth: true },
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  })

describe('BasicLayout', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders the route page and its breadcrumb', async () => {
    const router = createLayoutRouter()
    const pinia = createPinia()

    await router.push('/home')
    await router.isReady()

    const wrapper = mount(LayoutTestHost, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()

    expect(wrapper.find('.basic-layout').exists()).toBe(true)
    expect(wrapper.find('.app-sidebar').exists()).toBe(true)
    expect(wrapper.find('.sidebar-toggle').exists()).toBe(true)
    expect(wrapper.get('.language-toggle').attributes('title')).toBe('切换到 English')
    expect(wrapper.find('.app-sidebar').text()).toContain('演示')
    expect(wrapper.findComponent(NMenu).props('options')).toEqual([
      expect.objectContaining({
        key: 'demo',
        label: '演示',
        children: [
          expect.objectContaining({
            key: 'default-pages',
            label: '缺省页',
            children: [
              expect.objectContaining({ key: 'default-page-forbidden', label: '403 无权限' }),
              expect.objectContaining({ key: 'default-page-not-found', label: '404 页面不存在' }),
              expect.objectContaining({ key: 'default-page-server-error', label: '500 服务异常' }),
              expect.objectContaining({ key: 'default-page-offline', label: '网络离线' }),
            ],
          }),
        ],
      }),
    ])
    expect(wrapper.find('.app-breadcrumb').text()).toContain('首页')
    expect(wrapper.find('[data-testid="layout-page"]').exists()).toBe(true)

    await wrapper.get('.language-toggle').trigger('click')
    expect(usePreferencesStore(pinia).language).toBe('en-US')

    await wrapper.get('.sidebar-toggle').trigger('click')
    expect(wrapper.find('.app-sidebar').classes()).toContain('n-layout-sider--collapsed')

    wrapper.unmount()
  })

  it('applies layout visibility, width and sticky navigation preferences', async () => {
    const router = createLayoutRouter()
    const pinia = createPinia()

    await router.push('/home')
    await router.isReady()

    const wrapper = mount(LayoutTestHost, {
      global: {
        plugins: [router, pinia],
      },
    })
    const layoutSettings = useLayoutSettingsStore(pinia)

    layoutSettings.showSidebar = false
    layoutSettings.showTabs = false
    layoutSettings.showBreadcrumb = false
    layoutSettings.showFooter = false
    layoutSettings.contentWidth = 'centered'
    layoutSettings.scrollMode = 'sticky'
    await nextTick()

    expect(wrapper.find('.basic-layout--sticky-nav').exists()).toBe(true)
    expect(wrapper.find('.app-sidebar').exists()).toBe(false)
    expect(wrapper.find('.app-tabs').exists()).toBe(false)
    expect(wrapper.find('.header-breadcrumb').exists()).toBe(false)
    expect(wrapper.find('.app-footer').exists()).toBe(false)
    expect(wrapper.find('.content-container--centered').exists()).toBe(true)

    wrapper.unmount()
  })
})
