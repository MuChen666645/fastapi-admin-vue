import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import { permissionDirective } from '@/directives'
import { useAuthStore } from '@/stores'
import JobTable from '@/views/monitor/job/components/JobTable.vue'

const createJob = (status: '0' | '1' = '1') => ({
  id: 7,
  job_name: 'Daily report',
  job_key: 'report.daily',
  task_name: 'report.generate',
  cron_expression: '0 2 * * *',
  args_json: '{}',
  timeout_seconds: 300,
  max_retries: 0,
  status,
  last_run_time: null,
  next_run_time: '2026-08-13T02:00:00+08:00',
  last_status: null,
  last_message: null,
  create_by: 1,
  create_time: '2026-08-12T09:00:00+08:00',
  update_time: '2026-08-12T09:00:00+08:00',
})

const permissions = {
  list: true,
  query: true,
  create: true,
  edit: true,
  remove: true,
  run: true,
}

describe('定时任务表格', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAuthStore().permissions = [
      'monitor:job:query',
      'monitor:job:edit',
      'monitor:job:remove',
      'monitor:job:run',
    ]
  })

  it('提供详情、日志、编辑、执行和删除操作', async () => {
    const job = createJob()
    const wrapper = mount(JobTable, {
      props: { data: [job], loading: false, permissions, processingAction: null },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    for (const label of ['查看详情', '执行日志', '编辑任务', '立即执行', '删除任务']) {
      expect(wrapper.find(`[aria-label="${label}"]`).exists()).toBe(true)
    }

    await wrapper.get('[aria-label="立即执行"]').trigger('click')
    expect(wrapper.emitted('run')).toEqual([[job]])
    wrapper.unmount()
  })

  it('停用任务保留执行入口但禁用操作', async () => {
    const wrapper = mount(JobTable, {
      props: {
        data: [createJob('0')],
        loading: false,
        permissions,
        processingAction: null,
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.get('[aria-label="立即执行"]').attributes('disabled')).toBeDefined()
    wrapper.unmount()
  })

  it('无操作权限时不渲染操作列', async () => {
    useAuthStore().permissions = ['monitor:job:list']
    const wrapper = mount(JobTable, {
      props: {
        data: [createJob()],
        loading: false,
        permissions: {
          list: true,
          query: false,
          create: false,
          edit: false,
          remove: false,
          run: false,
        },
        processingAction: null,
      },
      global: { directives: { permission: permissionDirective } },
    })
    await nextTick()

    expect(wrapper.text()).not.toContain('操作')
    wrapper.unmount()
  })
})
