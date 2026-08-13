import type {
  SystemConfigCreatePayload,
  SystemConfigFormModel,
  SystemConfigUpdatePayload,
} from '@/types'

const normalizeOptionalText = (value: string): string | null => value.trim() || null

export const createSystemConfigPayload = (
  model: SystemConfigFormModel,
): SystemConfigCreatePayload => ({
  config_name: model.config_name.trim(),
  config_key: model.config_key.trim(),
  config_value: model.config_value || null,
  config_type: model.config_type.trim(),
  is_builtin: model.is_builtin,
  remark: normalizeOptionalText(model.remark),
})

export const createSystemConfigUpdatePayload = (
  model: SystemConfigFormModel,
): SystemConfigUpdatePayload => ({
  config_name: model.config_name.trim(),
  config_value: model.config_value || null,
  config_type: model.config_type.trim(),
  remark: normalizeOptionalText(model.remark),
})
