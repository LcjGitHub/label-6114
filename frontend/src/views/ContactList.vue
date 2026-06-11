<script setup lang="ts">
import { h, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useFetch } from '@vueuse/core'
import {
  NButton,
  NDataTable,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { deleteContact } from '@/api/contact'
import type { Contact } from '@/types/contact'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const { data, isFetching, error, execute } = useFetch('/api/contacts', {
  immediate: true,
  refetch: true,
}).json<Contact[]>()

watch(error, (err) => {
  if (err) {
    message.error('加载联系人列表失败')
  }
})

const contacts = computed(() => data.value ?? [])

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
    :data="contacts"
    :loading="isFetching"
    :bordered="false"
    striped
  />
</template>
