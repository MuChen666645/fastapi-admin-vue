import type { RequestMessageHandler } from '@/types'

let requestMessageHandler: RequestMessageHandler | null = null

export const configureRequestMessage = (handler: RequestMessageHandler | null): void => {
  requestMessageHandler = handler
}

export const showRequestMessage = (message: string): void => {
  requestMessageHandler?.(message)
}
