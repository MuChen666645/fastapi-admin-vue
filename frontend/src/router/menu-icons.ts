import type { Component } from 'vue'
import {
  AnalyticsOutline,
  BookOutline,
  BriefcaseOutline,
  BusinessOutline,
  ColorPalette,
  DocumentTextOutline,
  FolderOpenOutline,
  GlobeOutline,
  GridOutline,
  HomeOutline,
  MenuOutline,
  NotificationsOutline,
  PeopleOutline,
  SettingsOutline,
  ShieldCheckmarkOutline,
  TimeOutline,
} from '@vicons/ionicons5'

export interface MenuIconOption {
  value: string
  label: string
  component: Component
}

export const menuIconOptions: readonly MenuIconOption[] = [
  { value: 'HomeOutline', label: '首页', component: HomeOutline },
  { value: 'AnalyticsOutline', label: '系统监控', component: AnalyticsOutline },
  { value: 'PeopleOutline', label: '用户', component: PeopleOutline },
  { value: 'ShieldCheckmarkOutline', label: '角色', component: ShieldCheckmarkOutline },
  { value: 'MenuOutline', label: '菜单', component: MenuOutline },
  { value: 'BusinessOutline', label: '部门', component: BusinessOutline },
  { value: 'BriefcaseOutline', label: '岗位', component: BriefcaseOutline },
  { value: 'BookOutline', label: '字典', component: BookOutline },
  { value: 'FolderOpenOutline', label: '文件', component: FolderOpenOutline },
  { value: 'SettingsOutline', label: '配置', component: SettingsOutline },
  { value: 'NotificationsOutline', label: '通知', component: NotificationsOutline },
  { value: 'DocumentTextOutline', label: '日志', component: DocumentTextOutline },
  { value: 'GlobeOutline', label: '在线用户', component: GlobeOutline },
  { value: 'TimeOutline', label: '定时任务', component: TimeOutline },
  { value: 'ColorPalette', label: '调色板', component: ColorPalette },
]

const menuIconMap: Record<string, Component> = {
  '#': GridOutline,
  colorpalette: ColorPalette,
  colorpaletteoutline: ColorPalette,
  analytics: AnalyticsOutline,
  analyticsoutline: AnalyticsOutline,
  home: HomeOutline,
  homeoutline: HomeOutline,
  dashboard: HomeOutline,
  people: PeopleOutline,
  peopleoutline: PeopleOutline,
  user: PeopleOutline,
  users: PeopleOutline,
  shieldcheckmark: ShieldCheckmarkOutline,
  shieldcheckmarkoutline: ShieldCheckmarkOutline,
  role: ShieldCheckmarkOutline,
  menu: MenuOutline,
  menuoutline: MenuOutline,
  dept: BusinessOutline,
  department: BusinessOutline,
  business: BusinessOutline,
  businessoutline: BusinessOutline,
  post: BriefcaseOutline,
  briefcase: BriefcaseOutline,
  briefcaseoutline: BriefcaseOutline,
  dict: BookOutline,
  dictionary: BookOutline,
  book: BookOutline,
  bookoutline: BookOutline,
  file: FolderOpenOutline,
  folder: FolderOpenOutline,
  folderopenoutline: FolderOpenOutline,
  config: SettingsOutline,
  setting: SettingsOutline,
  settings: SettingsOutline,
  settingsoutline: SettingsOutline,
  notice: NotificationsOutline,
  notification: NotificationsOutline,
  notifications: NotificationsOutline,
  notificationsoutline: NotificationsOutline,
  log: DocumentTextOutline,
  logs: DocumentTextOutline,
  documenttext: DocumentTextOutline,
  documenttextoutline: DocumentTextOutline,
  online: GlobeOutline,
  globe: GlobeOutline,
  globeoutline: GlobeOutline,
  job: TimeOutline,
  time: TimeOutline,
  timeoutline: TimeOutline,
}

const normalizeIconKey = (value: string | null): string => value?.trim().toLowerCase() ?? ''

export const resolveMenuIcon = (iconKey: string | null): Component => {
  const normalizedKey = normalizeIconKey(iconKey)
  return menuIconMap[normalizedKey] ?? GridOutline
}
