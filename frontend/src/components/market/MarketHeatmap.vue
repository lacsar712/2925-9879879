<template>
  <div class="market-heatmap">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-4">
        <a-radio-group v-model:value="metricType" button-style="solid" size="large">
          <a-radio-button value="change">
            <template #icon><RiseOutlined /></template>
            涨跌幅
          </a-radio-button>
          <a-radio-button value="volume">
            <template #icon><BarChartOutlined /></template>
            成交量
          </a-radio-button>
        </a-radio-group>
        <a-tag color="blue" class="text-sm">
          点击色块查看详情
        </a-tag>
      </div>
      <a-button @click="handleRefresh" :loading="loading">
        <template #icon><ReloadOutlined /></template>
        刷新
      </a-button>
    </div>

    <a-spin :spinning="loading" tip="加载中...">
      <div v-if="heatmapData.length > 0" class="heatmap-container">
        <v-chart
          :option="chartOption"
          :autoresize="true"
          class="heatmap-chart"
          @click="handleChartClick"
        />
      </div>
      <a-empty v-else description="暂无热力图数据" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RiseOutlined, BarChartOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  VisualMapComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'
import VChart from 'vue-echarts'
import api from '../../api'
import { formatVolume } from '../../utils/format'
import { useTheme } from '../../composables/useTheme'
import { message } from 'ant-design-vue'

use([
  CanvasRenderer,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  VisualMapComponent,
])

const emit = defineEmits<{
  (e: 'cell-click', data: HeatmapCell): void
}>()

const router = useRouter()
const { getChartColors } = useTheme()

type MetricType = 'change' | 'volume'

interface HeatmapCell {
  bond_type: string
  term_bucket: string
  avg_change: number
  total_volume: number
  trade_count: number
}

interface HeatmapResponse {
  term_buckets: string[]
  bond_types: string[]
  data: HeatmapCell[]
}

const loading = ref(false)
const metricType = ref<MetricType>('change')
const termBuckets = ref<string[]>([])
const bondTypes = ref<string[]>([])
const heatmapData = ref<HeatmapCell[]>([])

const chartColors = computed(() => getChartColors())

const chartOption = computed<EChartsOption>(() => {
  const xData = termBuckets.value
  const yData = bondTypes.value
  const data = heatmapData.value

  if (xData.length === 0 || yData.length === 0 || data.length === 0) {
    return {}
  }

  const isChange = metricType.value === 'change'

  const seriesData: number[][] = []
  let minVal = Infinity
  let maxVal = -Infinity

  data.forEach((cell) => {
    const xIndex = xData.indexOf(cell.term_bucket)
    const yIndex = yData.indexOf(cell.bond_type)
    if (xIndex >= 0 && yIndex >= 0) {
      const value = isChange ? cell.avg_change : cell.total_volume
      seriesData.push([xIndex, yIndex, value])
      if (value < minVal) minVal = value
      if (value > maxVal) maxVal = value
    }
  })

  if (minVal === Infinity) {
    minVal = 0
    maxVal = 100
  }

  const visualMap: EChartsOption['visualMap'] = isChange
    ? {
        min: minVal,
        max: maxVal,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        inRange: {
          color: ['#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4'],
        },
        text: ['高', '低'],
        textStyle: {
          color: chartColors.value.axis,
        },
      }
    : {
        min: minVal,
        max: maxVal,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        inRange: {
          color: ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
        },
        text: ['高', '低'],
        textStyle: {
          color: chartColors.value.axis,
        },
      }

  return {
    tooltip: {
      position: 'top',
      backgroundColor: chartColors.value.tooltipBg,
      textStyle: { color: chartColors.value.tooltipText },
      formatter: (params: any) => {
        const cell = data.find(
          (c) =>
            c.term_bucket === xData[params.data[0]] &&
            c.bond_type === yData[params.data[1]]
        )
        if (!cell) return ''
        const changeStr = cell.avg_change >= 0 ? `+${cell.avg_change.toFixed(4)}%` : `${cell.avg_change.toFixed(4)}%`
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${cell.bond_type} - ${cell.term_bucket}</div>
            <div>平均涨跌幅: <span style="color: ${cell.avg_change >= 0 ? '#ff4d4f' : '#52c41a'}">${changeStr}</span></div>
            <div>成交量: ${formatVolume(cell.total_volume)}</div>
            <div>成交笔数: ${cell.trade_count}</div>
          </div>
        `
      },
    },
    grid: {
      left: '12%',
      right: '5%',
      top: '5%',
      bottom: '15%',
    },
    xAxis: {
      type: 'category',
      data: xData,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: chartColors.value.axis,
        fontSize: 12,
      },
      axisLine: { lineStyle: { color: chartColors.value.grid } },
      splitLine: { lineStyle: { color: chartColors.value.grid } },
    },
    yAxis: {
      type: 'category',
      data: yData,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: chartColors.value.axis,
        fontSize: 12,
      },
      axisLine: { lineStyle: { color: chartColors.value.grid } },
      splitLine: { lineStyle: { color: chartColors.value.grid } },
    },
    visualMap,
    series: [
      {
        name: isChange ? '平均涨跌幅' : '成交量',
        type: 'heatmap',
        data: seriesData,
        label: {
          show: true,
          formatter: (params: any) => {
            const value = params.data[2]
            if (isChange) {
              return value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`
            }
            if (value >= 10000) return `${(value / 10000).toFixed(1)}亿`
            if (value >= 1000) return `${(value / 1000).toFixed(1)}万`
            return value.toFixed(0)
          },
          color: '#333',
          fontSize: 11,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
})

async function fetchHeatmapData() {
  loading.value = true
  try {
    const res = await api.get<HeatmapResponse>('/api/dashboard/heatmap')
    const data = res.data
    termBuckets.value = data.term_buckets || []
    bondTypes.value = data.bond_types || []
    heatmapData.value = data.data || []
  } catch (e) {
    message.error('获取热力图数据失败')
    heatmapData.value = []
  } finally {
    loading.value = false
  }
}

function handleRefresh() {
  fetchHeatmapData()
}

function handleChartClick(params: any) {
  const xData = termBuckets.value
  const yData = bondTypes.value
  const cell = heatmapData.value.find(
    (c) =>
      c.term_bucket === xData[params.data[0]] &&
      c.bond_type === yData[params.data[1]]
  )
  if (cell) {
    emit('cell-click', cell)
    router.push({
      path: '/market',
      query: {
        bond_type: cell.bond_type,
        term_bucket: cell.term_bucket,
      },
    })
  }
}

onMounted(() => {
  fetchHeatmapData()
})
</script>

<style scoped>
.market-heatmap {
  width: 100%;
}

.heatmap-container {
  width: 100%;
  min-height: 500px;
}

.heatmap-chart {
  width: 100%;
  height: 500px;
}
</style>
