import { describe, expect, it } from 'vitest'

import { mount } from '@vue/test-utils'
import { NMessageProvider } from 'naive-ui'
import { defineComponent } from 'vue'

import SystemConfigView from '../views/system/config/index.vue'

const TestHost = defineComponent({
  components: {
    NMessageProvider,
    SystemConfigView,
  },
  template: '<NMessageProvider><SystemConfigView /></NMessageProvider>',
})

describe('SystemConfigView', () => {
  it('renders full-content preferences and switches between setting groups', async () => {
    const wrapper = mount(TestHost)

    expect(wrapper.find('main.preferences-page').exists()).toBe(true)
    expect(wrapper.findAll('[role="tab"]')).toHaveLength(3)
    const panels = wrapper.findAll('.settings-panel')

    expect(panels[0]?.isVisible()).toBe(true)
    expect(panels[0]?.get('h2').text()).toBe('外观设置')
    expect(wrapper.text()).not.toContain('网站名称')

    await wrapper.findAll('[role="tab"]')[1]?.trigger('click')
    expect(panels[1]?.isVisible()).toBe(true)
    expect(panels[1]?.get('h2').text()).toBe('布局设置')
    expect(wrapper.find('[aria-label="显示标签页"]').exists()).toBe(true)

    await wrapper.findAll('[role="tab"]')[2]?.trigger('click')
    expect(panels[2]?.isVisible()).toBe(true)
    expect(panels[2]?.get('h2').text()).toBe('通用设置')
    expect(wrapper.find('[aria-label="定时检查更新"]').exists()).toBe(true)

    wrapper.unmount()
  })
})
