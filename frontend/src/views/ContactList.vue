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
import { batchDeleteContacts, deleteContact, fetchContacts } from '@/api/contact'
import type { Contact } from '@/types/contact'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const isFetching = ref(false)
const contacts = ref<Contact[]>([])
const checkedRowKeys = ref<number[]>([])

async function loadContacts() {
  isFetching.value = true
  try {
    const result = await fetchContacts({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (!result.items) {
      message.error('加载联系人列表异常')
      return
    }
    contacts.value = result.items
    total.value = result.total
    checkedRowKeys.value = []
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
  {
    type: 'selection',
    options: ['all', 'none'],
  },
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
        if (contacts.value.length === 1 && currentPage.value > 1) {
          currentPage.value -= 1
        }
        await loadContacts()
      } catch {
        message.error('删除失败')
      }
    },
  })
}

function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning('请先选择要删除的联系人')
    return
  }
  dialog.warning({
    title: '确认批量删除',
    content: `确定删除选中的 ${checkedRowKeys.value.length} 位联系人吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await batchDeleteContacts(checkedRowKeys.value)
        message.success('批量删除成功')
        const deletedCount = checkedRowKeys.value.length
        if (contacts.value.length === deletedCount && currentPage.value > 1) {
          currentPage.value -= 1
        }
        await loadContacts()
      } catch {
        message.error('批量删除失败')
      }
    },
  })
}
</script>

<template>
  <n-space vertical :size="16" style="width: 100%">
    <n-space justify="space-between">
      <n-space>
        <n-button
          v-if="checkedRowKeys.length > 0"
          type="error"
          @click="handleBatchDelete"
        >
          批量删除 ({{ checkedRowKeys.length }})
        </n-button>
      </n-space>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="contacts"
      :loading="isFetching"
      :bordered="false"
      striped
      :row-key="(row: Contact) => row.id"
      v-model:checked-row-keys="checkedRowKeys"
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
