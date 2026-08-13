import type {
  TenantCreatePayload,
  TenantFormModel,
  TenantMemberAddFormModel,
  TenantMemberAddPayload,
  TenantUpdatePayload,
} from '@/types'

export const createTenantPayload = (model: TenantFormModel): TenantCreatePayload => ({
  code: model.code.trim(),
  name: model.name.trim(),
  description: model.description.trim() || null,
})

export const createTenantUpdatePayload = (
  model: TenantFormModel,
  version: number,
): TenantUpdatePayload => ({
  name: model.name.trim(),
  description: model.description.trim() || null,
  status: model.status,
  version,
})

export const createTenantMemberAddPayload = (
  model: TenantMemberAddFormModel,
): TenantMemberAddPayload | null => {
  if (model.user_id === null || !Number.isInteger(model.user_id) || model.user_id < 1) {
    return null
  }

  return { user_id: model.user_id, is_default: model.is_default }
}
