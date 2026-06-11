import axios from 'axios'
import type { Exchange, ExchangeFormData, Statistics } from '@/types/exchange'

const api = axios.create({
  baseURL: '/api',
})

export interface ExchangeQueryParams {
  keyword?: string
  status?: 'completed' | 'in_progress' | ''
}

export async function fetchExchanges(params?: ExchangeQueryParams): Promise<Exchange[]> {
  const { data } = await api.get<Exchange[]>('/exchanges', { params })
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
