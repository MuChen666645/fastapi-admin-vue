import type {
  MessageCreatePayload,
  MessageListFilters,
  MessageListQuery,
  MessageUpdatePayload,
  MyMessageFilters,
  MyMessageQuery,
  PaginationResult,
  RequestOptions,
  MessageDetail,
  MessageItem,
  MessageLatestResult,
  MessageListItem,
  MessageReadAllResult,
  MessageUnreadCountResult,
} from '@/types'
import { DEFAULT_DATETIME_FORMAT, getDateRange } from '@/utils'
import { requestJson } from '@/utils/request'

import {
  parseMessageDetail,
  parseMessageLatest,
  parseMessageListPage,
  parseMessageReadAll,
  parseMessageUnreadCount,
  parseMyMessageDetail,
  parseMyMessageListPage,
} from './parsers'

const appendDateRange = (query: URLSearchParams, publishTime: [number, number] | null): void => {
  if (!publishTime) {
    return
  }

  const [start, end] = publishTime
  const startRange = getDateRange(start)
  const endRange = getDateRange(end)
  if (startRange && endRange) {
    query.set('start_time', startRange.start.format(DEFAULT_DATETIME_FORMAT))
    query.set('end_time', endRange.end.format(DEFAULT_DATETIME_FORMAT))
  }
}

const createMessageListQuery = (params: MessageListQuery, filters: MessageListFilters): string => {
  const query = new URLSearchParams({
    page: String(params.page),
    size: String(params.size),
  })
  const title = filters.title.trim()
  const content = filters.content.trim()

  if (title) {
    query.set('title', title)
  }

  if (content) {
    query.set('content', content)
  }

  if (filters.message_type) {
    query.set('message_type', filters.message_type)
  }

  if (filters.status) {
    query.set('status', filters.status)
  }

  appendDateRange(query, filters.publish_time)
  return query.toString()
}

const createMyMessageQuery = (params: MyMessageQuery, filters: MyMessageFilters): string => {
  const query = new URLSearchParams({
    page: String(params.page),
    size: String(params.size),
  })
  const keyword = filters.keyword.trim()

  if (keyword) {
    query.set('keyword', keyword)
  }

  if (filters.message_type) {
    query.set('message_type', filters.message_type)
  }

  if (filters.read_status) {
    query.set('read_status', filters.read_status)
  }

  appendDateRange(query, filters.publish_time)
  return query.toString()
}

const silentRequest: Pick<RequestOptions, 'showMessage'> = { showMessage: false }

export const fetchMessageList = (
  params: MessageListQuery,
  filters: MessageListFilters,
  requestOptions: Pick<RequestOptions, 'showMessage'> = {},
): Promise<PaginationResult<MessageListItem>> =>
  requestJson(
    `/message/list?${createMessageListQuery(params, filters)}`,
    requestOptions,
    parseMessageListPage,
  )

export const fetchMessageDetail = (messageId: number): Promise<MessageDetail> =>
  requestJson(`/message/${messageId}`, {}, parseMessageDetail)

export const createMessage = (payload: MessageCreatePayload): Promise<MessageDetail> =>
  requestJson('/message/add', { method: 'POST', data: payload }, parseMessageDetail)

export const updateMessage = (messageId: number, payload: MessageUpdatePayload): Promise<null> =>
  requestJson(`/message/${messageId}`, { method: 'PUT', data: payload }, () => null)

export const deleteMessage = (messageId: number): Promise<null> =>
  requestJson(`/message/${messageId}`, { method: 'DELETE' }, () => null)

export const fetchLatestMessages = (): Promise<MessageLatestResult> =>
  requestJson('/message/latest', silentRequest, parseMessageLatest)

export const fetchUnreadMessageCount = (): Promise<MessageUnreadCountResult> =>
  requestJson('/message/unread-count', silentRequest, parseMessageUnreadCount)

export const fetchMyMessageList = (
  params: MyMessageQuery,
  filters: MyMessageFilters,
): Promise<PaginationResult<MessageItem>> =>
  requestJson(
    `/message/my/list?${createMyMessageQuery(params, filters)}`,
    {},
    parseMyMessageListPage,
  )

export const fetchMyMessageDetail = (messageId: number): Promise<MessageItem> =>
  requestJson(`/message/my/${messageId}`, {}, parseMyMessageDetail)

export const markMessageRead = (messageId: number): Promise<null> =>
  requestJson(`/message/${messageId}/read`, { method: 'POST', ...silentRequest }, () => null)

export const markAllMessagesRead = (): Promise<MessageReadAllResult> =>
  requestJson('/message/read-all', { method: 'POST', ...silentRequest }, parseMessageReadAll)
