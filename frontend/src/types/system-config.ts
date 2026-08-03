export type SettingsTab = 'appearance' | 'layout' | 'general'

export type ThemeMode = 'light' | 'dark' | 'system'

export type ContentWidth = 'full' | 'centered'

export type LayoutScrollMode = 'content' | 'workspace' | 'sticky'

export interface LayoutSettings {
  contentWidth: ContentWidth
  showSidebar: boolean
  showTabs: boolean
  showBreadcrumb: boolean
  showFooter: boolean
  scrollMode: LayoutScrollMode
}
