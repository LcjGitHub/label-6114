<script setup lang="ts">
import { h, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NInput,
  NPagination,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { deleteLabel, fetchLabels } from '@/api/label'
import type { Label } from '@/types/label'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const isFetching = ref(false)
const labels = ref<Label[]>([])
const keyword = ref('')

async function loadLabels() {
  isFetching.value = true
  try {
    const result = await fetchLabels({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
    })
    if (!result.items) {
      message.error('加载标签列表异常')
      return
    }
    labels.value = result.items
    total.value = result.total
  } catch {
    message.error('加载标签列表失败')
  } finally {
    isFetching.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadLabels()
}

loadLabels()

function handlePageChange(page: number) {
  currentPage.value = page
  loadLabels()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadLabels()
}

const columns: DataTableColumns<Label> = [
  {
    title: '标签名称',
    key: 'name',
    ellipsis: { tooltip: true },
    render: (row) =>
      h(
        NTag,
        { size: 'small', style: { backgroundColor: row.color, borderColor: row.color, color: '#fff' } },
        { default: () => row.name }
      ),
  },
  {
    title: '颜色标识',
    key: 'color',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h('div', {
            style: {
              width: '24px',
              height: '24px',
              borderRadius: '4px',
              backgroundColor: row.color,
              border: '1px solid #e0e0e0',
            },
          }),
          row.color,
        ],
      }),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, null, {
        default: () => [
          h(
            NButton,
            { size: 'small', onClick: () => router.push(`/labels/edit/${row.id}`) },
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

function handleDelete(row: Label) {
  dialog.warning({
    title: '确认删除',
    content: `确定删除标签「${row.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteLabel(row.id)
        message.success('已删除')
        if (labels.value.length === 1 && currentPage.value > 1) {
          currentPage.value -= 1
        }
        await loadLabels()
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

<template>
  <n-space vertical :size="16" style="width: 100%">
    <n-space justify="space-between" align="center">
      <n-input
        v-model:value="keyword"
        placeholder="输入关键词搜索标签名称"
        clearable
        @update:value="handleSearch"
        @keyup.enter="handleSearch"
      />
      <n-button type="primary" @click="router.push('/labels/new')">新增标签</n-button>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="labels"
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
