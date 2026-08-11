import type { DepartmentCreatePayload, DepartmentFormModel, DepartmentUpdatePayload } from '@/types'

const toNullableText = (value: string): string | null => {
  const trimmed = value.trim()
  return trimmed || null
}

export const createDepartmentPayload = (model: DepartmentFormModel): DepartmentCreatePayload => ({
  parent_id: model.parent_id > 0 ? model.parent_id : null,
  dept_name: model.dept_name.trim(),
  order_num: model.order_num,
  leader: toNullableText(model.leader),
  phone: toNullableText(model.phone),
  email: toNullableText(model.email),
  status: model.status,
})

export const createDepartmentUpdatePayload = (
  model: DepartmentFormModel,
): DepartmentUpdatePayload => createDepartmentPayload(model)
