import type { PaginationRequest } from './pagination'

export type MessageType = 'system' | 'approval' | 'alarm'

export type MessageStatus = '0' | '1'

export type MessageReadStatus = 'all' | 'unread' | 'read'

export type MessageDeliveryChannel = 'inbox' | 'webhook' | 'email' | 'sms'

export type MessageVisualTone = 'danger' | 'warning' | 'info'

export type MessageTab = MessageType

export type MessageViewMode = 'inbox' | 'manage'

export interface MessageItem {
  id: number
  message_title: string
  message_type: MessageType
  message_content: string
  publish_time: string | null
  read_at: string | null
}

export interface MessageListItem {
  id: number
  message_title: string
  message_type: MessageType
  message_content: string
  status: MessageStatus
  publish_time: string | null
  create_by: number | null
  create_time: string
  update_time: string
}

export type MessageDetail = MessageListItem

export type MessageDetailView = MessageDetail | MessageItem

export interface MessageListFilters {
  [key: string]: unknown
  title: string
  content: string
  message_type: MessageType | null
  status: MessageStatus | null
  publish_time: [number, number] | null
}

export interface MessageListQuery extends PaginationRequest {
  title?: string
  content?: string
  message_type?: MessageType
  status?: MessageStatus
  start_time?: string
  end_time?: string
}

export interface MyMessageFilters {
  [key: string]: unknown
  keyword: string
  message_type: MessageType | null
  read_status: MessageReadStatus
  publish_time: [number, number] | null
}

export interface MyMessageQuery extends PaginationRequest {
  keyword?: string
  message_type?: MessageType
  read_status?: MessageReadStatus
  start_time?: string
  end_time?: string
}

export interface MessageLatestResult {
  system: MessageItem[]
  approval: MessageItem[]
  alarm: MessageItem[]
}

export interface MessageUnreadCountResult {
  unread_count: number
}

export interface MessageReadAllResult {
  updated_count: number
}

export interface MessageCreatePayload {
  message_title: string
  message_type: MessageType
  message_content: string
  status: MessageStatus
  publish_time: string | null
  recipient_user_ids: number[]
  delivery_channels: MessageDeliveryChannel[]
}

export interface MessageUpdatePayload {
  message_title?: string
  message_type?: MessageType
  message_content?: string
  status?: MessageStatus
  publish_time?: string | null
}

export type MessageFormModel = Record<string, unknown> & {
  message_title: string
  message_type: MessageType
  message_content: string
  status: MessageStatus
  publish_time: number | null
  recipient_user_ids: string
  delivery_channels: MessageDeliveryChannel[]
}
