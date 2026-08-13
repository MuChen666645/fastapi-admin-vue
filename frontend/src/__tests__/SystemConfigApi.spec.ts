import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  createSystemConfig,
  deleteSystemConfig,
  fetchSystemConfigDetail,
  fetchSystemConfigs,
  updateSystemConfig,
} from '@/api/system-config'
import { parseSystemConfigPage } from '@/api/system-config/parsers'

const systemConfig = {
  id: 7,
  config_name: 'Feature switch',
  config_key: 'app.feature.enabled',
  config_value: 'true',
  config_type: 'text',
  is_builtin: false,
  remark: null,
  create_time: '2026-08-13T09:00:00',
  update_time: '2026-08-13T10:00:00',
}

describe('System config API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('sends only normalized list filters supported by the backend', async () => {
    await fetchSystemConfigs({ page: 2, size: 50 }, { name: ' Feature ', key: ' app.feature ' })
    await fetchSystemConfigs({ page: 1, size: 20 }, { name: ' ', key: '' })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/config/list',
      { params: { page: 2, size: 50, name: 'Feature', key: 'app.feature' } },
      parseSystemConfigPage,
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/config/list',
      { params: { page: 1, size: 20 } },
      parseSystemConfigPage,
    )
  })

  it('uses the backend detail, create, update, and delete contracts', async () => {
    const createPayload = {
      config_name: 'Feature switch',
      config_key: 'app.feature.enabled',
      config_value: 'true',
      config_type: 'text',
      is_builtin: false,
      remark: null,
    }
    const updatePayload = {
      config_name: 'Feature switch',
      config_value: 'false',
      config_type: 'text',
      remark: 'Updated',
    }

    await fetchSystemConfigDetail(7)
    await createSystemConfig(createPayload)
    await updateSystemConfig(7, updatePayload)
    await deleteSystemConfig(7)

    expect(requestJson).toHaveBeenNthCalledWith(1, '/config/7', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/config/add',
      { method: 'POST', data: createPayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/config/7',
      { method: 'PUT', data: updatePayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/config/7',
      { method: 'DELETE' },
      expect.any(Function),
    )
  })

  it('parses complete system config pages and rejects invalid protected fields', () => {
    expect(
      parseSystemConfigPage({ items: [systemConfig], total: 1, page: 1, size: 20, pages: 1 }),
    ).toEqual({ items: [systemConfig], total: 1, page: 1, size: 20, pages: 1 })

    expect(() =>
      parseSystemConfigPage({
        items: [{ ...systemConfig, is_builtin: 'false' }],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toThrow('接口字段 is_builtin 无效')
  })
})
