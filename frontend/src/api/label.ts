import axios from 'axios'
import type { Label, LabelFormData, PaginatedResult } from '@/types/label'

const api = axios.create({
  baseURL: '/api',
})

export interface LabelQueryParams {
  page?: number
  page_size?: number
  keyword?: string
}

export async function fetchLabels(params?: LabelQueryParams): Promise<PaginatedResult<Label>> {
  const { data } = await api.get<PaginatedResult<Label>>('/labels', { params })
  return data
}

export async function fetchAllLabels(): Promise<Label[]> {
  const { data } = await api.get<Label[]>('/labels/all')
  return data
}

export async function fetchLabel(id: number): Promise<Label> {
  const { data } = await api.get<Label>(`/labels/${id}`)
  return data
}

export async function createLabel(payload: LabelFormData): Promise<Label> {
  const { data } = await api.post<Label>('/labels', payload)
  return data
}

export async function updateLabel(id: number, payload: LabelFormData): Promise<Label> {
  const { data } = await api.put<Label>(`/labels/${id}`, payload)
  return data
}

export async function deleteLabel(id: number): Promise<void> {
  await api.delete(`/labels/${id}`)
}
