import type { DepartmentListItem, DepartmentParentTreeOption } from '@/types'

const toDepartmentTreeOptions = (
  items: DepartmentListItem[],
  currentId: number | null,
  blockedByAncestor: boolean = false,
): DepartmentParentTreeOption[] =>
  items.map((item) => {
    const isCurrent = item.dept_id === currentId
    const disabled = blockedByAncestor || isCurrent
    const children = toDepartmentTreeOptions(item.children, currentId, disabled)
    return {
      key: item.dept_id,
      label: item.dept_name,
      ...(disabled ? { disabled: true } : {}),
      ...(children.length > 0 ? { children } : {}),
    }
  })

export const createDepartmentParentOptions = (
  departments: DepartmentListItem[],
  currentId: number | null,
  rootLabel: string,
): DepartmentParentTreeOption[] => [
  { key: 0, label: rootLabel },
  ...toDepartmentTreeOptions(departments, currentId),
]
