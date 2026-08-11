import { describe, expect, it } from 'vitest'

import type { PostFormModel } from '@/types'
import { createPostPayload, createPostUpdatePayload } from '@/views/system/post/payloads'

const model: PostFormModel = {
  post_code: ' product_manager ',
  post_name: ' 产品经理 ',
  post_sort: 3,
  remark: ' ',
  status: '1',
}

describe('岗位载荷', () => {
  it('清理岗位文本并将空备注转换为 null', () => {
    expect(createPostPayload(model)).toEqual({
      post_code: 'product_manager',
      post_name: '产品经理',
      post_sort: 3,
      remark: null,
      status: '1',
    })
    expect(createPostUpdatePayload(model)).toEqual(createPostPayload(model))
  })

  it('保留有效备注', () => {
    expect(createPostPayload({ ...model, remark: ' 负责产品规划 ' }).remark).toBe('负责产品规划')
  })
})
