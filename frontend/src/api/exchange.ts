import axios from 'axios'
import type { Exchange, ExchangeFormData, ImportResult, PaginatedResult, Statistics } from '@/types/exchange'

const api = axios.create({
  baseURL: '/api',
})

export interface ExchangeQueryParams {
  keyword?: string
  status?: 'completed' | 'in_progress' | ''
  sent_date_order?: 'asc' | 'desc' | ''
  page?: number
  page_size?: number
}

export async function fetchExchanges(params?: ExchangeQueryParams): Promise<PaginatedResult<Exchange>> {
  const { data } = await api.get<PaginatedResult<Exchange>>('/exchanges', { params })
  return data
}

export async function fetchExchange(id: number): Promise<Exchange> {
  const { data } = await api.get<Exchange>(`/exchanges/${id}`)
  return data
}

export async function createExchange(payload: ExchangeFormData): Promise<Exchange> {
  const { data } = await api.post<Exchange>('/exchanges', payload)
  return data
}

export async function updateExchange(
  id: number,
  payload: ExchangeFormData
): Promise<Exchange> {
  const { data } = await api.put<Exchange>(`/exchanges/${id}`, payload)
  return data
}

export async function deleteExchange(id: number): Promise<void> {
  await api.delete(`/exchanges/${id}`)
}

export async function batchDeleteExchanges(ids: number[]): Promise<void> {
  await api.post('/exchanges/batch-delete', { ids })
}

export async function fetchStatistics(): Promise<Statistics> {
  const { data } = await api.get<Statistics>('/statistics')
  return data
}

export async function exportExchanges(): Promise<Blob> {
  const { data } = await api.get('/exchanges/export', {
    responseType: 'blob',
  })
  return data
}

export async function importExchanges(file: File): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<ImportResult>('/exchanges/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}
