import type { PostCreatePayload, PostFormModel, PostUpdatePayload } from '@/types'

const toNullableText = (value: string): string | null => {
  const trimmed = value.trim()
  return trimmed || null
}

export const createPostPayload = (model: PostFormModel): PostCreatePayload => ({
  post_code: model.post_code.trim(),
  post_name: model.post_name.trim(),
  post_sort: model.post_sort,
  remark: toNullableText(model.remark),
  status: model.status,
})

export const createPostUpdatePayload = (model: PostFormModel): PostUpdatePayload =>
  createPostPayload(model)
