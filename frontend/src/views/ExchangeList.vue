<script setup lang="ts">
import { h, ref, onMounted, watch, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NDataTable,
  NInput,
  NPagination,
  NSelect,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
  type SelectOption,
} from 'naive-ui'
import { deleteExchange, exportExchanges, fetchExchanges, fetchStatistics } from '@/api/exchange'
import type { Exchange } from '@/types/exchange'
import type { Statistics } from '@/types/exchange'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const keyword = ref('')
const status = ref<'completed' | 'in_progress' | ''>('')
const exchanges = ref<Exchange[]>([])
const isFetching = ref(false)
const exporting = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const statistics = ref<Statistics>({ total_count: 0, completed_count: 0, in_progress_count: 0 })

const statusOptions: SelectOption[] = [
  { label: '全部状态', value: '' },
  { label: '已完成', value: 'completed' },
  { label: '进行中', value: 'in_progress' },
]

async function loadExchanges() {
  isFetching.value = true
  try {
    const result = await fetchExchanges({
      keyword: keyword.value || undefined,
      status: status.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (!result.items) {
      message.error('加载列表异常')
      return
    }
    exchanges.value = result.items
    total.value = result.total
  } catch {
    message.error('加载列表失败')
  } finally {
    isFetching.value = false
  }
}

function handleStatusChange() {
  currentPage.value = 1
  loadExchanges()
}

let searchTimer: ReturnType<typeof setTimeout> | null = null

watch(keyword, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadExchanges()
  }, 300)
})

function handlePageChange(page: number) {
  currentPage.value = page
  loadExchanges()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadExchanges()
}

async function loadStatistics() {
  try {
    statistics.value = await fetchStatistics()
  } catch {
    message.error('加载统计数据失败')
  }
}

onMounted(() => {
  loadExchanges()
  loadStatistics()
})

onActivated(() => {
  loadStatistics()
})

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
    title: '备注',
    key: 'notes',
    width: 200,
    ellipsis: { tooltip: true },
    render: (row) => row.notes ?? '-',
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/detail/${row.id}`) },
            { default: () => '查看' }
          ),
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

async function handleExport() {
  if (exporting.value) return
  exporting.value = true
  try {
    const blob = await exportExchanges()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '交换记录.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch {
    message.error('导出失败')
  } finally {
    exporting.value = false
  }
}

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
        if (exchanges.value.length === 1 && currentPage.value > 1) {
          currentPage.value -= 1
        }
        await loadExchanges()
        loadStatistics()
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <n-space vertical :size="16" style="width: 100%">
    <n-space justify="space-between">
      <n-space>
        <n-input
          v-model:value="keyword"
          placeholder="搜索书名或对方昵称"
          clearable
          style="width: 280px"
        />
        <n-select
          v-model:value="status"
          :options="statusOptions"
          style="width: 160px"
          @update:value="handleStatusChange"
        />
      </n-space>
      <n-button type="primary" :loading="exporting" @click="handleExport">
        导出记录
      </n-button>
    </n-space>
    <n-space :size="24" align="center">
      <n-tag :bordered="false" type="info" size="medium">
        总记录 {{ statistics.total_count }}
      </n-tag>
      <n-tag :bordered="false" type="success" size="medium">
        已完成 {{ statistics.completed_count }}
      </n-tag>
      <n-tag :bordered="false" type="warning" size="medium">
        进行中 {{ statistics.in_progress_count }}
      </n-tag>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="exchanges"
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
