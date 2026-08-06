import type {
  MessageDetail,
  MessageItem,
  MessageLatestResult,
  MessageListItem,
  MessageReadAllResult,
  MessageStatus,
  MessageType,
  MessageUnreadCountResult,
} from '@/types'
import type { PaginationResult } from '@/types'
import { isRecord, readNumber, readString, requireNumber, requireString } from '@/utils/guards/api'
import { isMessageType } from '@/utils/message'

const requirePaginationNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const parsed = requireNumber(value, fieldName)
  if (!Number.isInteger(parsed) || parsed < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return parsed
}

const requireMessageType = (value: unknown): MessageType => {
  const messageType = requireString(value, 'message_type')
  if (!isMessageType(messageType)) {
    throw new Error('接口字段 message_type 无效')
  }

  return messageType
}

const requireMessageStatus = (value: unknown): MessageStatus => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseMessageItem = (value: unknown): MessageItem => {
  if (!isRecord(value)) {
    throw new Error('消息数据无效')
  }

  return {
    id: requirePaginationNumber(value.id, 'id', 1),
    message_title: requireString(value.message_title, 'message_title'),
    message_type: requireMessageType(value.message_type),
    message_content: requireString(value.message_content, 'message_content'),
    publish_time: readString(value.publish_time),
    read_at: readString(value.read_at),
  }
}

const parseMessageListItem = (value: unknown): MessageListItem => {
  if (!isRecord(value)) {
    throw new Error('消息管理列表数据无效')
  }

  return {
    ...parseMessageItem({ ...value, read_at: null }),
    status: requireMessageStatus(value.status),
    create_by: readNumber(value.create_by),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

export const parseMessageListPage = (value: unknown): PaginationResult<MessageListItem> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('消息管理分页响应无效')
  }

  return {
    items: value.items.map(parseMessageListItem),
    total: requirePaginationNumber(value.total, 'total', 0),
    page: requirePaginationNumber(value.page, 'page', 1),
    size: requirePaginationNumber(value.size, 'size', 1),
    pages: requirePaginationNumber(value.pages, 'pages', 0),
  }
}

export const parseMyMessageListPage = (value: unknown): PaginationResult<MessageItem> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('我的消息分页响应无效')
  }

  return {
    items: value.items.map(parseMessageItem),
    total: requirePaginationNumber(value.total, 'total', 0),
    page: requirePaginationNumber(value.page, 'page', 1),
    size: requirePaginationNumber(value.size, 'size', 1),
    pages: requirePaginationNumber(value.pages, 'pages', 0),
  }
}

export const parseMessageDetail = (value: unknown): MessageDetail => parseMessageListItem(value)

export const parseMyMessageDetail = (value: unknown): MessageItem => parseMessageItem(value)

const parseLatestItems = (value: unknown, messageType: MessageType): MessageItem[] => {
  if (!Array.isArray(value)) {
    throw new Error(`最新${messageType}消息数据无效`)
  }

  return value.map(parseMessageItem)
}

export const parseMessageLatest = (value: unknown): MessageLatestResult => {
  if (!isRecord(value)) {
    throw new Error('最新消息响应无效')
  }

  return {
    system: parseLatestItems(value.system, 'system'),
    approval: parseLatestItems(value.approval, 'approval'),
    alarm: parseLatestItems(value.alarm, 'alarm'),
  }
}

export const parseMessageUnreadCount = (value: unknown): MessageUnreadCountResult => {
  if (!isRecord(value)) {
    throw new Error('未读消息响应无效')
  }

  return {
    unread_count: requirePaginationNumber(value.unread_count, 'unread_count', 0),
  }
}

export const parseMessageReadAll = (value: unknown): MessageReadAllResult => {
  if (!isRecord(value)) {
    throw new Error('全部已读响应无效')
  }

  return {
    updated_count: requirePaginationNumber(value.updated_count, 'updated_count', 0),
  }
}
