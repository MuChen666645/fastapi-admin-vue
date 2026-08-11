import { createApp, defineComponent, h } from 'vue'
import { createPinia } from 'pinia'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const fetchDictDataByType = vi.hoisted(() => vi.fn())

vi.mock('@/api/dictionary', () => ({ fetchDictDataByType }))

import DictTag from '@/components/DictTag/index.vue'
import { useDict } from '@/hooks'
import { createDictionaryPlugin } from '@/plugins'

const dictData = {
  dict_code: 2,
  dict_sort: 1,
  dict_label: '男',
  dict_value: '0',
  dict_type: 'sys_user_sex',
  status: '1' as const,
  remark: null,
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
}

describe('字典 Vue 使用入口', () => {
  beforeEach(() => {
    fetchDictDataByType.mockReset()
    fetchDictDataByType.mockResolvedValue([dictData])
  })

  it('useDict 在挂载后加载并暴露同名字典 Ref', async () => {
    const pinia = createPinia()
    const harness = defineComponent({
      setup: () => {
        const dictionaries = useDict('sys_user_sex')
        return () => h('span', dictionaries.sys_user_sex?.value[0]?.dict_label ?? '')
      },
    })

    const wrapper = mount(harness, { global: { plugins: [pinia] } })
    await flushPromises()

    expect(wrapper.text()).toBe('男')
    expect(fetchDictDataByType).toHaveBeenCalledWith('sys_user_sex')
    wrapper.unmount()
  })

  it('Vue 插件注册 DictTag 并注入缓存服务', async () => {
    const app = createApp({ render: () => null })
    const pinia = createPinia()
    app.use(pinia)
    app.use(createDictionaryPlugin(pinia))

    expect(app.component('DictTag')).toBe(DictTag)
    expect(app.config.globalProperties.useDict).toBe(useDict)
    await expect(app.config.globalProperties.$dict.get('sys_user_sex')).resolves.toEqual([dictData])
    expect(app.config.globalProperties.$dict.peek('sys_user_sex')).toEqual([dictData])
  })
})
