<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import {
  CheckmarkCircleOutline,
  CodeSlashOutline,
  InformationCircleOutline,
  ListOutline,
  RefreshOutline,
  SearchOutline,
  TimeOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NEmpty, NIcon, NInput, NSpin, NTag, useMessage } from 'naive-ui'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import type {
  AppFormField,
  AppFormRecord,
  SearchFormDemoModel,
  SearchFormDemoRecord,
  SearchFormDemoStatus,
} from '@/types'

defineOptions({ name: 'SearchFormDemoView' })

const message = useMessage()
const loading = ref(false)
const hasSearched = ref(false)
const lastSearchAt = ref<number | null>(null)

const createInitialQuery = (): SearchFormDemoModel => ({
  keyword: '',
  status: 'all',
  owner: null,
  category: null,
  updatedAt: null,
  minCount: null,
  includeArchived: false,
})

const initialQuery = createInitialQuery()
const query = reactive<SearchFormDemoModel>(createInitialQuery())
const now = Date.now()

const records: SearchFormDemoRecord[] = [
  {
    id: 'record-001',
    name: '用户权限中心',
    code: 'AUTH-001',
    category: '平台能力',
    status: 'enabled',
    owner: '林晓',
    updatedAt: now - 2 * 24 * 60 * 60 * 1000,
    count: 128,
    archived: false,
    tags: ['RBAC', '核心模块'],
  },
  {
    id: 'record-002',
    name: '运营数据看板',
    code: 'DATA-014',
    category: '数据产品',
    status: 'enabled',
    owner: '周宁',
    updatedAt: now - 5 * 24 * 60 * 60 * 1000,
    count: 86,
    archived: false,
    tags: ['指标', '分析'],
  },
  {
    id: 'record-003',
    name: '供应商档案',
    code: 'SUP-008',
    category: '业务管理',
    status: 'disabled',
    owner: '陈默',
    updatedAt: now - 12 * 24 * 60 * 60 * 1000,
    count: 34,
    archived: false,
    tags: ['档案', '待复核'],
  },
  {
    id: 'record-004',
    name: '历史订单查询',
    code: 'ORDER-099',
    category: '业务管理',
    status: 'disabled',
    owner: '林晓',
    updatedAt: now - 35 * 24 * 60 * 60 * 1000,
    count: 210,
    archived: true,
    tags: ['归档', '订单'],
  },
  {
    id: 'record-005',
    name: '消息通知配置',
    code: 'MSG-021',
    category: '平台能力',
    status: 'enabled',
    owner: '赵可',
    updatedAt: now - 8 * 24 * 60 * 60 * 1000,
    count: 52,
    archived: false,
    tags: ['通知', '配置'],
  },
  {
    id: 'record-006',
    name: '旧版报表中心',
    code: 'REPORT-003',
    category: '数据产品',
    status: 'disabled',
    owner: '周宁',
    updatedAt: now - 60 * 24 * 60 * 60 * 1000,
    count: 17,
    archived: true,
    tags: ['归档', '报表'],
  },
]

const results = ref<SearchFormDemoRecord[]>(records)

const fields: AppFormField[] = [
  {
    key: 'keyword',
    path: 'keyword',
    label: '关键词',
    componentProps: { clearable: true, placeholder: '名称、编码或标签' },
  },
  {
    key: 'status',
    path: 'status',
    label: '状态',
    type: 'select',
    componentProps: {
      options: [
        { label: '全部状态', value: 'all' },
        { label: '启用', value: 'enabled' },
        { label: '停用', value: 'disabled' },
      ],
    },
  },
  {
    key: 'owner',
    path: 'owner',
    label: '负责人',
    type: 'select',
    componentProps: {
      clearable: true,
      placeholder: '全部负责人',
      options: [
        { label: '林晓', value: '林晓' },
        { label: '周宁', value: '周宁' },
        { label: '陈默', value: '陈默' },
        { label: '赵可', value: '赵可' },
      ],
    },
  },
  {
    key: 'category',
    path: 'category',
    label: '所属分类',
    type: 'select',
    componentProps: {
      clearable: true,
      placeholder: '全部分类',
      options: [
        { label: '平台能力', value: '平台能力' },
        { label: '数据产品', value: '数据产品' },
        { label: '业务管理', value: '业务管理' },
      ],
    },
  },
  {
    key: 'updatedAt',
    path: 'updatedAt',
    label: '更新时间',
    type: 'date',
    componentProps: { type: 'daterange', clearable: true, placeholder: '选择时间范围' },
  },
  {
    key: 'minCount',
    path: 'minCount',
    label: '最小数量',
    type: 'number',
    componentProps: { clearable: true, min: 0, placeholder: '不少于' },
  },
  {
    key: 'includeArchived',
    path: 'includeArchived',
    label: '包含归档项',
    type: 'switch',
  },
]

const statusLabel: Record<SearchFormDemoStatus, string> = {
  all: '全部',
  enabled: '启用',
  disabled: '停用',
}

const statusTagType = (status: SearchFormDemoRecord['status']): 'success' | 'warning' =>
  status === 'enabled' ? 'success' : 'warning'

const normalizeQuery = (model: AppFormRecord): SearchFormDemoModel => {
  const rawStatus = model.status
  const status: SearchFormDemoStatus =
    rawStatus === 'enabled' || rawStatus === 'disabled' ? rawStatus : 'all'
  const rawDateRange = model.updatedAt
  const updatedAt: [number, number] | null =
    Array.isArray(rawDateRange) && rawDateRange.length === 2
      ? [Number(rawDateRange[0]), Number(rawDateRange[1])]
      : null
  const rawMinCount = Number(model.minCount)

  return {
    keyword: typeof model.keyword === 'string' ? model.keyword.trim().toLowerCase() : '',
    status,
    owner: typeof model.owner === 'string' && model.owner ? model.owner : null,
    category: typeof model.category === 'string' && model.category ? model.category : null,
    updatedAt,
    minCount: Number.isFinite(rawMinCount) ? rawMinCount : null,
    includeArchived: model.includeArchived === true,
  }
}

const matchesQuery = (record: SearchFormDemoRecord, searchQuery: SearchFormDemoModel): boolean => {
  const keywordMatches = searchQuery.keyword
    ? `${record.name} ${record.code} ${record.tags.join(' ')}`
        .toLowerCase()
        .includes(searchQuery.keyword)
    : true
  const statusMatches = searchQuery.status === 'all' || record.status === searchQuery.status
  const ownerMatches = !searchQuery.owner || record.owner === searchQuery.owner
  const categoryMatches = !searchQuery.category || record.category === searchQuery.category
  const countMatches = searchQuery.minCount === null || record.count >= searchQuery.minCount
  const archivedMatches = searchQuery.includeArchived || !record.archived
  const dateMatches = searchQuery.updatedAt
    ? record.updatedAt >= searchQuery.updatedAt[0] && record.updatedAt <= searchQuery.updatedAt[1]
    : true

  return (
    keywordMatches &&
    statusMatches &&
    ownerMatches &&
    categoryMatches &&
    countMatches &&
    archivedMatches &&
    dateMatches
  )
}

const handleSearch = async (model: AppFormRecord): Promise<void> => {
  loading.value = true
  try {
    const searchQuery = normalizeQuery(model)
    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 350)
    })
    results.value = records.filter((record) => matchesQuery(record, searchQuery))
    hasSearched.value = true
    lastSearchAt.value = Date.now()
    message.success(`查询完成，共找到 ${results.value.length} 条记录`)
  } finally {
    loading.value = false
  }
}

const handleReset = (): void => {
  results.value = records
  hasSearched.value = false
  lastSearchAt.value = null
  message.info('筛选条件已重置')
}

const activeFilterCount = computed(() => {
  const values = [
    query.keyword,
    query.status !== 'all' ? query.status : null,
    query.owner,
    query.category,
    query.updatedAt,
    query.minCount,
    query.includeArchived ? true : null,
  ]
  return values.filter((value) => value !== null && value !== '' && value !== false).length
})

const resultSummary = computed(() => {
  if (!hasSearched.value) {
    return `示例数据 ${records.length} 条`
  }

  return `符合条件 ${results.value.length} 条`
})

const formatDate = (value: number): string =>
  new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(value)

const formatSearchTime = computed(() =>
  lastSearchAt.value ? new Intl.DateTimeFormat('zh-CN').format(lastSearchAt.value) : '尚未执行查询',
)
</script>

<template>
  <main class="search-form-demo-page">
    <section class="search-form-demo-panel search-form-demo-panel--filters">
      <div class="search-form-demo-panel__header">
        <div>
          <h2>资源筛选</h2>
          <p>默认展示常用条件，高级条件可以展开后继续参与查询。</p>
        </div>
        <div class="search-form-demo-filter-count">
          <span>已选条件</span>
          <strong>{{ activeFilterCount }}</strong>
        </div>
      </div>

      <AppSearchForm
        :model="query"
        :initial-values="initialQuery"
        :fields="fields"
        :loading="loading"
        default-collapsed
        :collapsed-fields="3"
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
      >
        <template #field-keyword="{ value, setValue }">
          <NInput
            :value="typeof value === 'string' ? value : ''"
            clearable
            placeholder="搜索名称、编码或标签"
            @update:value="setValue"
          />
        </template>

        <template
          #actions="{
            loading: formLoading,
            disabled: formDisabled,
            canToggle,
            collapsed,
            search,
            reset,
            toggle,
          }"
        >
          <NButton attr-type="button" :disabled="formDisabled" @click="reset">
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
            重置条件
          </NButton>
          <NButton
            v-if="canToggle"
            attr-type="button"
            secondary
            :disabled="formDisabled"
            class="search-form-demo-toggle"
            @click="toggle"
          >
            {{ collapsed ? '更多条件' : '收起条件' }}
          </NButton>
          <NButton
            attr-type="button"
            type="primary"
            :loading="formLoading"
            :disabled="formDisabled"
            class="search-form-demo-search-button"
            @click="search()"
          >
            <template #icon>
              <NIcon><SearchOutline /></NIcon>
            </template>
            查询结果
          </NButton>
        </template>
      </AppSearchForm>
    </section>

    <div class="search-form-demo-layout">
      <section
        class="search-form-demo-panel search-form-demo-results"
        aria-labelledby="result-title"
      >
        <div class="search-form-demo-panel__header">
          <div>
            <h2 id="result-title">查询结果</h2>
            <p>{{ resultSummary }} · 最近查询：{{ formatSearchTime }}</p>
          </div>
          <NIcon :size="24" color="var(--app-color-primary)" aria-hidden="true">
            <CheckmarkCircleOutline />
          </NIcon>
        </div>

        <NSpin :show="loading">
          <NEmpty v-if="results.length === 0" description="没有符合条件的记录" />
          <ul v-else class="search-form-demo-records">
            <li v-for="record in results" :key="record.id" class="search-form-demo-record">
              <div class="search-form-demo-record__main">
                <div class="search-form-demo-record__title">
                  <h3>{{ record.name }}</h3>
                  <NTag :type="statusTagType(record.status)" size="small" round>
                    {{ statusLabel[record.status] }}
                  </NTag>
                  <NTag v-if="record.archived" type="default" size="small" round>已归档</NTag>
                </div>
                <p>{{ record.code }} · {{ record.category }} · 负责人：{{ record.owner }}</p>
              </div>
              <div class="search-form-demo-record__meta">
                <span><TimeOutline aria-hidden="true" /> {{ formatDate(record.updatedAt) }}</span>
                <span><ListOutline aria-hidden="true" /> {{ record.count }} 项</span>
                <div class="search-form-demo-record__tags">
                  <NTag v-for="tag in record.tags" :key="tag" size="small">{{ tag }}</NTag>
                </div>
              </div>
            </li>
          </ul>
        </NSpin>
      </section>

      <aside class="search-form-demo-aside" aria-labelledby="search-guide-title">
        <NAlert type="info" :show-icon="false" class="search-form-demo-note">
          <strong>演示说明</strong>
          <p>提交会模拟短暂查询，用于观察 Loading 和重复提交保护；不会写入后端数据。</p>
        </NAlert>

        <section class="search-form-demo-guide">
          <div class="search-form-demo-guide__heading">
            <NIcon :size="18" aria-hidden="true"><InformationCircleOutline /></NIcon>
            <h2 id="search-guide-title">搜索表单规范</h2>
          </div>
          <ul class="search-form-demo-capabilities">
            <li>
              <NIcon :size="16" aria-hidden="true"><ListOutline /></NIcon>
              <span>常用条件优先展示，高级条件可折叠</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><CodeSlashOutline /></NIcon>
              <span>schema 驱动字段，自定义控件通过插槽接入</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><SearchOutline /></NIcon>
              <span>校验通过后才触发搜索，支持回车和显式查询</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><RefreshOutline /></NIcon>
              <span>重置恢复初始条件，查询期间禁止重复操作</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </main>
</template>

<style lang="scss" scoped>
.search-form-demo-page {
  display: grid;
  gap: 20px;
  min-width: 0;
  color: var(--app-color-text);
}

.search-form-demo-panel__header,
.search-form-demo-guide__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.search-form-demo-panel__header h2,
.search-form-demo-panel__header p,
.search-form-demo-guide__heading h2,
.search-form-demo-note p {
  margin: 0;
}

.search-form-demo-panel__header p {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 14px;
}

.search-form-demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
  align-items: start;
  gap: 20px;
}

.search-form-demo-panel,
.search-form-demo-guide {
  min-width: 0;
  padding: 24px;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.search-form-demo-panel--filters {
  padding-bottom: 20px;
}

.search-form-demo-panel__header {
  align-items: center;
  margin-bottom: 22px;
}

.search-form-demo-panel__header h2,
.search-form-demo-guide__heading h2 {
  font-size: 16px;
  line-height: 1.4;
}

.search-form-demo-filter-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.search-form-demo-filter-count strong {
  min-width: 24px;
  padding: 2px 7px;
  border-radius: 12px;
  color: var(--app-color-primary);
  background: var(--app-color-primary-soft);
  text-align: center;
}

.search-form-demo-search-button {
  min-width: 112px;
}

.search-form-demo-aside {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.search-form-demo-note {
  line-height: 1.6;
}

.search-form-demo-note p {
  margin-top: 6px;
}

.search-form-demo-guide {
  padding: 18px;
}

.search-form-demo-guide__heading {
  align-items: center;
  justify-content: flex-start;
  color: var(--app-color-primary);
}

.search-form-demo-guide__heading h2 {
  color: var(--app-color-text);
}

.search-form-demo-capabilities {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.search-form-demo-capabilities li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.search-form-demo-capabilities .n-icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--app-color-primary);
}

.search-form-demo-records {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.search-form-demo-record {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
}

.search-form-demo-record__main,
.search-form-demo-record__meta {
  min-width: 0;
}

.search-form-demo-record__title,
.search-form-demo-record__meta,
.search-form-demo-record__tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-form-demo-record__title h3 {
  margin: 0;
  font-size: 15px;
  line-height: 1.4;
}

.search-form-demo-record__main p {
  margin: 7px 0 0;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.search-form-demo-record__meta {
  flex-wrap: wrap;
  justify-content: flex-end;
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.search-form-demo-record__meta > span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.search-form-demo-record__tags {
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (width <= 880px) {
  .search-form-demo-layout {
    grid-template-columns: 1fr;
  }
}

@media (width <= 640px) {
  .search-form-demo-panel {
    padding: 16px;
  }

  .search-form-demo-record {
    align-items: flex-start;
  }

  .search-form-demo-record {
    flex-direction: column;
  }

  .search-form-demo-record__meta {
    justify-content: flex-start;
  }

  .search-form-demo-record__tags {
    justify-content: flex-start;
  }
}
</style>
