<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFetch } from '@vueuse/core'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NDataTable,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { deleteExchange } from '@/api/exchange'
import type { Exchange } from '@/types/exchange'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const { data, isFetching, execute } = useFetch('/api/exchanges', {
  immediate: true,
  refetch: true,
}).json<Exchange[]>()

const exchanges = computed(() => data.value ?? [])

function formatDate(value: string | null) {
  if (!value) return '-'
  return format(parseISO(value), 'yyyy-MM-dd')
}

const columns: DataTableColumns<Exchange> = [
  { title: '书名', key: 'book_title', ellipsis: { tooltip: true } },
  { title: '对方昵称', key: 'counterpart_nickname' },
  {
    title: '寄出日期',
    key: 'sent_date',
    render: (row) => formatDate(row.sent_date),
  },
  {
    title: '收到日期',
    key: 'received_date',
    render: (row) => formatDate(row.received_date),
  },
  {
    title: '状态',
    key: 'is_completed',
    render: (row) =>
      h(
        NTag,
        { type: row.is_completed ? 'success' : 'warning', size: 'small' },
        { default: () => (row.is_completed ? '已完成' : '进行中') }
      ),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/edit/${row.id}`) },
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

function handleDelete(row: Exchange) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除「${row.book_title}」的交换记录吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteExchange(row.id)
        message.success('已删除')
        await execute()
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <n-data-table
    :columns="columns"
    :data="exchanges"
    :loading="isFetching"
    :bordered="false"
    striped
  />
</template>
