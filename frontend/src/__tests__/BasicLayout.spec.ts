import { describe, expect, it } from 'vitest'

import { mount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { NMessageProvider } from 'naive-ui'

import BasicLayout from '../layouts/BasicLayout/index.vue'

const LayoutPage = defineComponent({
  template: '<div data-testid="layout-page">Layout page content</div>',
})

const LayoutTestHost = defineComponent({
  components: { BasicLayout, NMessageProvider },
  template: '<NMessageProvider><BasicLayout /></NMessageProvider>',
})

const createLayoutRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
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
        ],
      },
    ],
  })

describe('BasicLayout', () => {
  it('renders the route page and its breadcrumb', async () => {
    const router = createLayoutRouter()

    await router.push('/home')
    await router.isReady()

    const wrapper = mount(LayoutTestHost, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await flushPromises()

    expect(wrapper.find('.basic-layout').exists()).toBe(true)
    expect(wrapper.find('.app-sidebar').exists()).toBe(true)
    expect(wrapper.find('.sidebar-toggle').exists()).toBe(true)
    expect(wrapper.find('.app-breadcrumb').text()).toContain('首页')
    expect(wrapper.find('[data-testid="layout-page"]').exists()).toBe(true)

    await wrapper.get('.sidebar-toggle').trigger('click')
    expect(wrapper.find('.app-sidebar').classes()).toContain('n-layout-sider--collapsed')

    wrapper.unmount()
  })
})
