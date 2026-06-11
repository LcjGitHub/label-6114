export interface PaginatedResult<T> {
  items: T[]
  total: number
}

export interface Label {
  id: number
  name: string
  color: string
}

export interface LabelFormData {
  name: string
  color: string
}
