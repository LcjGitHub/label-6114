<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NSpace,
  NTag,
  useMessage,
} from 'naive-ui'
import { fetchExchange } from '@/api/exchange'
import type { Exchange } from '@/types/exchange'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const loading = ref(false)
const exchange = ref<Exchange | null>(null)

function formatDate(value: string | null) {
  if (!value) return '-'
  return format(parseISO(value), 'yyyy-MM-dd')
}

const statusTag = computed(() => {
  const data = exchange.value
  if (!data) return null
  return h(
    NTag,
    { type: data.is_completed ? 'success' : 'warning', size: 'small' },
    { default: () => (data.is_completed ? '已完成' : '进行中') }
  )
})

async function loadExchange() {
  const id = route.params.id as string
  if (!id) return
  loading.value = true
  try {
    exchange.value = await fetchExchange(Number(id))
  } catch {
    message.error('加载记录失败')
    router.push('/list')
  } finally {
    loading.value = false
  }
}

onMounted(loadExchange)
</script>

<template>
  <n-card title="交换记录详情" :loading="loading">
    <n-descriptions v-if="exchange" :column="1" label-placement="left" label-style="width: 96px">
      <n-descriptions-item label="书名">
        {{ exchange.book_title }}
      </n-descriptions-item>
      <n-descriptions-item label="对方昵称">
        {{ exchange.counterpart_nickname }}
      </n-descriptions-item>
      <n-descriptions-item label="寄出日期">
        {{ formatDate(exchange.sent_date) }}
      </n-descriptions-item>
      <n-descriptions-item label="收到日期">
        {{ formatDate(exchange.received_date) }}
      </n-descriptions-item>
      <n-descriptions-item label="完成状态">
        <component :is="statusTag" />
      </n-descriptions-item>
      <n-descriptions-item label="备注">
        {{ exchange.notes ?? '-' }}
      </n-descriptions-item>
    </n-descriptions>
    <template #footer>
      <n-space>
        <n-button type="primary" @click="router.push(`/edit/${exchange?.id}`)">
          编辑
        </n-button>
        <n-button @click="router.push('/list')">返回列表</n-button>
      </n-space>
    </template>
  </n-card>
</template>
