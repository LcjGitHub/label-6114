import axios from 'axios'
import type { Contact, ContactFormData, PaginatedResult } from '@/types/contact'

const api = axios.create({
  baseURL: '/api',
})

export interface ContactQueryParams {
  page?: number
  page_size?: number
}

export async function fetchContacts(params?: ContactQueryParams): Promise<PaginatedResult<Contact>> {
  const { data } = await api.get<PaginatedResult<Contact>>('/contacts', { params })
  return data
}

export async function fetchContact(id: number): Promise<Contact> {
  const { data } = await api.get<Contact>(`/contacts/${id}`)
  return data
}

export async function createContact(payload: ContactFormData): Promise<Contact> {
  const { data } = await api.post<Contact>('/contacts', payload)
  return data
}

export async function updateContact(
  id: number,
  payload: ContactFormData
): Promise<Contact> {
  const { data } = await api.put<Contact>(`/contacts/${id}`, payload)
  return data
}

export async function deleteContact(id: number): Promise<void> {
  await api.delete(`/contacts/${id}`)
}
