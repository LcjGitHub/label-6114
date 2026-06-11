<script setup lang="ts">
import { h, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NDataTable,
  NSpace,
  NTag,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { fetchOverdueExchanges } from '@/api/exchange'
import type { OverdueExchange } from '@/types/exchange'

const router = useRouter()
const message = useMessage()

const overdueList = ref<OverdueExchange[]>([])
const isFetching = ref(false)

async function loadOverdueList() {
  isFetching.value = true
  try {
    const result = await fetchOverdueExchanges()
    overdueList.value = result
  } catch {
    message.error('加载逾期提醒列表失败')
  } finally {
    isFetching.value = false
  }
}

onMounted(() => {
  loadOverdueList()
})

function formatDate(value: string | null) {
  if (!value) return '-'
  return format(parseISO(value), 'yyyy-MM-dd')
}

const columns = computed<DataTableColumns<OverdueExchange>>(() => [
  { title: '书名', key: 'book_title', ellipsis: { tooltip: true } },
  { title: '对方昵称', key: 'counterpart_nickname' },
  {
    title: '寄出日期',
    key: 'sent_date',
    render: (row) => formatDate(row.sent_date),
  },
  {
    title: '逾期天数',
    key: 'overdue_days',
    render: (row) =>
      h(
        NTag,
        { type: row.overdue_days >= 30 ? 'error' : 'warning', size: 'small' },
        { default: () => `逾期 ${row.overdue_days} 天` }
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
            { size: 'small', onClick: () => router.push(`/detail/${row.id}`) },
            { default: () => '查看' }
          ),
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/edit/${row.id}`) },
            { default: () => '编辑' }
          ),
        ],
      }),
  },
])
</script>

<template>
  <n-space vertical :size="16" style="width: 100%">
    <n-space justify="space-between" align="center">
      <n-space align="center">
        <h2 style="margin: 0; font-size: 20px">逾期提醒</h2>
        <n-tag :bordered="false" type="error" size="medium">
          共 {{ overdueList.length }} 条逾期记录
        </n-tag>
      </n-space>
      <n-space>
        <n-button @click="loadOverdueList">刷新</n-button>
      </n-space>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="overdueList"
      :loading="isFetching"
      :bordered="false"
      striped
      :row-key="(row: OverdueExchange) => row.id"
    />
  </n-space>
</template>
