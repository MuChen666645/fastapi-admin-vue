import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import { permissionDirective } from '@/directives'
import { useAuthStore } from '@/stores'
import TenantTable from '@/views/system/tenant/components/TenantTable.vue'

const tenant = {
  id: 7,
  code: 'tenant-a',
  name: 'Tenant A',
  description: null,
  status: '1' as const,
  version: 3,
  deleted_at: null,
  create_time: '2026-08-13T09:00:00',
  update_time: '2026-08-13T10:00:00',
}

const permissions = {
  list: true,
  create: true,
  edit: true,
  remove: true,
  memberList: true,
  memberAdd: true,
  memberEdit: true,
  memberRemove: true,
}

describe('Tenant table', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAuthStore().permissions = [
      'system:tenant:list',
      'system:tenant:edit',
      'system:tenant:remove',
      'system:tenant:member:list',
    ]
  })

  it('emits platform tenant operations for an enabled tenant', async () => {
    const wrapper = mount(TenantTable, {
      props: { data: [tenant], loading: false, permissions },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    await wrapper.get('[aria-label="查看详情"]').trigger('click')
    await wrapper.get('[aria-label="管理成员"]').trigger('click')
    await wrapper.get('[aria-label="编辑租户"]').trigger('click')
    await wrapper.get('[aria-label="删除租户"]').trigger('click')

    expect(wrapper.emitted('detail')).toEqual([[tenant]])
    expect(wrapper.emitted('members')).toEqual([[tenant]])
    expect(wrapper.emitted('edit')).toEqual([[tenant]])
    expect(wrapper.emitted('delete')).toEqual([[tenant]])
    wrapper.unmount()
  })

  it('does not expose member management for a disabled tenant', async () => {
    const wrapper = mount(TenantTable, {
      props: { data: [{ ...tenant, status: '0' as const }], loading: false, permissions },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="管理成员"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('does not expose edit or delete actions for the default tenant', async () => {
    const wrapper = mount(TenantTable, {
      props: { data: [{ ...tenant, id: 1 }], loading: false, permissions },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="编辑租户"]').exists()).toBe(false)
    expect(wrapper.find('[aria-label="删除租户"]').exists()).toBe(false)
    wrapper.unmount()
  })
})
