import type { HooksDemoQuery, HooksDemoRecord, PaginationRequest, PaginationResult } from '@/types'

const demoRecords: HooksDemoRecord[] = [
  {
    id: 'hook-001',
    name: 'usePagination',
    category: 'request',
    status: 'active',
    owner: '前端基础设施',
    updatedAt: '2026-08-05 09:20',
    description: '统一管理 page、size、loading 和列表响应。',
  },
  {
    id: 'hook-002',
    name: 'useTheme',
    category: 'state',
    status: 'active',
    owner: '应用壳层',
    updatedAt: '2026-08-04 17:40',
    description: '同步主题偏好、Naive UI 主题和根节点状态。',
  },
  {
    id: 'hook-003',
    name: 'useLocale',
    category: 'state',
    status: 'active',
    owner: '应用壳层',
    updatedAt: '2026-08-04 15:10',
    description: '提供响应式语言状态和类型安全的界面词典。',
  },
  {
    id: 'hook-004',
    name: 'useRouteCache',
    category: 'lifecycle',
    status: 'active',
    owner: 'BasicLayout',
    updatedAt: '2026-08-03 16:30',
    description: '为 KeepAlive 路由生成隔离的缓存组件名称。',
  },
  {
    id: 'hook-005',
    name: 'useLottie',
    category: 'lifecycle',
    status: 'active',
    owner: 'Loading 组件',
    updatedAt: '2026-08-03 11:45',
    description: '管理动画实例的加载、播放、暂停和销毁。',
  },
  {
    id: 'hook-006',
    name: 'useECharts',
    category: 'lifecycle',
    status: 'paused',
    owner: '数据可视化',
    updatedAt: '2026-08-02 14:25',
    description: '绑定图表容器、响应尺寸变化并清理实例。',
  },
  {
    id: 'hook-007',
    name: 'useDocumentTitle',
    category: 'lifecycle',
    status: 'active',
    owner: '应用壳层',
    updatedAt: '2026-08-02 10:05',
    description: '监听路由和语言变化，更新浏览器标题。',
  },
  {
    id: 'hook-008',
    name: 'useRequestFeedback',
    category: 'request',
    status: 'paused',
    owner: '请求基础设施',
    updatedAt: '2026-08-01 18:20',
    description: '把请求错误反馈桥接到全局 Message 展示。',
  },
  {
    id: 'hook-009',
    name: 'useAuthSession',
    category: 'state',
    status: 'archived',
    owner: '认证模块',
    updatedAt: '2026-07-31 13:15',
    description: '历史会话行为已迁移到 auth Store。',
  },
  {
    id: 'hook-010',
    name: 'useRouteLoading',
    category: 'request',
    status: 'active',
    owner: '路由基础设施',
    updatedAt: '2026-07-31 09:50',
    description: '协调屏幕级和内容区级路由 Loading 状态。',
  },
  {
    id: 'hook-011',
    name: 'usePreferences',
    category: 'state',
    status: 'active',
    owner: '系统设置',
    updatedAt: '2026-07-30 16:05',
    description: '集中管理外观、布局和通用偏好配置。',
  },
  {
    id: 'hook-012',
    name: 'useFormState',
    category: 'state',
    status: 'paused',
    owner: '表单演示',
    updatedAt: '2026-07-30 11:35',
    description: '候选表单状态抽象，当前由 AppForm 负责。',
  },
  {
    id: 'hook-013',
    name: 'useResizeObserver',
    category: 'lifecycle',
    status: 'archived',
    owner: '组件基础设施',
    updatedAt: '2026-07-29 15:45',
    description: '已收敛到图表 Hook 内部，避免重复暴露。',
  },
  {
    id: 'hook-014',
    name: 'useMessageBridge',
    category: 'request',
    status: 'active',
    owner: '请求基础设施',
    updatedAt: '2026-07-29 10:25',
    description: '为页面提供统一的请求成功和失败反馈入口。',
  },
  {
    id: 'hook-015',
    name: 'useTabState',
    category: 'state',
    status: 'active',
    owner: '标签页模块',
    updatedAt: '2026-07-28 17:05',
    description: '标签页跨路由状态由 Pinia Store 统一持久化。',
  },
]

const matchesQuery = (record: HooksDemoRecord, query: HooksDemoQuery): boolean => {
  const keyword = query.keyword.trim().toLowerCase()
  const keywordMatches =
    keyword.length === 0 ||
    `${record.name} ${record.owner} ${record.description}`.toLowerCase().includes(keyword)
  const categoryMatches = query.category === 'all' || record.category === query.category
  const statusMatches = query.status === 'all' || record.status === query.status

  return keywordMatches && categoryMatches && statusMatches
}

export const fetchHooksDemoPage = async (
  params: PaginationRequest,
  query: HooksDemoQuery,
): Promise<PaginationResult<HooksDemoRecord>> => {
  await new Promise<void>((resolve) => {
    window.setTimeout(resolve, 280)
  })

  const filteredRecords = demoRecords.filter((record) => matchesQuery(record, query))
  const total = filteredRecords.length
  const pages = Math.ceil(total / params.size)
  const page = pages === 0 ? 1 : Math.min(params.page, pages)
  const start = (page - 1) * params.size

  return {
    items: filteredRecords.slice(start, start + params.size),
    total,
    page,
    size: params.size,
    pages,
  }
}
