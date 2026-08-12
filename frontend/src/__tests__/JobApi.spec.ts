import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  createScheduledJob,
  deleteScheduledJob,
  fetchScheduledJobDetail,
  fetchScheduledJobLogs,
  fetchScheduledJobs,
  runScheduledJob,
  updateScheduledJob,
} from '@/api/job'
import {
  parseScheduledJobDetail,
  parseScheduledJobLogPage,
  parseScheduledJobPage,
  parseScheduledJobRunResult,
} from '@/api/job/parsers'

const job = {
  id: 7,
  job_name: 'Daily report',
  job_key: 'report.daily',
  task_name: 'report.generate',
  cron_expression: '0 2 * * *',
  args_json: '{"tenant_id":1}',
  timeout_seconds: 300,
  max_retries: 2,
  status: '1',
  last_run_time: null,
  next_run_time: '2026-08-13T02:00:00+08:00',
  last_status: null,
  last_message: null,
  create_by: 1,
  create_time: '2026-08-12T09:00:00+08:00',
  update_time: '2026-08-12T09:00:00+08:00',
}

const payload = {
  job_name: 'Daily report',
  job_key: 'report.daily',
  task_name: 'report.generate',
  cron_expression: '0 2 * * *',
  args_json: '{"tenant_id":1}',
  timeout_seconds: 300,
  max_retries: 2,
  status: '1' as const,
}

describe('定时任务 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按后端契约传递分页、名称和状态筛选', async () => {
    await fetchScheduledJobs({ page: 2, size: 50 }, { name: ' report ', status: '1' })
    await fetchScheduledJobs({ page: 1, size: 20 }, { name: ' ', status: null })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/job/list',
      { params: { page: 2, size: 50, name: 'report', status: '1' } },
      parseScheduledJobPage,
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/job/list',
      { params: { page: 1, size: 20 } },
      parseScheduledJobPage,
    )
  })

  it('使用真实 CRUD、立即执行和日志路径', async () => {
    const updatePayload = { ...payload }
    Reflect.deleteProperty(updatePayload, 'job_key')

    await createScheduledJob(payload)
    await fetchScheduledJobDetail(7)
    await updateScheduledJob(7, updatePayload)
    await deleteScheduledJob(7)
    await runScheduledJob(7, 930_000)
    await fetchScheduledJobLogs(7, { page: 3, size: 20 })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/job/add',
      { method: 'POST', data: payload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(2, '/job/7', {}, parseScheduledJobDetail)
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/job/7',
      { method: 'PUT', data: updatePayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/job/7',
      { method: 'DELETE' },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      5,
      '/job/7/run',
      { method: 'POST', timeout: 930_000 },
      parseScheduledJobRunResult,
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      6,
      '/job/7/log/list',
      { params: { page: 3, size: 20 } },
      parseScheduledJobLogPage,
    )
  })

  it('严格解析任务详情、分页、执行结果和执行日志', () => {
    expect(parseScheduledJobDetail(job)).toEqual(job)
    expect(parseScheduledJobPage({ items: [job], total: 1, page: 1, size: 20, pages: 1 })).toEqual({
      items: [job],
      total: 1,
      page: 1,
      size: 20,
      pages: 1,
    })
    expect(parseScheduledJobRunResult({ job_id: 7, status: 'queued', message: null })).toEqual({
      job_id: 7,
      status: 'queued',
      message: null,
    })
    expect(
      parseScheduledJobLogPage({
        items: [
          {
            id: 9,
            job_id: 7,
            task_name: 'report.generate',
            status: 'success',
            message: 'done',
            start_time: '2026-08-12T09:00:00+08:00',
            end_time: '2026-08-12T09:00:01+08:00',
            duration_ms: 1000,
          },
        ],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toMatchObject({ total: 1, items: [{ job_id: 7, duration_ms: 1000 }] })
  })

  it('拒绝非法任务状态、范围和日志数据', () => {
    expect(() => parseScheduledJobDetail({ ...job, status: 'enabled' })).toThrow(
      '接口字段 status 无效',
    )
    expect(() => parseScheduledJobDetail({ ...job, max_retries: 11 })).toThrow(
      '接口字段 max_retries 无效',
    )
    expect(() =>
      parseScheduledJobLogPage({
        items: [
          {
            id: 1,
            job_id: 7,
            task_name: 'report.generate',
            status: 'success',
            message: null,
            start_time: '2026-08-12T09:00:00+08:00',
            end_time: null,
            duration_ms: -1,
          },
        ],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toThrow('接口字段 duration_ms 无效')
  })
})
