export interface PaginatedResult<T> {
  items: T[]
  total: number
}

export interface Contact {
  id: number
  nickname: string
  contact_info: string
  notes: string | null
}

export interface ContactFormData {
  nickname: string
  contact_info: string
  notes: string | null
}
