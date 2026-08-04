export type SearchFormDemoStatus = 'all' | 'enabled' | 'disabled'

export interface SearchFormDemoModel {
  [key: string]: unknown
  keyword: string
  status: SearchFormDemoStatus
  owner: string | null
  category: string | null
  updatedAt: [number, number] | null
  minCount: number | null
  includeArchived: boolean
}

export interface SearchFormDemoRecord {
  id: string
  name: string
  code: string
  category: string
  status: Exclude<SearchFormDemoStatus, 'all'>
  owner: string
  updatedAt: number
  count: number
  archived: boolean
  tags: string[]
}
