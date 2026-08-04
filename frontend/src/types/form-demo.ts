export type FormDemoPriority = 'normal' | 'urgent'
export type FormDemoReviewerRole = 'owner' | 'reviewer' | 'observer'

export interface FormDemoReviewer {
  [key: string]: unknown
  id: string
  name: string
  role: FormDemoReviewerRole
  email: string
}

export interface FormDemoModel {
  [key: string]: unknown
  projectName: string
  owner: string
  email: string
  priority: FormDemoPriority
  dueDate: number | null
  active: boolean
  remarks: string
  reviewers: FormDemoReviewer[]
}
