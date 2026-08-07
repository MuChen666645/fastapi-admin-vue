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
  RequestParameters,
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

const getDateRangeParameters = (publishTime: [number, number] | null): RequestParameters => {
  if (!publishTime) {
    return {}
  }

  const [start, end] = publishTime
  const startRange = getDateRange(start)
  const endRange = getDateRange(end)
  if (startRange && endRange) {
    return {
      start_time: startRange.start.format(DEFAULT_DATETIME_FORMAT),
      end_time: endRange.end.format(DEFAULT_DATETIME_FORMAT),
    }
  }

  return {}
}

const createMessageListParameters = (
  params: MessageListQuery,
  filters: MessageListFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  const title = filters.title.trim()
  const content = filters.content.trim()

  if (title) {
    parameters.title = title
  }

  if (content) {
    parameters.content = content
  }

  if (filters.message_type) {
    parameters.message_type = filters.message_type
  }

  if (filters.status) {
    parameters.status = filters.status
  }

  return { ...parameters, ...getDateRangeParameters(filters.publish_time) }
}

const createMyMessageParameters = (
  params: MyMessageQuery,
  filters: MyMessageFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  const keyword = filters.keyword.trim()

  if (keyword) {
    parameters.keyword = keyword
  }

  if (filters.message_type) {
    parameters.message_type = filters.message_type
  }

  if (filters.read_status) {
    parameters.read_status = filters.read_status
  }

  return { ...parameters, ...getDateRangeParameters(filters.publish_time) }
}

const silentRequest: Pick<RequestOptions, 'showMessage'> = { showMessage: false }

export const fetchMessageList = (
  params: MessageListQuery,
  filters: MessageListFilters,
  requestOptions: Pick<RequestOptions, 'showMessage'> = {},
): Promise<PaginationResult<MessageListItem>> =>
  requestJson(
    '/message/list',
    { ...requestOptions, params: createMessageListParameters(params, filters) },
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
    '/message/my/list',
    { params: createMyMessageParameters(params, filters) },
    parseMyMessageListPage,
  )

export const fetchMyMessageDetail = (messageId: number): Promise<MessageItem> =>
  requestJson(`/message/my/${messageId}`, {}, parseMyMessageDetail)

export const markMessageRead = (messageId: number): Promise<null> =>
  requestJson(`/message/${messageId}/read`, { method: 'POST', ...silentRequest }, () => null)

export const markAllMessagesRead = (): Promise<MessageReadAllResult> =>
  requestJson('/message/read-all', { method: 'POST', ...silentRequest }, parseMessageReadAll)
