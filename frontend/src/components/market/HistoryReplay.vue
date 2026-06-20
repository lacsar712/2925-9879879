<template>
  <div class="history-replay">
    <div class="replay-header">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <h3 class="text-lg font-semibold text-gray-800">历史行情回放</h3>
          <a-tag color="purple">
            <template #icon>
              <ClockCircleOutlined />
            </template>
            热门债券
          </a-tag>
        </div>
        <div class="flex items-center gap-2">
          <a-select
            v-model:value="selectedBondId"
            style="width: 280px"
            :options="bondOptions"
            @change="handleBondChange"
          >
            <template #option="{ value, label, extra }">
              <div class="flex items-center justify-between w-full">
                <span>{{ label }}</span>
                <a-tag :color="bondTypeColor(extra.bond_type)" size="small">{{ extra.bond_type }}</a-tag>
              </div>
            </template>
          </a-select>
        </div>
      </div>

      <a-card class="timeline-card">
        <div class="timeline-control">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
            <a-button
              size="small"
              :disabled="currentIndex === 0"
              @click="goToPrevious"
            >
              <template #icon>
                <LeftOutlined />
              </template>
              上一个
            </a-button>
            <a-button
              size="small"
              :disabled="currentIndex === snapshots.length - 1"
              @click="goToNext"
            >
              下一个
              <template #icon>
                <RightOutlined />
              </template>
            </a-button>
            <a-button
              size="small"
              @click="togglePlay"
              :type="isPlaying ? 'danger' : 'primary'"
            >
              <template #icon>
                <component :is="isPlaying ? PauseCircleOutlined : PlayCircleOutlined" />
              </template>
              {{ isPlaying ? '暂停' : '自动播放' }}
            </a-button>
            <a-select
              v-model:value="playSpeed"
              style="width: 100px"
              size="small"
              :options="speedOptions"
            />
            </div>

          <div class="flex items-center gap-3">
            <a-switch
              v-model:checked="showDiff"
              checked-children="差异"
              un-checked-children="正常"
            />
            <a-tag v-if="showDiff">
              <DiffOutlined />
              高亮变动
            </a-tag>
            <div class="current-time">
              <ClockCircleOutlined class="mr-1" />
              <span class="font-mono text-blue-600">{{ currentSnapshotTime }}</span>
            </div>
          </div>
        </div>

        <div class="slider-container">
          <a-slider
            v-model:value="currentIndex"
            :min="0"
            :max="snapshots.length - 1"
            :marks="sliderMarks"
            :tooltip-formatter="tooltipFormatter"
            @change="handleSliderChange"
          />
        </div>

        <div class="timeline-dots">
          <div
            v-for="(snap, index) in snapshots"
            :key="snap.snapshot_id"
            class="timeline-dot"
            :class="{ active: index <= currentIndex, current: index === currentIndex }"
            :title="formatTime(snap.snapshot_time)"
            @click="goToSnapshot(index)"
          />
        </div>
        </div>
      </a-card>
    </div>

    <div v-if="currentSnapshot" class="replay-content">
      <div class="bond-info-bar">
        <a-card class="mb-4">
          <a-row :gutter="16">
            <a-col :span="6">
            <div class="info-item">
              <span class="info-label">债券代码</span>
              <span class="info-value tabular-nums">{{ currentSnapshot.bond.code }}</span>
            </div>
            </a-col>
            <a-col :span="6">
            <div class="info-item">
              <span class="info-label">债券简称</span>
              <span class="info-value">{{ currentSnapshot.bond.name }}</span>
            </div>
            </a-col>
            <a-col :span="4">
            <div class="info-item">
              <span class="info-label">债券类型</span>
              <a-tag :color="bondTypeColor(currentSnapshot.bond.bond_type)">
                {{ currentSnapshot.bond.bond_type }}
              </a-tag>
            </div>
            </a-col>
            <a-col :span="4">
            <div class="info-item">
              <span class="info-label">票面利率</span>
              <span class="info-value tabular-nums">{{ currentSnapshot.bond.coupon_rate }}%</span>
            </div>
            </a-col>
            <a-col :span="4">
            <div class="info-item">
              <span class="info-label">剩余期限</span>
              <span class="info-value">{{ currentSnapshot.bond.remaining_term }}</span>
            </div>
            </a-col>
          </a-row>
        </a-card>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="col-span-2">
          <a-card title="多源报价对比">
            <div class="quote-table-container">
              <div class="quote-table">
                <div class="table-header">
                  <div class="header-cell source-cell">行情源</div>
                  <div class="header-cell bid-cell">买价</div>
                  <div class="header-cell ask-cell">卖价</div>
                  <div class="header-cell bid-vol-cell">买量</div>
                  <div class="header-cell ask-vol-cell">卖量</div>
                  <div class="header-cell time-cell">报价时间</div>
                </div>
                <div
                  v-for="source in currentSnapshot.sources"
                  :key="source.source_id"
                  class="table-row"
                  :class="{ 'has-quote': currentSnapshot.quotes[source.source_id] }"
                >
                  <div class="row-cell source-cell">
                    <span class="source-name">{{ source.name }}</span>
                    <a-tag :color="sourceTypeColor(source.source_type)" size="small">
                      {{ sourceTypeLabel(source.source_type) }}
                    </a-tag>
                  </div>
                  <template v-if="currentSnapshot.quotes[source.source_id]">
                    <div class="row-cell bid-cell">
                      <span
                        class="price-value bid tabular-nums"
                        :class="getBidDiffClass(source.source_id)"
                      >
                        {{ formatPrice(currentSnapshot.quotes[source.source_id]!.bid_price) }}
                      </span>
                      <span
                        v-if="showDiff && diffs[source.source_id]"
                        class="diff-indicator"
                        :class="diffs[source.source_id]!.bid_price_change"
                      >
                        {{ formatDiff(diffs[source.source_id]!.bid_price_diff) }}
                      </span>
                    </div>
                    <div class="row-cell ask-cell">
                      <span
                        class="price-value ask tabular-nums"
                        :class="getAskDiffClass(source.source_id)"
                      >
                        {{ formatPrice(currentSnapshot.quotes[source.source_id]!.ask_price) }}
                      </span>
                      <span
                        v-if="showDiff && diffs[source.source_id]"
                        class="diff-indicator"
                        :class="diffs[source.source_id]!.ask_price_change"
                      >
                        {{ formatDiff(diffs[source.source_id]!.ask_price_diff) }}
                      </span>
                    </div>
                    <div class="row-cell bid-vol-cell">
                      <span class="vol-value tabular-nums">
                        {{ formatVolume(currentSnapshot.quotes[source.source_id]!.bid_volume) }}
                      </span>
                    </div>
                    <div class="row-cell ask-vol-cell">
                      <span class="vol-value tabular-nums">
                        {{ formatVolume(currentSnapshot.quotes[source.source_id]!.ask_volume) }}
                      </span>
                    </div>
                    <div class="row-cell time-cell">
                      <span class="time-value tabular-nums">
                        {{ formatTime(currentSnapshot.quotes[source.source_id]!.quote_time) }}
                      </span>
                    </div>
                  </template>
                  <template v-else>
                    <div class="row-cell bid-cell no-quote">--</div>
                    <div class="row-cell ask-cell no-quote">--</div>
                    <div class="row-cell bid-vol-cell no-quote">--</div>
                    <div class="row-cell ask-vol-cell no-quote">--</div>
                    <div class="row-cell time-cell no-quote">--</div>
                  </template>
                </div>
              </div>
            </div>
          </a-card>
        </div>

        <div class="col-span-1">
          <a-card title="本时段成交">
            <a-table
              :data-source="currentSnapshot.trades"
              :columns="tradeColumns"
              :pagination="false"
              size="small"
              :scroll="{ y: 320 }"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'direction'">
                  <a-tag :color="record.direction === 'buy' ? 'red' : 'green'" size="small">
                    {{ record.direction === 'buy' ? '买入' : '卖出' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'price'">
                  <span
                    class="tabular-nums"
                    :class="record.direction === 'buy' ? 'text-red-600' : 'text-green-600'"
                  >
                    {{ formatPrice(record.price) }}
                  </span>
                </template>
                <template v-else-if="column.key === 'volume'">
                  <span class="tabular-nums">{{ formatVolume(record.volume) }}</span>
                </template>
                <template v-else-if="column.key === 'source'">
                  <span class="text-xs text-gray-600">{{ record.source }}</span>
                </template>
                <template v-else-if="column.key === 'trade_time'">
                  <span class="tabular-nums text-xs">{{ formatTime(record.trade_time) }}</span>
                </template>
              </template>
            </a-table>
          </a-card>
        </div>
      </div>
    </div>

    <a-empty v-else description="请选择债券查看历史行情" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import {
  ClockCircleOutlined,
  LeftOutlined,
  RightOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DiffOutlined,
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import {
  getHotBonds,
  getHistoryReplayData,
  calculateSnapshotDiff,
  type QuoteSnapshot,
  type QuoteDiff,
} from '../../mock/historyReplay'
import { formatPrice, formatVolume, formatTime, bondTypeColor, sourceTypeLabel } from '../../utils/format'

const props = defineProps<{
  defaultBondId?: string
}>()

const emit = defineEmits<{
  (e: 'snapshot-change', snapshot: QuoteSnapshot): void
}>()

const hotBonds = getHotBonds()
const bondOptions = hotBonds.map((b) => ({
  value: b.bond_id,
  label: `${b.code} ${b.name}`,
  extra: b,
}))

const selectedBondId = ref(props.defaultBondId || hotBonds[0]?.bond_id || '')
const snapshots = ref<QuoteSnapshot[]>([])
const currentIndex = ref(0)
const showDiff = ref(false)
const isPlaying = ref(false)
const playSpeed = ref(2000)

const speedOptions = [
  { value: 3000, label: '0.5x' },
  { value: 2000, label: '1x' },
  { value: 1000, label: '2x' },
  { value: 500, label: '4x' },
]

const tradeColumns = [
  { title: '方向', key: 'direction', dataIndex: 'direction', width: 70 },
  { title: '价格', key: 'price', dataIndex: 'price', width: 90 },
  { title: '成交量', key: 'volume', dataIndex: 'volume', width: 80 },
  { title: '来源', key: 'source', dataIndex: 'source', width: 80 },
  { title: '成交时间', key: 'trade_time', dataIndex: 'trade_time', width: 80 },
]

let playTimer: ReturnType<typeof setInterval> | null = null

const currentSnapshot = computed<QuoteSnapshot | undefined>(() => snapshots.value[currentIndex.value])

const currentSnapshotTime = computed(() => {
  if (!currentSnapshot.value) return '--'
  return formatTime(currentSnapshot.value.snapshot_time)
})

const previousSnapshot = computed<QuoteSnapshot | undefined>(
  () => currentIndex.value > 0 ? snapshots.value[currentIndex.value - 1] : undefined
)

const diffs = computed<Record<string, QuoteDiff>>(() => {
  if (!currentSnapshot.value || !showDiff.value) return {}
  return calculateSnapshotDiff(currentSnapshot.value, previousSnapshot.value)
})

const sliderMarks = computed(() => {
  const marks: Record<number, string> = {}
  snapshots.value.forEach((snap, index) => {
    if (index % 3 === 0 || index === snapshots.value.length - 1) {
      marks[index] = formatTime(snap.snapshot_time)
    }
  })
  return marks
})

function sourceTypeColor(type: string): string {
  const map: Record<string, string> = {
    broker: 'blue',
    xbond: 'geekblue',
    exchange: 'purple',
  }
  return map[type] || 'default'
}

function tooltipFormatter(value: number): string {
  if (!snapshots.value[value]) return ''
  return formatTime(snapshots.value[value].snapshot_time)
}

function handleBondChange() {
  loadSnapshots()
}

function loadSnapshots() {
  const data = getHistoryReplayData(selectedBondId.value)
  if (data) {
    snapshots.value = data.snapshots
    currentIndex.value = 0
  } else {
    snapshots.value = []
    message.warning('该债券暂无历史快照数据')
  }
}

function handleSliderChange(value: number) {
  currentIndex.value = value
  if (currentSnapshot.value) {
    emit('snapshot-change', currentSnapshot.value)
  }
}

function goToSnapshot(index: number) {
  currentIndex.value = index
  if (currentSnapshot.value) {
    emit('snapshot-change', currentSnapshot.value)
  }
}

function goToPrevious() {
  if (currentIndex.value > 0) {
    currentIndex.value--
    if (currentSnapshot.value) {
      emit('snapshot-change', currentSnapshot.value)
    }
  }
}

function goToNext() {
  if (currentIndex.value < snapshots.value.length - 1) {
    currentIndex.value++
    if (currentSnapshot.value) {
      emit('snapshot-change', currentSnapshot.value)
    }
  }
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    startAutoPlay()
  } else {
    stopAutoPlay()
  }
}

function startAutoPlay() {
  stopAutoPlay()
  playTimer = setInterval(() => {
    if (currentIndex.value < snapshots.value.length - 1) {
      currentIndex.value++
      if (currentSnapshot.value) {
        emit('snapshot-change', currentSnapshot.value)
      }
    } else {
      currentIndex.value = 0
    }
  }, playSpeed.value)
}

function stopAutoPlay() {
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
}

function formatDiff(diff?: number): string {
  if (diff === undefined) return ''
  const sign = diff > 0 ? '+' : ''
  return `${sign}${diff.toFixed(4)}`
}

function getBidDiffClass(sourceId: string): string {
  if (!showDiff.value || !diffs.value[sourceId]) return ''
  const change = diffs.value[sourceId]?.bid_price_change
  if (change === 'up') return 'diff-up'
  if (change === 'down') return 'diff-down'
  return ''
}

function getAskDiffClass(sourceId: string): string {
  if (!showDiff.value || !diffs.value[sourceId]) return ''
  const change = diffs.value[sourceId]?.ask_price_change
  if (change === 'up') return 'diff-up'
  if (change === 'down') return 'diff-down'
  return ''
}

watch(
  () => props.defaultBondId,
  (val) => {
    if (val) {
      selectedBondId.value = val
      loadSnapshots()
    }
  }
)

watch(playSpeed, () => {
  if (isPlaying.value) {
    stopAutoPlay()
    startAutoPlay()
  }
})

loadSnapshots()

onUnmounted(() => {
  stopAutoPlay()
})
</script>

<style scoped>
.history-replay {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.replay-header {
  margin-bottom: 16px;
}

.timeline-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.timeline-control {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-time {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  background: #eff6ff;
  border-radius: 16px;
}

.slider-container {
  margin: 16px 0;
  padding: 0 8px;
}

.timeline-dots {
  display: flex;
  justify-content: space-between;
  padding: 0 8px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
}

.timeline-dot.active {
  background: #3b82f6;
}

.timeline-dot.current {
  transform: scale(1.4);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.timeline-dot:hover {
  transform: scale(1.2);
}

.bond-info-bar .info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #6b7280;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.quote-table-container {
  overflow-x: auto;
}

.quote-table {
  min-width: 100%;
}

.table-header {
  display: flex;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 6px 6px 0 0;
}

.header-cell {
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 13px;
  text-align: center;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.header-cell:last-child {
  border-right: none;
}

.header-cell.source-cell {
  flex: 1.5;
  text-align: left;
}

.header-cell.bid-cell,
.header-cell.ask-cell {
  flex: 1;
}

.header-cell.bid-vol-cell,
.header-cell.ask-vol-cell {
  flex: 0.8;
}

.header-cell.time-cell {
  flex: 1;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: #f8fafc;
}

.table-row.has-quote {
  background-color: #fff;
}

.row-cell {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #f0f0f0;
}

.row-cell:last-child {
  border-right: none;
}

.row-cell.source-cell {
  flex: 1.5;
  justify-content: flex-start;
  gap: 8px;
}

.row-cell.bid-cell,
.row-cell.ask-cell {
  flex: 1;
  gap: 4px;
}

.row-cell.bid-vol-cell,
.row-cell.ask-vol-cell {
  flex: 0.8;
}

.row-cell.time-cell {
  flex: 1;
}

.source-name {
  font-weight: 600;
  color: #1e3a8a;
}

.price-value {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.price-value.bid {
  color: #dc2626;
}

.price-value.ask {
  color: #16a34a;
}

.price-value.bid.diff-up {
  animation: flash-up 0.5s ease-in-out;
}

.price-value.bid.diff-down {
  animation: flash-down 0.5s ease-in-out;
}

.price-value.ask.diff-up {
  animation: flash-up 0.5s ease-in-out;
}

.price-value.ask.diff-down {
  animation: flash-down 0.5s ease-in-out;
}

.diff-indicator {
  font-size: 11px;
  font-weight: 500;
}

.diff-indicator.up {
  color: #dc2626;
}

.diff-indicator.down {
  color: #16a34a;
}

.diff-indicator.unchanged {
  color: #6b7280;
}

.vol-value {
  font-size: 13px;
  color: #4b5563;
}

.time-value {
  font-size: 12px;
  color: #6b7280;
}

.row-cell.no-quote {
  color: #d1d5db;
  font-size: 16px;
}

@keyframes flash-up {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(220, 38, 38, 0.15); }
}

@keyframes flash-down {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(22, 163, 74, 0.15); }
}
</style>
