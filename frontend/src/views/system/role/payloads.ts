import type { RoleCreatePayload, RoleFormModel, RoleUpdatePayload } from '@/types'

const toNullableText = (value: string): string | null => value.trim() || null

const normalizeDepartmentIds = (model: RoleFormModel): number[] =>
  model.data_scope === '2' ? [...model.dept_ids] : []

export const createRolePayload = (model: RoleFormModel): RoleCreatePayload => ({
  name: model.name.trim(),
  code: model.code.trim(),
  description: toNullableText(model.description),
  data_scope: model.data_scope,
  menu_ids: [...model.menu_ids],
  dept_ids: normalizeDepartmentIds(model),
  field_permission_codes: [...model.field_permission_codes],
})

export const createRoleUpdatePayload = (model: RoleFormModel): RoleUpdatePayload => ({
  name: model.name.trim(),
  description: toNullableText(model.description),
  data_scope: model.data_scope,
  status: model.status,
  version: model.version ?? undefined,
  menu_ids: [...model.menu_ids],
  dept_ids: normalizeDepartmentIds(model),
  field_permission_codes: [...model.field_permission_codes],
})
