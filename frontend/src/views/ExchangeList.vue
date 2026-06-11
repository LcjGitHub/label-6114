<script setup lang="ts">
import { h, ref, computed, onMounted, watch, onActivated } from 'vue'
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
import { batchDeleteExchanges, deleteExchange, exportExchanges, fetchExchanges, fetchStatistics, importExchanges } from '@/api/exchange'
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
const importing = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const statistics = ref<Statistics>({ total_count: 0, completed_count: 0, in_progress_count: 0, recent_in_progress: [] })
const checkedRowKeys = ref<number[]>([])
const sentDateOrder = ref<'asc' | 'desc' | ''>('')

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
      sent_date_order: sentDateOrder.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (!result.items) {
      message.error('加载列表异常')
      return
    }
    exchanges.value = result.items
    total.value = result.total
    checkedRowKeys.value = []
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

function handleSorterChange(sorter: { columnKey: string | number | undefined; sorter: boolean | 'default' | { multiple: number }; order: 'ascend' | 'descend' | false } | null) {
  if (!sorter || sorter.columnKey !== 'sent_date') {
    sentDateOrder.value = ''
  } else if (sorter.order === 'ascend') {
    sentDateOrder.value = 'asc'
  } else if (sorter.order === 'descend') {
    sentDateOrder.value = 'desc'
  } else {
    sentDateOrder.value = ''
  }
  currentPage.value = 1
  loadExchanges()
}

const columns = computed<DataTableColumns<Exchange>>(() => [
  {
    type: 'selection',
    options: ['all', 'none'],
  },
  { title: '书名', key: 'book_title', ellipsis: { tooltip: true } },
  { title: '对方昵称', key: 'counterpart_nickname' },
  {
    title: '寄出日期',
    key: 'sent_date',
    sorter: true,
    sortOrder: sentDateOrder.value === 'asc' ? 'ascend' : sentDateOrder.value === 'desc' ? 'descend' : false,
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
])

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

function handleImportClick() {
  if (importing.value) return
  fileInputRef.value?.click()
}

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  importing.value = true
  try {
    const result = await importExchanges(file)
    if (result.failure_count === 0) {
      message.success(`导入成功，共导入 ${result.success_count} 条记录`)
    } else if (result.success_count === 0) {
      message.error(`导入失败，共 ${result.failure_count} 条记录失败`)
    } else {
      message.warning(`导入完成，成功 ${result.success_count} 条，失败 ${result.failure_count} 条`)
    }
    if (result.errors.length > 0) {
      console.warn('导入错误详情:', result.errors)
    }
    currentPage.value = 1
    await loadExchanges()
    loadStatistics()
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || '导入失败'
    message.error(errorMsg)
  } finally {
    importing.value = false
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
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

function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning('请先选择要删除的记录')
    return
  }
  dialog.warning({
    title: '确认批量删除',
    content: `确定删除选中的 ${checkedRowKeys.value.length} 条交换记录吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await batchDeleteExchanges(checkedRowKeys.value)
        message.success('批量删除成功')
        const deletedCount = checkedRowKeys.value.length
        if (exchanges.value.length === deletedCount && currentPage.value > 1) {
          currentPage.value -= 1
        }
        await loadExchanges()
        loadStatistics()
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
        <n-button
          v-if="checkedRowKeys.length > 0"
          type="error"
          @click="handleBatchDelete"
        >
          批量删除 ({{ checkedRowKeys.length }})
        </n-button>
      </n-space>
      <n-space>
        <n-button :loading="importing" @click="handleImportClick">
          导入记录
        </n-button>
        <n-button type="primary" :loading="exporting" @click="handleExport">
          导出记录
        </n-button>
      </n-space>
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
      remote
      :row-key="(row: Exchange) => row.id"
      v-model:checked-row-keys="checkedRowKeys"
      @update:sorter="handleSorterChange"
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
    <input
      ref="fileInputRef"
      type="file"
      accept=".csv"
      style="display: none"
      @change="handleFileChange"
    />
  </n-space>
</template>
