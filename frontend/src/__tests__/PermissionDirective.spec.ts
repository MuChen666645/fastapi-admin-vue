import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h, nextTick, ref, withDirectives } from 'vue'
import type { Ref } from 'vue'

import { permissionDirective } from '@/directives'
import type { PermissionDirectiveValue } from '@/directives'
import { useAuthStore } from '@/stores'

const createPermissionHost = (requirement: Ref<PermissionDirectiveValue>) =>
  defineComponent({
    setup: () => () =>
      withDirectives(h('button', { id: 'permission-action' }, 'Action'), [
        [permissionDirective, requirement.value],
      ]),
  })

describe('permissionDirective', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('hides unauthorized elements and restores them after permissions change', async () => {
    const auth = useAuthStore()
    auth.permissions = ['system:message:list']
    const requirement = ref<PermissionDirectiveValue>('system:message:add')
    const wrapper = mount(createPermissionHost(requirement))
    const button = wrapper.get('#permission-action').element as HTMLButtonElement

    expect(button.hidden).toBe(true)
    expect(button.getAttribute('aria-hidden')).toBe('true')

    auth.permissions = ['system:message:add']
    await nextTick()

    expect(button.hidden).toBe(false)
    expect(button.hasAttribute('aria-hidden')).toBe(false)
    wrapper.unmount()
  })

  it('supports all and any permission matching, including the super permission', async () => {
    const auth = useAuthStore()
    auth.permissions = ['system:role:list']
    const requirement = ref<PermissionDirectiveValue>({
      permissions: ['system:role:list', 'system:role:edit'],
      mode: 'all',
    })
    const wrapper = mount(createPermissionHost(requirement))
    const button = wrapper.get('#permission-action').element as HTMLButtonElement

    expect(button.hidden).toBe(true)

    requirement.value = {
      permissions: ['system:role:list', 'system:role:edit'],
      mode: 'any',
    }
    await nextTick()
    expect(button.hidden).toBe(false)

    auth.permissions = ['*:*:*']
    requirement.value = {
      permissions: ['system:message:remove'],
      mode: 'all',
    }
    await nextTick()
    expect(button.hidden).toBe(false)
    wrapper.unmount()
  })
})
