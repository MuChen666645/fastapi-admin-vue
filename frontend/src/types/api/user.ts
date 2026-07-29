export interface CurrentUserResponse {
  posts: unknown[]
  user: {
    id: number
    username: string
    nickname: string | null
    email: string | null
    phone: string | null
    avatar: string | null
    status: string | number
  }
  roles: Array<{
    id: number
    name: string
    code: string
  }>
  permissions: string[]
}
