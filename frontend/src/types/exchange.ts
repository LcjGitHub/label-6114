export interface Exchange {
  id: number
  book_title: string
  counterpart_nickname: string
  sent_date: string | null
  received_date: string | null
  is_completed: boolean
}

export interface ExchangeFormData {
  book_title: string
  counterpart_nickname: string
  sent_date: string | null
  received_date: string | null
  is_completed: boolean
}
