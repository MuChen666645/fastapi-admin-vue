import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import { permissionDirective } from '@/directives'
import { useAuthStore } from '@/stores'
import OnlineSessionTable from '@/views/monitor/online/components/OnlineSessionTable.vue'

const createSession = (userId: number | string = 7) => ({
  token_id: 'a'.repeat(64),
  user_id: userId,
  username: 'admin',
  ip_address: '127.0.0.1',
  user_agent: 'Mozilla/5.0',
  login_time: '2026-08-12T09:00:00+08:00',
  expire_time: '2026-08-12T10:00:00+08:00',
})

describe('在线会话表格', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAuthStore().permissions = ['monitor:online:forceLogout']
  })

  it('为整数用户会话提供会话级和用户级强退操作', async () => {
    const session = createSession()
    const wrapper = mount(OnlineSessionTable, {
      props: {
        data: [session],
        loading: false,
        forceLogoutAllowed: true,
        revokingAction: null,
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    const sessionButton = wrapper.get('[aria-label="下线当前会话"]')
    const userButton = wrapper.get('[aria-label="下线该用户全部会话"]')
    await sessionButton.trigger('click')
    await userButton.trigger('click')

    expect(wrapper.emitted('force-session')).toEqual([[session]])
    expect(wrapper.emitted('force-user')).toEqual([[session]])
    wrapper.unmount()
  })

  it('非整数历史用户标识只允许会话级强退', async () => {
    const wrapper = mount(OnlineSessionTable, {
      props: {
        data: [createSession('legacy-user')],
        loading: false,
        forceLogoutAllowed: true,
        revokingAction: null,
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="下线当前会话"]').exists()).toBe(true)
    expect(wrapper.find('[aria-label="下线该用户全部会话"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('无强退权限时不渲染操作列', async () => {
    useAuthStore().permissions = ['monitor:online:list']
    const wrapper = mount(OnlineSessionTable, {
      props: {
        data: [createSession()],
        loading: false,
        forceLogoutAllowed: false,
        revokingAction: null,
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.find('[aria-label="下线当前会话"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('操作')
    wrapper.unmount()
  })
})
