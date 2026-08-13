import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import { permissionDirective } from '@/directives'
import { useAuthStore } from '@/stores'
import TenantMemberModal from '@/views/system/tenant/components/TenantMemberModal.vue'

const tenant = {
  id: 1,
  code: 'default',
  name: '默认租户',
  description: null,
  status: '1' as const,
  version: 1,
  deleted_at: null,
  create_time: '2026-08-13T09:00:00',
  update_time: '2026-08-13T10:00:00',
}

const protectedAdminMember = {
  user_id: 1,
  tenant_id: 1,
  username: 'admin',
  nickname: 'fastapi-admin',
  status: '1' as const,
  is_default: true,
  version: 1,
}

const member = {
  ...protectedAdminMember,
  user_id: 2,
  username: 'test',
  nickname: 'fastapi-user',
  is_default: false,
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

const userOptions = [
  { id: 1, username: 'admin', nickname: 'fastapi-admin' },
  { id: 2, username: 'test', nickname: 'fastapi-user' },
]

const mountModal = (members = [protectedAdminMember]) => {
  const pinia = createPinia()
  useAuthStore(pinia).permissions = [
    'system:tenant:member:add',
    'system:tenant:member:edit',
    'system:tenant:member:remove',
  ]

  return mount(TenantMemberModal, {
    props: {
      show: true,
      tenant,
      members,
      userOptions,
      userOptionsLoading: false,
      canSelectUsers: true,
      loading: false,
      addModel: { user_id: null, is_default: false },
      permissions,
    },
    global: {
      plugins: [pinia],
      directives: { permission: permissionDirective },
    },
  })
}

describe('Tenant member modal', () => {
  it('uses an aligned medium-height switch in the member add area', async () => {
    const wrapper = mountModal()
    await nextTick()

    const memberSwitch = document.body.querySelector('.tenant-member-default-switch')
    expect(memberSwitch?.getAttribute('style')).toContain('--n-rail-height: 34px')
    expect(document.body.querySelector('.tenant-member-add-button')).not.toBeNull()
    expect(document.body.querySelector('.tenant-member-user-select')).not.toBeNull()
    wrapper.unmount()
  })

  it('does not expose mutations for the protected admin member', async () => {
    const wrapper = mountModal()
    await nextTick()

    expect(document.body.querySelector('[aria-label="停用"]')).toBeNull()
    expect(document.body.querySelector('[aria-label="设为默认租户"]')).toBeNull()
    expect(document.body.querySelector('[aria-label="移除成员"]')).toBeNull()
    wrapper.unmount()
  })

  it('keeps mutations available for ordinary members', async () => {
    const wrapper = mountModal([member])
    await nextTick()

    expect(document.body.querySelector('[aria-label="停用"]')).not.toBeNull()
    expect(document.body.querySelector('[aria-label="设为默认租户"]')).not.toBeNull()
    expect(document.body.querySelector('[aria-label="移除成员"]')).not.toBeNull()
    wrapper.unmount()
  })

  it('disables users who are already tenant members', async () => {
    const wrapper = mountModal([member])
    await nextTick()

    const select = wrapper.findComponent({ name: 'Select' })
    expect(select.props('options')).toEqual([
      { label: 'admin（fastapi-admin）', value: 1, disabled: false },
      { label: 'test（fastapi-user）', value: 2, disabled: true },
    ])
    wrapper.unmount()
  })

  it('writes the selected user ID to the member add model', async () => {
    const wrapper = mountModal()
    await nextTick()

    const select = wrapper.findComponent({ name: 'Select' })
    select.vm.$emit('update:value', 2)
    await nextTick()

    expect(wrapper.emitted('update:add-model')).toEqual([[{ user_id: 2, is_default: false }]])
    wrapper.unmount()
  })
})
