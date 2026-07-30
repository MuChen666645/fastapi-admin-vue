import type { Component } from 'vue'
import * as Ionicons5 from '@vicons/ionicons5'

const iconComponents = Ionicons5 as unknown as Record<string, Component>

export const resolveIconComponent = (iconName: string | null): Component | null => {
  if (!iconName) {
    return null
  }

  return iconComponents[iconName] ?? null
}
