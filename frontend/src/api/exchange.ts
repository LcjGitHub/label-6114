import axios from 'axios'
import type { Exchange, ExchangeFormData } from '@/types/exchange'

const api = axios.create({
  baseURL: '/api',
})

export async function fetchExchanges(): Promise<Exchange[]> {
  const { data } = await api.get<Exchange[]>('/exchanges')
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
