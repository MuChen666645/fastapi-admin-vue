import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import { permissionDirective } from '@/directives'
import { useAuthStore } from '@/stores'
import SystemConfigTable from '@/views/system/config/components/SystemConfigTable.vue'

const createConfig = (isBuiltin = false) => ({
  id: 7,
  config_name: '分页大小',
  config_key: 'system.page_size',
  config_value: '20',
  config_type: 'number',
  is_builtin: isBuiltin,
  remark: '列表默认分页大小',
  create_time: '2026-08-13T09:00:00+08:00',
  update_time: '2026-08-13T09:00:00+08:00',
})

const permissions = {
  list: true,
  query: true,
  create: true,
  edit: true,
  remove: true,
  removeBuiltin: false,
}

describe('系统参数表格', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAuthStore().permissions = [
      'system:config:query',
      'system:config:edit',
      'system:config:remove',
    ]
  })

  it('为普通参数提供删除操作并触发删除事件', async () => {
    const config = createConfig()
    const wrapper = mount(SystemConfigTable, {
      props: { data: [config], loading: false, permissions },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="查看详情"]').exists()).toBe(true)
    expect(wrapper.find('[aria-label="编辑参数"]').exists()).toBe(true)
    expect(wrapper.find('[aria-label="删除参数"]').exists()).toBe(true)

    await wrapper.get('[aria-label="查看详情"]').trigger('click')
    await wrapper.get('[aria-label="删除参数"]').trigger('click')
    expect(wrapper.emitted('detail')).toEqual([[config]])
    expect(wrapper.emitted('delete')).toEqual([[config]])
    wrapper.unmount()
  })

  it('普通删除权限不允许删除内置参数', async () => {
    const wrapper = mount(SystemConfigTable, {
      props: { data: [createConfig(true)], loading: false, permissions },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="删除参数"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('超级管理员可以删除内置参数', async () => {
    const config = createConfig(true)
    useAuthStore().permissions = ['*:*:*']
    const wrapper = mount(SystemConfigTable, {
      props: {
        data: [config],
        loading: false,
        permissions: { ...permissions, removeBuiltin: true },
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    await wrapper.get('[aria-label="删除参数"]').trigger('click')
    expect(wrapper.emitted('delete')).toEqual([[config]])
    wrapper.unmount()
  })
})
