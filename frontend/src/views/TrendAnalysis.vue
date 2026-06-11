<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { NCard, NSpin, NSpace, useMessage, NRadioGroup, NRadioButton, NStatistic } from 'naive-ui'
import * as echarts from 'echarts'
import { fetchMonthlyStatistics } from '@/api/exchange'
import type { MonthlyStatsItem } from '@/types/exchange'

const message = useMessage()

const loading = ref(true)
const chartType = ref<'line' | 'bar'>('line')
const monthlyData = ref<MonthlyStatsItem[]>([])

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const totalCount = computed(() => {
  return monthlyData.value.reduce((sum, item) => sum + item.total_count, 0)
})

const completedCount = computed(() => {
  return monthlyData.value.reduce((sum, item) => sum + item.completed_count, 0)
})

const completionRate = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

function initChart() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chartInstance) return

  const months = monthlyData.value.map((item) => item.month)
  const totalCounts = monthlyData.value.map((item) => item.total_count)
  const completedCounts = monthlyData.value.map((item) => item.completed_count)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
    },
    legend: {
      data: ['交换总数', '已完成数'],
      top: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: chartType.value === 'bar',
      data: months,
      axisLabel: {
        rotate: 30,
        fontSize: 12,
      },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
    },
    series: [
      {
        name: '交换总数',
        type: chartType.value,
        data: totalCounts,
        smooth: true,
        itemStyle: {
          color: '#2080f0',
        },
        areaStyle: chartType.value === 'line'
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(32, 128, 240, 0.3)' },
                { offset: 1, color: 'rgba(32, 128, 240, 0.05)' },
              ]),
            }
          : undefined,
        barWidth: chartType.value === 'bar' ? '30%' : undefined,
      },
      {
        name: '已完成数',
        type: chartType.value,
        data: completedCounts,
        smooth: true,
        itemStyle: {
          color: '#18a058',
        },
        areaStyle: chartType.value === 'line'
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(24, 160, 88, 0.3)' },
                { offset: 1, color: 'rgba(24, 160, 88, 0.05)' },
              ]),
            }
          : undefined,
        barWidth: chartType.value === 'bar' ? '30%' : undefined,
      },
    ],
  }

  chartInstance.setOption(option, true)
}

function handleResize() {
  chartInstance?.resize()
}

watch(chartType, () => {
  updateChart()
})

onMounted(async () => {
  try {
    const data = await fetchMonthlyStatistics()
    monthlyData.value = data.items
  } catch {
    message.error('加载月度统计数据失败')
  } finally {
    loading.value = false
  }
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<template>
  <n-space vertical size="large">
    <h2 style="margin: 0; font-size: 22px">趋势分析</h2>

    <n-spin :show="loading">
      <n-card>
        <n-space justify="space-between" align="center" style="margin-bottom: 16px">
          <div style="font-size: 16px; font-weight: 500">近十二月交换趋势</div>
          <n-radio-group v-model:value="chartType" size="small">
            <n-radio-button value="line">折线图</n-radio-button>
            <n-radio-button value="bar">柱状图</n-radio-button>
          </n-radio-group>
        </n-space>
        <div ref="chartRef" style="width: 100%; height: 400px"></div>
      </n-card>

      <n-card title="周期汇总" style="margin-top: 16px">
        <n-space :size="24" wrap>
          <n-statistic label="近十二月交换总数" :value="totalCount">
            <template #prefix>
              <span style="color: #2080f0; font-size: 18px">📚</span>
            </template>
          </n-statistic>
          <n-statistic label="近十二月已完成数" :value="completedCount" value-style="color: #18a058">
            <template #prefix>
              <span style="color: #18a058; font-size: 18px">✅</span>
            </template>
          </n-statistic>
          <n-statistic label="整体完成率" :value="completionRate" suffix="%">
            <template #prefix>
              <span style="color: #f0a020; font-size: 18px">📊</span>
            </template>
          </n-statistic>
        </n-space>
      </n-card>
    </n-spin>
  </n-space>
</template>
