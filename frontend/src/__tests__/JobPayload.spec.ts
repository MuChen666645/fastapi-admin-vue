import { describe, expect, it } from 'vitest'

import {
  calculateScheduledJobRunTimeout,
  createScheduledJobPayload,
  createScheduledJobUpdatePayload,
} from '@/views/monitor/job/payloads'

const model = {
  job_name: ' Daily report ',
  job_key: ' report.daily ',
  task_name: ' report.generate ',
  cron_expression: '0   2  * * *',
  args_json: ' { "tenant_id": 1 } ',
  timeout_seconds: 300,
  max_retries: 2,
  status: '1' as const,
}

describe('定时任务负载', () => {
  it('清理文本、规范 Cron 与 JSON 对象并保留后端字段', () => {
    expect(createScheduledJobPayload(model)).toEqual({
      job_name: 'Daily report',
      job_key: 'report.daily',
      task_name: 'report.generate',
      cron_expression: '0 2 * * *',
      args_json: '{"tenant_id":1}',
      timeout_seconds: 300,
      max_retries: 2,
      status: '1',
    })
  })

  it('更新负载不提交后端不可修改的任务标识', () => {
    expect(createScheduledJobUpdatePayload(model)).not.toHaveProperty('job_key')
  })

  it('拒绝非对象任务参数', () => {
    expect(() => createScheduledJobPayload({ ...model, args_json: '[]' })).toThrow(
      '任务参数必须是 JSON 对象',
    )
    expect(() => createScheduledJobPayload({ ...model, args_json: 'invalid' })).toThrow()
  })

  it('按后端允许的全局最大重试次数计算同步执行请求时限', () => {
    expect(calculateScheduledJobRunTimeout(300, 2)).toBe(3_330_000)
  })
})
