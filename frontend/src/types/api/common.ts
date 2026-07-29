export interface ApiResponse<T> {
  code: number
  error_code?: string | null
  message: string
  data: T | null
}
