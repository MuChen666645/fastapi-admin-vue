import type { Component } from 'vue'
import * as Ionicons5 from '@vicons/ionicons5'

const iconComponents = Ionicons5 as unknown as Record<string, Component>

/**
 * 按后端菜单返回的静态图标名称解析 Ionicons5 组件。
 *
 * 未知名称返回 null，避免根据不可信输入执行动态导入。
 */
export const resolveIconComponent = (iconName: string | null): Component | null => {
  if (!iconName) {
    return null
  }

  return iconComponents[iconName] ?? null
}
