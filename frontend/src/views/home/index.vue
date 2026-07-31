<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  BarChartOutline,
  CashOutline,
  CartOutline,
  HelpCircleOutline,
  KeyOutline,
  PersonAddOutline,
  PeopleOutline,
  SettingsOutline,
  TimeOutline,
} from '@vicons/ionicons5'
import type { EChartsOption } from 'echarts'
import { NIcon } from 'naive-ui'

import { useECharts } from '@/hooks/useECharts'
import { useTheme } from '@/hooks/useTheme'
import { useAuthStore } from '@/stores'
import type {
  DashboardActivity,
  DashboardAnnouncement,
  DashboardQuickAction,
  DashboardSummaryCard,
} from '@/types'

defineOptions({ name: 'HomeView' })

const auth = useAuthStore()
const { isDarkMode } = useTheme()
const trendChart = ref<HTMLElement | null>(null)
const channelChart = ref<HTMLElement | null>(null)

const displayName = computed(() => auth.displayName || '超级管理员')

const summaryCards: DashboardSummaryCard[] = [
  {
    label: '今日订单',
    value: '1,482',
    change: '+12.4%',
    context: '较昨日同期',
    tone: 'positive',
    icon: CartOutline,
  },
  {
    label: '销售额 (元)',
    value: '¥ 128,450',
    change: '+8.2%',
    context: '较昨日同期',
    tone: 'positive',
    icon: CashOutline,
  },
  {
    label: '新增用户',
    value: '328',
    change: '-2.4%',
    context: '较昨日同期',
    tone: 'negative',
    icon: PersonAddOutline,
  },
  {
    label: '待处理事项',
    value: '14',
    change: '需尽快处理',
    context: '较昨日同期',
    tone: 'warning',
    icon: TimeOutline,
  },
]

const quickActions: DashboardQuickAction[] = [
  { label: '添加用户', icon: PeopleOutline, tone: 'blue' },
  { label: '角色授权', icon: KeyOutline, tone: 'purple' },
  { label: '配置中心', icon: SettingsOutline, tone: 'pink' },
  { label: '订单中心', icon: CartOutline, tone: 'green' },
  { label: '数据监控', icon: BarChartOutline, tone: 'yellow' },
  { label: '操作指南', icon: HelpCircleOutline, tone: 'gray' },
]

const announcements: DashboardAnnouncement[] = [
  { title: '系统计划于本周日进行停机维护通知', date: '09-30' },
  { title: '安全审计中心功能全面升级正式上线', date: '09-28' },
  { title: '关于节假日业务备份及值班安排', date: '09-25' },
]

const activities: DashboardActivity[] = [
  { user: '管理员A', action: '修改了用户角色权限', time: '10分钟前' },
  { user: '运营B', action: '导出了今日订单数据', time: '30分钟前' },
  { user: '系统', action: '完成系统全量安全备份', time: '1小时前' },
]

const chartColors = computed(() => ({
  axis: isDarkMode.value ? '#b7bdd8' : '#999',
  border: isDarkMode.value ? '#3c4260' : '#e5e7eb',
  grid: isDarkMode.value ? '#303650' : '#f0f2f5',
  line: isDarkMode.value ? '#aeb8f3' : '#6c7ce5',
  bar: isDarkMode.value ? '#6fd1a0' : '#18a058',
}))

const trendOption = computed<EChartsOption>(() => ({
  animationDuration: 500,
  grid: { top: 12, right: 8, bottom: 24, left: 8, containLabel: true },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'line' },
    valueFormatter: (value) => `${value} 单`,
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLine: { lineStyle: { color: chartColors.value.border } },
    axisTick: { show: false },
    axisLabel: { color: chartColors.value.axis, fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    splitNumber: 3,
    axisLabel: { color: chartColors.value.axis, fontSize: 11 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: chartColors.value.grid } },
  },
  series: [
    {
      type: 'line',
      data: [420, 680, 510, 1120, 820, 1380, 1240],
      smooth: false,
      symbol: 'none',
      lineStyle: { color: chartColors.value.line, width: 2 },
    },
  ],
}))

const channelOption = computed<EChartsOption>(() => ({
  animationDuration: 500,
  grid: { top: 12, right: 8, bottom: 24, left: 8, containLabel: true },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    valueFormatter: (value) => `${value} 万元`,
  },
  xAxis: {
    type: 'category',
    data: ['官网', '小程序', '代理商', '线下门店', '合作渠道', '其他', '分销'],
    axisLine: { lineStyle: { color: chartColors.value.border } },
    axisTick: { show: false },
    axisLabel: { color: chartColors.value.axis, fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    splitNumber: 3,
    axisLabel: { color: chartColors.value.axis, fontSize: 11 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: chartColors.value.grid } },
  },
  series: [
    {
      type: 'bar',
      barMaxWidth: 42,
      data: [82, 104, 118, 52, 130, 146, 112],
      itemStyle: { color: chartColors.value.bar, borderRadius: [4, 4, 0, 0] },
    },
  ],
}))

const { renderChart: renderTrendChart } = useECharts(trendChart, () => trendOption.value)
const { renderChart: renderChannelChart } = useECharts(channelChart, () => channelOption.value)

watch(isDarkMode, () => {
  renderTrendChart()
  renderChannelChart()
})
</script>

<template>
  <section class="home-page">
    <div class="page-heading">
      <h1>数据概览</h1>
    </div>

    <div class="summary-grid">
      <article v-for="card in summaryCards" :key="card.label" class="summary-card">
        <div class="summary-card-header">
          <span class="summary-label">{{ card.label }}</span>
          <span class="summary-icon" :class="`summary-icon--${card.tone}`">
            <NIcon :size="17"><component :is="card.icon" /></NIcon>
          </span>
        </div>
        <strong class="summary-value">{{ card.value }}</strong>
        <div class="summary-footnote">
          <span class="summary-change" :class="`summary-change--${card.tone}`">{{
            card.change
          }}</span>
          <span>{{ card.context }}</span>
        </div>
      </article>
    </div>

    <div class="chart-grid">
      <article class="content-card chart-card">
        <div class="card-heading">
          <h2>近七天趋势</h2>
          <span>单位: 单</span>
        </div>
        <div ref="trendChart" class="chart-container" aria-label="近七天订单趋势图" />
      </article>
      <article class="content-card chart-card">
        <div class="card-heading">
          <h2>渠道订单统计</h2>
          <span>单位: 万元</span>
        </div>
        <div ref="channelChart" class="chart-container" aria-label="渠道订单统计图" />
      </article>
    </div>

    <div class="lower-grid">
      <article class="content-card quick-card">
        <h2>快捷入口</h2>
        <div class="quick-actions">
          <button
            v-for="action in quickActions"
            :key="action.label"
            type="button"
            class="quick-action"
          >
            <span class="quick-action-icon" :class="`quick-action-icon--${action.tone}`">
              <NIcon :size="20"><component :is="action.icon" /></NIcon>
            </span>
            <span>{{ action.label }}</span>
          </button>
        </div>
      </article>

      <article class="content-card list-card">
        <h2>系统公告</h2>
        <ul class="announcement-list">
          <li v-for="item in announcements" :key="item.date">
            <span>{{ item.title }}</span>
            <time>{{ item.date }}</time>
          </li>
        </ul>
      </article>

      <article class="content-card list-card">
        <h2>最近操作记录</h2>
        <ul class="activity-list">
          <li v-for="item in activities" :key="`${item.user}-${item.time}`">
            <span class="activity-dot" aria-hidden="true" />
            <div>
              <p>
                <strong>{{ item.user }}</strong
                >{{ ` ${item.action}` }}
              </p>
              <time>{{ item.time }}</time>
            </div>
          </li>
        </ul>
      </article>
    </div>

    <p class="dashboard-greeting">欢迎回来，{{ displayName }}</p>
  </section>
</template>

<style scoped>
.home-page {
  --home-primary: var(--app-color-primary);
  --home-primary-dark: var(--app-color-primary-dark);
  --home-text: var(--app-color-text);
  --home-muted: var(--app-color-text-muted);
  --home-border: var(--app-color-border);
  --home-divider: var(--app-color-surface-muted);

  display: grid;
  gap: 20px;
  color: var(--home-text);
}

.page-heading {
  display: grid;
  gap: 8px;
}

.page-heading h1,
.content-card h2 {
  margin: 0;
}

.page-heading h1 {
  color: var(--home-text);
  font-size: 22px;
  font-weight: 700;
  line-height: 1.25;
}

.summary-grid,
.chart-grid,
.lower-grid {
  display: grid;
  gap: 16px;
}

.summary-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.chart-grid {
  min-width: 0;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.lower-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.summary-card,
.content-card {
  min-width: 0;
  border: 1px solid var(--home-border);
  border-radius: 12px;
  background: var(--app-color-surface);
  box-shadow: 0 8px 24px rgb(109 119 171 / 7%);
}

.summary-card {
  display: grid;
  gap: 12px;
  min-height: 142px;
  padding: 20px;
}

.summary-card-header,
.card-heading,
.summary-footnote {
  display: flex;
  align-items: center;
}

.summary-card-header,
.card-heading {
  justify-content: space-between;
}

.summary-label {
  color: var(--home-muted);
  font-size: 14px;
}

.summary-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 8px;
  color: var(--home-primary);
  background: var(--app-color-primary-soft);
}

.summary-value {
  color: var(--home-text);
  font-size: 24px;
  line-height: 1;
}

.summary-footnote {
  justify-content: flex-start;
  gap: 4px;
  color: #9ba1b6;
  font-size: 12px;
}

.summary-change {
  font-weight: 600;
}

.summary-change--positive {
  color: var(--app-color-success);
}

.summary-change--negative {
  color: var(--app-color-danger);
}

.summary-change--warning {
  color: var(--app-color-warning);
}

.content-card {
  padding: 20px;
}

.card-heading {
  min-width: 0;
  gap: 12px;
}

.card-heading h2,
.content-card h2 {
  min-width: 0;
  color: var(--home-text);
  font-size: 16px;
  font-weight: 700;
  line-height: 1.4;
}

.card-heading span {
  flex: 0 0 auto;
  color: var(--home-muted);
  font-size: 12px;
  white-space: nowrap;
}

.chart-card {
  display: grid;
  gap: 10px;
  min-width: 0;
  overflow: hidden;
}

.chart-container {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  height: 200px;
  overflow: hidden;
}

.quick-card,
.list-card {
  min-height: 186px;
}

.quick-card {
  display: grid;
  gap: 16px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.quick-action {
  display: grid;
  min-width: 0;
  gap: 7px;
  padding: 10px 6px;
  place-items: center;
  color: var(--home-text);
  border: 0;
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
}

.quick-action:hover,
.quick-action:focus-visible {
  background: var(--app-color-surface-muted);
  outline: none;
}

.quick-action-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 10px;
}

.quick-action-icon--blue {
  color: var(--app-color-primary);
  background: var(--app-color-primary-soft);
}

.quick-action-icon--purple {
  color: var(--app-color-primary-dark);
  background: var(--app-color-primary-soft);
}

.quick-action-icon--pink {
  color: var(--app-color-danger);
  background: var(--app-color-danger-soft);
}

.quick-action-icon--green {
  color: var(--app-color-success);
  background: var(--app-color-success-soft);
}

.quick-action-icon--yellow {
  color: var(--app-color-warning);
  background: var(--app-color-warning-soft);
}

.quick-action-icon--gray {
  color: var(--home-muted);
  background: var(--app-color-neutral-soft);
}

.list-card {
  display: grid;
  align-content: start;
  gap: 16px;
}

.announcement-list,
.activity-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.announcement-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--home-divider);
  color: var(--home-text);
  font-size: 13px;
}

.announcement-list li span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.announcement-list time,
.activity-list time {
  flex: 0 0 auto;
  color: #9ba1b6;
  font-size: 12px;
}

.activity-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.activity-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  margin-top: 5px;
  border-radius: 3px;
  background: var(--home-primary);
}

.activity-list p {
  margin: 0 0 2px;
  color: var(--home-text);
  font-size: 13px;
}

.dashboard-greeting {
  display: none;
}

@media (width <= 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .lower-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 760px) {
  .chart-grid,
  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 520px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .content-card,
  .summary-card {
    padding: 16px;
  }

  .chart-container {
    height: 180px;
  }
}
</style>
