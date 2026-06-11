<script setup lang="ts">
import { h, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NPagination,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { deleteContact, fetchContacts } from '@/api/contact'
import type { Contact } from '@/types/contact'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const isFetching = ref(false)
const contacts = ref<Contact[]>([])

async function loadContacts() {
  isFetching.value = true
  try {
    const result = await fetchContacts({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    contacts.value = result.items
    total.value = result.total
  } catch {
    message.error('加载联系人列表失败')
  } finally {
    isFetching.value = false
  }
}

loadContacts()

function handlePageChange(page: number) {
  currentPage.value = page
  loadContacts()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadContacts()
}

const columns: DataTableColumns<Contact> = [
  { title: '昵称', key: 'nickname', ellipsis: { tooltip: true } },
  { title: '联系方式', key: 'contact_info', ellipsis: { tooltip: true } },
  {
    title: '备注说明',
    key: 'notes',
    render: (row) => row.notes ?? h(NTag, { size: 'small', type: 'default' }, { default: () => '无' }),
    ellipsis: { tooltip: true },
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/contacts/edit/${row.id}`) },
            { default: () => '编辑' }
          ),
          h(
            NButton,
            { size: 'small', type: 'error', onClick: () => handleDelete(row) },
            { default: () => '删除' }
          ),
        ],
      }),
  },
]

function handleDelete(row: Contact) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除联系人「${row.nickname}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteContact(row.id)
        message.success('已删除')
        await loadContacts()
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <n-space vertical :size="16" style="width: 100%">
    <n-data-table
      :columns="columns"
      :data="contacts"
      :loading="isFetching"
      :bordered="false"
      striped
    />
    <n-pagination
      :page="currentPage"
      :page-size="pageSize"
      :item-count="total"
      :page-sizes="[10, 20, 50]"
      show-size-picker
      @update:page="handlePageChange"
      @update:page-size="handlePageSizeChange"
    />
  </n-space>
</template>
