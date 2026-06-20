<template>
  <div class="broker-quote-board">
    <div class="board-header flex items-center justify-between mb-3">
      <div class="flex items-center gap-3">
        <h3 class="text-lg font-semibold text-gray-800">经纪商报价板</h3>
        <a-tag color="blue" v-if="autoRefresh">
          <template #icon>
            <ReloadOutlined :class="{ 'animate-spin': loading }" />
          </template>
          自动刷新
        </a-tag>
      </div>
      <div class="flex items-center gap-2">
        <a-select
          v-model:value="sourceType"
          style="width: 140px"
          size="small"
          :options="sourceTypeOptions"
          @change="handleSourceTypeChange"
        />
        <a-select
          v-model:value="refreshInterval"
          style="width: 120px"
          size="small"
          :options="refreshOptions"
          @change="handleRefreshChange"
        />
        <a-button size="small" @click="refresh" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
      </div>
    </div>

    <div class="board-container">
      <a-spin :spinning="loading" tip="加载中...">
        <div class="quote-grid" v-if="matrixData && matrixData.sources.length > 0">
          <div class="grid-header">
            <div class="corner-cell">
              <div class="bond-info">
                <span class="bond-code">代码/简称</span>
              </div>
            </div>
            <div
              v-for="source in matrixData.sources"
              :key="source.source_id"
              class="source-cell"
              :title="source.name"
            >
              <span class="source-name">{{ source.name }}</span>
            </div>
          </div>

          <div class="grid-body">
            <div
              v-for="row in matrixData.matrix"
              :key="row.bond.bond_id"
              class="grid-row"
            >
              <div class="bond-cell" @click="goToDetail(row.bond.bond_id)">
                <div class="bond-code">{{ row.bond.code }}</div>
                <div class="bond-name" :title="row.bond.name">{{ row.bond.name }}</div>
                <div class="bond-meta">
                  <a-tag :color="bondTypeColor(row.bond.bond_type)" size="small">
                    {{ row.bond.bond_type }}
                  </a-tag>
                </div>
              </div>

              <div
                v-for="source in matrixData.sources"
                :key="source.source_id"
                class="quote-cell"
                :class="{
                  'has-quote': row.quotes[source.source_id],
                  'no-quote': !row.quotes[source.source_id],
                  'clickable': row.quotes[source.source_id],
                }"
                @click="handleQuoteClick(row.bond.bond_id, row.quotes[source.source_id])"
              >
                <template v-if="row.quotes[source.source_id]">
                  <div class="quote-row bid-row">
                    <span class="quote-label">买</span>
                    <span class="quote-price bid-price tabular-nums">
                      {{ formatPrice(row.quotes[source.source_id].bid_price) }}
                    </span>
                  </div>
                  <div class="quote-row ask-row">
                    <span class="quote-label">卖</span>
                    <span class="quote-price ask-price tabular-nums">
                      {{ formatPrice(row.quotes[source.source_id].ask_price) }}
                    </span>
                  </div>
                  <div class="quote-time tabular-nums">
                    {{ formatTimeAgo(row.quotes[source.source_id].quote_time) }}
                  </div>
                </template>
                <template v-else>
                  <div class="no-quote-text">--</div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <a-empty v-else description="暂无报价数据" />
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import api from '../../api'
import { formatPrice, bondTypeColor } from '../../utils/format'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

interface BondInfo {
  bond_id: string
  code: string
  name: string
  bond_type: string
  coupon_rate?: number
  remaining_term?: number
  credit_rating?: string
}

interface SourceInfo {
  source_id: string
  name: string
  source_type: string
}

interface QuoteCell {
  bid_price?: number
  ask_price?: number
  bid_yield?: number
  ask_yield?: number
  quote_time?: string
}

interface MatrixRow {
  bond: BondInfo
  quotes: Record<string, QuoteCell | undefined>
}

interface MatrixData {
  bonds: BondInfo[]
  sources: SourceInfo[]
  matrix: MatrixRow[]
}

const props = defineProps<{
  defaultSourceType?: string
  bondLimit?: number
}>()

const emit = defineEmits<{
  (e: 'quote-click', bondId: string, quote: QuoteCell): void
}>()

const router = useRouter()

const loading = ref(false)
const matrixData = ref<MatrixData | null>(null)
const sourceType = ref(props.defaultSourceType || 'broker')
const refreshInterval = ref(30)
const autoRefresh = ref(true)

const sourceTypeOptions = [
  { value: 'broker', label: '货币经纪' },
  { value: 'xbond', label: '银行间xBond' },
  { value: 'exchange', label: '交易所' },
]

const refreshOptions = [
  { value: 10, label: '10秒刷新' },
  { value: 30, label: '30秒刷新' },
  { value: 60, label: '1分钟刷新' },
  { value: 0, label: '手动刷新' },
]

let refreshTimer: ReturnType<typeof setInterval> | null = null

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get<MatrixData>('/api/quotes/matrix', {
      params: {
        source_type: sourceType.value,
        bond_limit: props.bondLimit || 15,
      },
    })
    matrixData.value = res.data
  } catch (e) {
    message.error('获取报价数据失败')
    matrixData.value = null
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchData()
}

function handleSourceTypeChange() {
  fetchData()
}

function handleRefreshChange(val: number) {
  autoRefresh.value = val > 0
  setupRefreshTimer()
}

function setupRefreshTimer() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (refreshInterval.value > 0) {
    refreshTimer = setInterval(() => {
      fetchData()
    }, refreshInterval.value * 1000)
  }
}

function formatTimeAgo(timeStr?: string): string {
  if (!timeStr) return '--'
  return dayjs(timeStr).fromNow()
}

function goToDetail(bondId: string) {
  router.push(`/market/${bondId}`)
}

function handleQuoteClick(bondId: string, quote: QuoteCell | undefined) {
  if (quote) {
    emit('quote-click', bondId, quote)
    goToDetail(bondId)
  }
}

watch(
  () => props.defaultSourceType,
  (val) => {
    if (val) {
      sourceType.value = val
    }
  }
)

onMounted(() => {
  fetchData()
  setupRefreshTimer()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped>
.broker-quote-board {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.board-container {
  overflow-x: auto;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

.quote-grid {
  min-width: max-content;
}

.grid-header {
  display: flex;
  position: sticky;
  top: 0;
  z-index: 10;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 6px 6px 0 0;
}

.corner-cell {
  min-width: 180px;
  padding: 12px 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
}

.bond-info .bond-code {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 13px;
}

.source-cell {
  flex: 1;
  min-width: 140px;
  padding: 12px 8px;
  text-align: center;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.source-cell:last-child {
  border-right: none;
}

.source-name {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.grid-body {
  border: 1px solid #e5e7eb;
  border-top: none;
  border-radius: 0 0 6px 6px;
}

.grid-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.grid-row:last-child {
  border-bottom: none;
}

.grid-row:hover {
  background-color: #f8fafc;
}

.bond-cell {
  min-width: 180px;
  padding: 10px 16px;
  border-right: 1px solid #e5e7eb;
  cursor: pointer;
  background: #fafafa;
}

.bond-cell:hover {
  background: #f0f7ff;
}

.bond-code {
  font-size: 13px;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 2px;
}

.bond-name {
  font-size: 12px;
  color: #4b5563;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.bond-meta :deep(.ant-tag) {
  font-size: 11px;
  padding: 0 6px;
  height: 18px;
  line-height: 16px;
}

.quote-cell {
  flex: 1;
  min-width: 140px;
  padding: 8px 10px;
  border-right: 1px solid #f0f0f0;
  text-align: center;
  transition: all 0.2s;
}

.quote-cell:last-child {
  border-right: none;
}

.quote-cell.has-quote.clickable {
  cursor: pointer;
}

.quote-cell.has-quote.clickable:hover {
  background: #eff6ff;
  box-shadow: inset 0 0 0 1px #3b82f6;
}

.quote-cell.no-quote {
  background: #fafafa;
}

.quote-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 4px;
}

.quote-label {
  font-size: 11px;
  font-weight: 500;
  width: 18px;
  text-align: center;
  padding: 1px 4px;
  border-radius: 3px;
}

.bid-row .quote-label {
  background: #fef2f2;
  color: #dc2626;
}

.ask-row .quote-label {
  background: #f0fdf4;
  color: #16a34a;
}

.quote-price {
  font-size: 14px;
  font-weight: 600;
  flex: 1;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.bid-price {
  color: #dc2626;
}

.ask-price {
  color: #16a34a;
}

.quote-time {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 4px;
  text-align: right;
  padding-right: 4px;
}

.no-quote-text {
  font-size: 18px;
  color: #d1d5db;
  line-height: 40px;
}

.grid-body::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}

.grid-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.grid-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.grid-body::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
