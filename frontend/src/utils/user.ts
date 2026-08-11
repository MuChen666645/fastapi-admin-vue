import type { DictDataListItem, UserSex, UserSexSelectOption } from '@/types'

const PROTECTED_ADMIN_USERNAME = 'admin'

const isUserSex = (value: string): value is UserSex => value === '0' || value === '1'

export const isProtectedAdminUser = (username: string): boolean =>
  username.trim().toLowerCase() === PROTECTED_ADMIN_USERNAME

export const toUserSexSelectOptions = (
  dictionary: ReadonlyArray<DictDataListItem>,
): UserSexSelectOption[] =>
  dictionary.flatMap((item) =>
    isUserSex(item.dict_value) ? [{ label: item.dict_label, value: item.dict_value }] : [],
  )
