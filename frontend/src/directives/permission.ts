import { watch } from 'vue'
import type { Directive } from 'vue'

import { useAuthStore } from '@/stores'
import { hasPermission as matchesPermission } from '@/utils/permissions'

export type PermissionMatchMode = 'all' | 'any'

export interface PermissionDirectiveOptions {
  permissions: string | ReadonlyArray<string>
  mode?: PermissionMatchMode
}

export type PermissionDirectiveValue = string | ReadonlyArray<string> | PermissionDirectiveOptions

interface PermissionDirectiveState {
  value: PermissionDirectiveValue
  originalHidden: boolean
  originalAriaHidden: string | null
  originalDisplay: string
  originalDisplayPriority: string
  stopWatching: () => void
}

const states = new WeakMap<HTMLElement, PermissionDirectiveState>()

const normalizePermissions = (value: string | ReadonlyArray<string>): string[] => {
  const permissions = typeof value === 'string' ? [value] : value
  return permissions.map((permission) => permission.trim()).filter(Boolean)
}

const resolveRequirement = (
  value: PermissionDirectiveValue,
): { permissions: string[]; mode: PermissionMatchMode } => {
  if (typeof value === 'string') {
    return { permissions: normalizePermissions(value), mode: 'all' }
  }

  if ('permissions' in value) {
    return {
      permissions: normalizePermissions(value.permissions),
      mode: value.mode ?? 'all',
    }
  }

  return { permissions: normalizePermissions(value), mode: 'all' }
}

const isAllowed = (
  permissions: ReadonlyArray<string>,
  value: PermissionDirectiveValue,
): boolean => {
  const requirement = resolveRequirement(value)
  if (requirement.permissions.length === 0) {
    return false
  }

  if (requirement.mode === 'any') {
    return requirement.permissions.some((permission) => matchesPermission(permissions, permission))
  }

  return requirement.permissions.every((permission) => matchesPermission(permissions, permission))
}

const updateVisibility = (element: HTMLElement, state: PermissionDirectiveState): void => {
  if (isAllowed(useAuthStore().permissions, state.value)) {
    element.hidden = state.originalHidden
    if (state.originalDisplay) {
      element.style.setProperty('display', state.originalDisplay, state.originalDisplayPriority)
    } else {
      element.style.removeProperty('display')
    }
    if (state.originalAriaHidden === null) {
      element.removeAttribute('aria-hidden')
    } else {
      element.setAttribute('aria-hidden', state.originalAriaHidden)
    }
    return
  }

  element.hidden = true
  element.style.setProperty('display', 'none', 'important')
  element.setAttribute('aria-hidden', 'true')
}

export const permissionDirective: Directive<HTMLElement, PermissionDirectiveValue> = {
  mounted: (element, binding) => {
    const state: PermissionDirectiveState = {
      value: binding.value,
      originalHidden: element.hidden === true,
      originalAriaHidden: element.getAttribute('aria-hidden'),
      originalDisplay: element.style.getPropertyValue('display'),
      originalDisplayPriority: element.style.getPropertyPriority('display'),
      stopWatching: () => undefined,
    }

    states.set(element, state)
    state.stopWatching = watch(
      () => useAuthStore().permissions,
      () => updateVisibility(element, state),
      { deep: true },
    )
    updateVisibility(element, state)
  },
  updated: (element, binding) => {
    const state = states.get(element)
    if (!state) {
      return
    }

    state.value = binding.value
    updateVisibility(element, state)
  },
  beforeUnmount: (element) => {
    states.get(element)?.stopWatching()
    states.delete(element)
  },
}
