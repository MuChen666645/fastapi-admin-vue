import type { Component } from 'vue'

export type DashboardCardTone = 'positive' | 'negative' | 'warning'

export interface DashboardSummaryCard {
  label: string
  value: string
  change: string
  context: string
  tone: DashboardCardTone
  icon: Component
}

export interface DashboardQuickAction {
  label: string
  icon: Component
  tone: string
}

export interface DashboardAnnouncement {
  title: string
  date: string
}

export interface DashboardActivity {
  user: string
  action: string
  time: string
}
