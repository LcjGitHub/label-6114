<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useBreakpoints } from '@vueuse/core'
import { NCard, NGrid, NGridItem, NStatistic, NSpace, NSpin, NDataTable, useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { fetchStatistics } from '@/api/exchange'
import type { Statistics, RecentExchange } from '@/types/exchange'

const breakpoints = useBreakpoints({
  xs: 0,
  sm: 640,
  md: 960,
})

const message = useMessage()
const router = useRouter()

const statistics = ref<Statistics | null>(null)
const loading = ref(true)

const gridCols = computed(() => {
  if (breakpoints.smaller('sm').value) return 1
  if (breakpoints.smaller('md').value) return 2
  return 3
})

const totalCount = computed(() => statistics.value?.total_count ?? 0)
const completedCount = computed(() => statistics.value?.completed_count ?? 0)
const inProgressCount = computed(() => statistics.value?.in_progress_count ?? 0)

const completedPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const recentInProgress = computed<RecentExchange[]>(() => statistics.value?.recent_in_progress ?? [])

const recentColumns = [
  { title: '编号', key: 'id', width: 70 },
  { title: '书名', key: 'book_title' },
  { title: '对方昵称', key: 'counterpart_nickname' },
]

function handleRowClick(row: RecentExchange) {
  router.push({ name: 'detail', params: { id: row.id } })
}

onMounted(async () => {
  try {
    statistics.value = await fetchStatistics()
  } catch {
    message.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <n-space vertical size="large">
    <h2 style="margin: 0; font-size: 22px">数据概览</h2>
    <n-spin :show="loading">
      <n-grid :cols="gridCols" :x-gap="16" :y-gap="16">
        <n-grid-item>
          <n-card hoverable>
            <n-statistic label="总记录数" :value="totalCount">
              <template #prefix>
                <span style="color: #2080f0; font-size: 20px">📚</span>
              </template>
            </n-statistic>
            <div style="margin-top: 12px; color: #999; font-size: 13px">
              累计创建的交换记录总数
            </div>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card hoverable>
            <n-statistic label="已完成" :value="completedCount" value-style="color: #18a058">
              <template #prefix>
                <span style="color: #18a058; font-size: 20px">✅</span>
              </template>
            </n-statistic>
            <div style="margin-top: 12px; color: #999; font-size: 13px">
              已完成的交换记录（占 {{ completedPercent }}%）
            </div>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card hoverable>
            <n-statistic label="进行中" :value="inProgressCount" value-style="color: #f0a020">
              <template #prefix>
                <span style="color: #f0a020; font-size: 20px">⏳</span>
              </template>
            </n-statistic>
            <div style="margin-top: 12px; color: #999; font-size: 13px">
              正在进行中的交换记录数
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
      <n-card title="最近进行中记录" style="margin-top: 16px" v-if="recentInProgress.length > 0">
        <n-data-table
          :columns="recentColumns"
          :data="recentInProgress"
          :bordered="false"
          size="small"
          :row-props="(row: RecentExchange) => ({ style: 'cursor: pointer;', onClick: () => handleRowClick(row) })"
        />
      </n-card>
    </n-spin>
  </n-space>
</template>
