export type HooksDemoStatus = 'active' | 'paused' | 'archived'
export type HooksDemoCategory = 'lifecycle' | 'request' | 'state'

export interface HooksDemoQuery {
  [key: string]: unknown
  keyword: string
  category: HooksDemoCategory | 'all'
  status: HooksDemoStatus | 'all'
}

export interface HooksDemoRecord {
  id: string
  name: string
  category: HooksDemoCategory
  status: HooksDemoStatus
  owner: string
  updatedAt: string
  description: string
}
