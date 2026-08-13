import { describe, expect, it } from 'vitest'

import { mount } from '@vue/test-utils'
import { NDrawer, NMessageProvider } from 'naive-ui'
import { createPinia } from 'pinia'
import { defineComponent, nextTick, ref } from 'vue'

import SystemSettingsDrawer from '../layouts/BasicLayout/components/SystemSettingsDrawer/index.vue'

const TestHost = defineComponent({
  components: {
    NMessageProvider,
    SystemSettingsDrawer,
  },
  setup() {
    const visible = ref(true)

    return {
      visible,
    }
  },
  template: '<NMessageProvider><SystemSettingsDrawer v-model:show="visible" /></NMessageProvider>',
})

describe('SystemSettingsDrawer', () => {
  it('renders preferences in a right-side drawer and forwards close events', async () => {
    const wrapper = mount(TestHost, {
      attachTo: document.body,
      global: {
        plugins: [createPinia()],
      },
    })

    await nextTick()

    const drawer = wrapper.findComponent(SystemSettingsDrawer)
    const naiveDrawer = drawer.findComponent(NDrawer)

    expect(naiveDrawer.props('placement')).toBe('right')
    expect(naiveDrawer.props('width')).toMatch(/^min\(\d+px, 100vw\)$/)
    expect(document.body.querySelector('.system-settings-drawer')).not.toBeNull()
    expect(document.body.querySelector('.preferences-page')).not.toBeNull()
    expect(document.body.querySelectorAll('[role="tab"]')).toHaveLength(3)

    naiveDrawer.vm.$emit('update:show', false)
    await nextTick()

    expect(drawer.emitted('update:show')).toEqual([[false]])

    wrapper.unmount()
  })
})
