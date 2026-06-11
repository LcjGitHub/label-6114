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

export interface Statistics {
  total_count: number
  completed_count: number
  in_progress_count: number
}
