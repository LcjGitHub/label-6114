export interface PaginatedResult<T> {
  items: T[]
  total: number
}

export interface Exchange {
  id: number
  book_title: string
  counterpart_nickname: string
  sent_date: string | null
  received_date: string | null
  is_completed: boolean
  notes: string | null
}

export interface ExchangeFormData {
  book_title: string
  counterpart_nickname: string
  sent_date: string | null
  received_date: string | null
  is_completed: boolean
  notes: string | null
}

export interface RecentExchange {
  id: number
  book_title: string
  counterpart_nickname: string
}

export interface Statistics {
  total_count: number
  completed_count: number
  in_progress_count: number
  recent_in_progress: RecentExchange[]
}

export interface MonthlyStatsItem {
  month: string
  total_count: number
  completed_count: number
}

export interface MonthlyStats {
  items: MonthlyStatsItem[]
}

export interface ImportResult {
  success_count: number
  failure_count: number
  errors: string[]
}

export interface OverdueExchange {
  id: number
  book_title: string
  counterpart_nickname: string
  sent_date: string | null
  overdue_days: number
}
