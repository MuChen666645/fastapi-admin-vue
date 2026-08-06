<script setup lang="ts">
import { computed, h, reactive } from 'vue'
import {
  CodeSlashOutline,
  GitBranchOutline,
  InformationCircleOutline,
  RefreshOutline,
  SearchOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { usePagination } from '@/hooks'
import type {
  AppFormField,
  HooksDemoCategory,
  HooksDemoQuery,
  HooksDemoRecord,
  HooksDemoStatus,
} from '@/types'

import { fetchHooksDemoPage } from './data'

defineOptions({ name: 'HooksDemoView' })

const createInitialQuery = (): HooksDemoQuery => ({
  keyword: '',
  category: 'all',
  status: 'all',
})

const query = reactive<HooksDemoQuery>(createInitialQuery())
const appliedQuery = reactive<HooksDemoQuery>(createInitialQuery())
const { data, error, loading, page, pageSize, total, pagination, refresh, reset } = usePagination(
  (params) => fetchHooksDemoPage(params, appliedQuery),
  {
    initialPageSize: 5,
    pageSizes: [5, 10, 20],
  },
)

const categoryOptions = [
  { label: '全部场景', value: 'all' as const },
  { label: '生命周期', value: 'lifecycle' as const },
  { label: '请求协调', value: 'request' as const },
  { label: '状态管理', value: 'state' as const },
]

const statusOptions = [
  { label: '全部状态', value: 'all' as const },
  { label: '使用中', value: 'active' as const },
  { label: '暂停维护', value: 'paused' as const },
  { label: '已归档', value: 'archived' as const },
]

const initialQuery = createInitialQuery()
const fields: AppFormField<HooksDemoQuery>[] = [
  {
    key: 'keyword',
    path: 'keyword',
    label: '关键词',
    componentProps: {
      clearable: true,
      placeholder: '搜索 Hook 名称、维护方或说明',
    },
  },
  {
    key: 'category',
    path: 'category',
    label: '分类',
    type: 'select',
    componentProps: { options: categoryOptions },
  },
  {
    key: 'status',
    path: 'status',
    label: '状态',
    type: 'select',
    componentProps: { options: statusOptions },
  },
]

const categoryLabel: Record<HooksDemoCategory, string> = {
  lifecycle: '生命周期',
  request: '请求协调',
  state: '状态管理',
}

const statusLabel: Record<HooksDemoStatus, string> = {
  active: '使用中',
  paused: '暂停维护',
  archived: '已归档',
}

const statusTagType = (status: HooksDemoStatus): 'success' | 'warning' | 'default' => {
  if (status === 'active') {
    return 'success'
  }

  if (status === 'paused') {
    return 'warning'
  }

  return 'default'
}

const columns = [
  {
    title: 'Hook',
    key: 'name',
    minWidth: 180,
    render: (record: HooksDemoRecord) =>
      h('div', { class: 'hooks-demo-hook-cell' }, [
        h('strong', record.name),
        h('span', record.description),
      ]),
  },
  {
    title: '场景',
    key: 'category',
    width: 110,
    render: (record: HooksDemoRecord) => categoryLabel[record.category],
  },
  {
    title: '状态',
    key: 'status',
    width: 110,
    render: (record: HooksDemoRecord) =>
      h(
        NTag,
        { type: statusTagType(record.status), size: 'small', round: true },
        { default: () => statusLabel[record.status] },
      ),
  },
  {
    title: '维护方',
    key: 'owner',
    width: 140,
  },
  {
    title: '最近更新',
    key: 'updatedAt',
    width: 150,
  },
]

const rowKey = (record: HooksDemoRecord): string => record.id
const requestSummary = computed(() => `page=${page.value} · size=${pageSize.value}`)

const applyQuery = (nextQuery: HooksDemoQuery): void => {
  Object.assign(appliedQuery, nextQuery)
}

const handleSearch = async (nextQuery: HooksDemoQuery): Promise<void> => {
  applyQuery(nextQuery)
  await reset()
}

const handleReset = async (nextQuery: HooksDemoQuery): Promise<void> => {
  applyQuery(nextQuery)
  await reset()
}
</script>

<template>
  <main class="hooks-demo-page">
    <section class="hooks-demo-filter-panel" aria-labelledby="hooks-filter-title">
      <div class="hooks-demo-panel-heading">
        <div>
          <h2 id="hooks-filter-title">筛选演示数据</h2>
          <p>查询使用统一 AppSearchForm，分页 Hook 只接收标准的 page 和 size。</p>
        </div>
        <NIcon :size="24" color="var(--app-color-primary)" aria-hidden="true">
          <SearchOutline />
        </NIcon>
      </div>

      <AppSearchForm
        :model="query"
        :initial-values="initialQuery"
        :fields="fields"
        :loading="loading"
        :layout="{
          labelPlacement: 'top',
          labelWidth: 'auto',
          columns: '1 s:2 m:3',
          responsive: 'screen',
          xGap: 20,
          yGap: 6,
          actionAlign: 'end',
        }"
        @search="handleSearch"
        @reset="handleReset"
      />
    </section>

    <div class="hooks-demo-layout">
      <section class="hooks-demo-results-panel" aria-labelledby="hooks-results-title">
        <div class="hooks-demo-panel-heading">
          <div>
            <h2 id="hooks-results-title">分页结果</h2>
            <p>共 {{ total }} 条记录 · 当前请求：{{ requestSummary }}</p>
          </div>
          <NButton
            quaternary
            circle
            :loading="loading"
            aria-label="刷新分页数据"
            title="刷新分页数据"
            @click="refresh"
          >
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
          </NButton>
        </div>

        <div v-if="error" class="hooks-demo-error">
          <NAlert type="error" :show-icon="false">分页数据加载失败，请重试。</NAlert>
          <NButton size="small" @click="refresh">重试</NButton>
        </div>

        <NDataTable
          :columns="columns"
          :data="data"
          :loading="loading"
          remote
          :row-key="rowKey"
          :pagination="pagination"
          :scroll-x="760"
        >
          <template #empty>
            <NEmpty description="没有匹配的 Hook 记录" />
          </template>
        </NDataTable>
      </section>

      <aside class="hooks-demo-aside" aria-labelledby="hooks-guide-title">
        <NAlert type="info" :show-icon="false" class="hooks-demo-note">
          <strong>演示边界</strong>
          <p>
            本页使用页面私有的异步适配器模拟列表请求，不新增后端接口；接入业务页面时替换为领域 API
            即可。
          </p>
        </NAlert>

        <section class="hooks-demo-guide">
          <div class="hooks-demo-guide-heading">
            <NIcon :size="18" aria-hidden="true"><InformationCircleOutline /></NIcon>
            <h2 id="hooks-guide-title">本页覆盖能力</h2>
          </div>
          <ul>
            <li>
              <NIcon :size="16" aria-hidden="true"><CodeSlashOutline /></NIcon
              ><span>统一传递后端 page / size 参数</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><RefreshOutline /></NIcon
              ><span>查询、重置和刷新共享同一加载状态</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><GitBranchOutline /></NIcon
              ><span>NDataTable 内置分页自动触发列表更新</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </main>
</template>

<style lang="scss" scoped>
.hooks-demo-page {
  display: grid;
  gap: 20px;
  min-width: 0;
  color: var(--app-color-text);
}

.hooks-demo-panel-heading,
.hooks-demo-guide-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.hooks-demo-panel-heading h2,
.hooks-demo-panel-heading p,
.hooks-demo-guide-heading h2,
.hooks-demo-note p {
  margin: 0;
}

.hooks-demo-panel-heading p {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 14px;
}

.hooks-demo-filter-panel,
.hooks-demo-results-panel,
.hooks-demo-guide {
  min-width: 0;
  padding: 24px;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.hooks-demo-panel-heading {
  align-items: center;
  margin-bottom: 20px;
}

.hooks-demo-panel-heading h2,
.hooks-demo-guide-heading h2 {
  font-size: 16px;
  line-height: 1.4;
}

.hooks-demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
  align-items: start;
  gap: 20px;
}

.hooks-demo-results-panel {
  overflow: hidden;
}

.hooks-demo-results-panel :deep(.n-data-table) {
  margin: 0 -24px;
}

.hooks-demo-hook-cell {
  display: grid;
  gap: 4px;
}

.hooks-demo-hook-cell strong {
  color: var(--app-color-text);
}

.hooks-demo-hook-cell span {
  color: var(--app-color-text-muted);
  font-size: 12px;
  line-height: 1.5;
}

.hooks-demo-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.hooks-demo-error .n-alert {
  flex: 1;
}

.hooks-demo-aside {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.hooks-demo-note {
  line-height: 1.6;
}

.hooks-demo-note p {
  margin-top: 6px;
}

.hooks-demo-guide {
  padding: 18px;
}

.hooks-demo-guide-heading {
  align-items: center;
  justify-content: flex-start;
  color: var(--app-color-primary);
}

.hooks-demo-guide-heading h2 {
  color: var(--app-color-text);
}

.hooks-demo-guide ul {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.hooks-demo-guide li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.hooks-demo-guide li .n-icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--app-color-primary);
}

@media (width <= 880px) {
  .hooks-demo-layout {
    grid-template-columns: 1fr;
  }
}

@media (width <= 640px) {
  .hooks-demo-filter-panel,
  .hooks-demo-results-panel {
    padding: 16px;
  }

  .hooks-demo-results-panel :deep(.n-data-table) {
    margin: 0 -16px;
  }
}
</style>
