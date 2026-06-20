<template>
  <div class="data-quality-monitoring p-4">
    <a-spin :spinning="loading" tip="加载中...">
      <a-row :gutter="[16, 16]" class="mb-6">
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-green-50/80">
            <a-statistic
              title="综合健康分"
              :value="overview?.avg_health_score ?? 0"
              :precision="1"
              :value-style="{ color: healthScoreColor(overview?.avg_health_score) }"
              class="tabular-nums"
            >
              <template #prefix>
                <HeartOutlined :style="{ color: healthScoreColor(overview?.avg_health_score) }" />
              </template>
              <template #suffix>分</template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-blue-50/80">
            <a-statistic
              title="行情源总数"
              :value="overview?.total_sources ?? 0"
              class="tabular-nums"
            >
              <template #prefix>
                <DatabaseOutlined class="text-blue-500" />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-emerald-50/80">
            <a-statistic
              title="在线/正常"
              :value="overview?.healthy_sources ?? 0"
              class="tabular-nums"
            >
              <template #prefix>
                <CheckCircleOutlined class="text-emerald-500" />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-amber-50/80">
            <a-statistic
              title="需关注"
              :value="overview?.warning_sources ?? 0"
              class="tabular-nums"
            >
              <template #prefix>
                <WarningOutlined class="text-amber-500" />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-red-50/80">
            <a-statistic
              title="异常"
              :value="overview?.critical_sources + (overview?.error_sources ?? 0)"
              class="tabular-nums"
            >
              <template #prefix>
                <ExclamationCircleOutlined class="text-red-500" />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="8" :md="6" :lg="4">
          <a-card class="rounded-lg bg-purple-50/80">
            <a-statistic
              title="平均延迟"
              :value="overview?.avg_latency_ms ?? 0"
              :precision="1"
              class="tabular-nums"
            >
              <template #prefix>
                <ClockCircleOutlined class="text-purple-500" />
              </template>
              <template #suffix>ms</template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <a-row :gutter="[16, 16]" class="mb-6">
        <a-col :xs="12" :sm="12" :md="8" :lg="6">
          <a-card class="rounded-lg" size="small">
            <div class="flex items-center justify-between">
              <span class="text-gray-500 text-sm">当日缺失报价</span>
              <span class="tabular-nums font-semibold text-lg">
                {{ overview?.total_missing_quotes ?? 0 }}
                <span class="text-xs text-gray-400 font-normal">次</span>
              </span>
            </div>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="12" :md="8" :lg="6">
          <a-card class="rounded-lg" size="small">
            <div class="flex items-center justify-between">
              <span class="text-gray-500 text-sm">买卖价倒挂</span>
              <span class="tabular-nums font-semibold text-lg">
                {{ overview?.total_inverted_spreads ?? 0 }}
                <span class="text-xs text-gray-400 font-normal">次</span>
              </span>
            </div>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="12" :md="8" :lg="6">
          <a-card class="rounded-lg" size="small">
            <div class="flex items-center justify-between">
              <span class="text-gray-500 text-sm">已禁用</span>
              <span class="tabular-nums font-semibold text-lg">
                {{ overview?.disabled_sources ?? 0 }}
                <span class="text-xs text-gray-400 font-normal">个</span>
              </span>
            </div>
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="12" :md="8" :lg="6">
          <a-card class="rounded-lg" size="small">
            <div class="flex items-center justify-between">
              <span class="text-gray-500 text-sm">在线/离线</span>
              <span class="tabular-nums font-semibold text-lg">
                {{ overview?.online_sources ?? 0 }}
                <span class="text-gray-400 mx-1">/</span>
                {{ overview?.offline_sources ?? 0 }}
              </span>
            </div>
          </a-card>
        </a-col>
      </a-row>

      <a-card title="行情源数据质量明细" class="rounded-lg">
        <a-table
          :data-source="sources"
          :columns="columns"
          :pagination="false"
          :scroll="{ x: 'max-content' }"
          :row-key="(r) => r.id"
          :row-class-name="(record) => getRowClassName(record)"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'source_type'">
              <a-tag :color="sourceTypeColor(record.source_type)">
                {{ sourceTypeLabel(record.source_type) }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'status'">
              <a-badge
                v-if="record.is_enabled"
                :status="sourceStatusBadge(record.status)"
                :text="sourceStatusText(record.status)"
              />
              <a-tag v-else color="default">已禁用（离线）</a-tag>
            </template>
            <template v-else-if="column.key === 'health_score'">
              <template v-if="record.is_enabled && record.health_score !== null">
                <a-progress
                  :percent="Math.round(record.health_score)"
                  :stroke-color="healthScoreColor(record.health_score)"
                  size="small"
                />
                <span
                  class="tabular-nums ml-2 font-medium"
                  :style="{ color: healthScoreColor(record.health_score) }"
                >
                  {{ record.health_score.toFixed(1) }}
                </span>
              </template>
              <span v-else class="text-gray-400">--</span>
            </template>
            <template v-else-if="column.key === 'avg_latency_ms'">
              <template v-if="record.is_enabled && record.avg_latency_ms !== null">
                <span
                  class="tabular-nums"
                  :class="latencyClass(record.avg_latency_ms)"
                >
                  {{ record.avg_latency_ms.toFixed(1) }}
                  <span class="text-xs text-gray-400">ms</span>
                </span>
              </template>
              <span v-else class="text-gray-400">--</span>
            </template>
            <template v-else-if="column.key === 'today_missing_quotes'">
              <template v-if="record.is_enabled">
                <span
                  class="tabular-nums"
                  :class="record.today_missing_quotes > 10 ? 'text-red-600 font-medium' : record.today_missing_quotes > 0 ? 'text-amber-600' : 'text-gray-700'"
                >
                  {{ record.today_missing_quotes }}
                </span>
              </template>
              <span v-else class="text-gray-400">--</span>
            </template>
            <template v-else-if="column.key === 'today_inverted_spreads'">
              <template v-if="record.is_enabled">
                <span
                  class="tabular-nums"
                  :class="record.today_inverted_spreads > 5 ? 'text-red-600 font-medium' : record.today_inverted_spreads > 0 ? 'text-amber-600' : 'text-gray-700'"
                >
                  {{ record.today_inverted_spreads }}
                </span>
              </template>
              <span v-else class="text-gray-400">--</span>
            </template>
            <template v-else-if="column.key === 'last_heartbeat'">
              <template v-if="record.is_enabled && record.last_heartbeat">
                <span class="tabular-nums text-sm">{{ formatDateTime(record.last_heartbeat) }}</span>
              </template>
              <span v-else class="text-gray-400">--</span>
            </template>
          </template>
        </a-table>
      </a-card>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  HeartOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons-vue'
import {
  getDataQualityOverview,
  getDataQualitySources,
  type DataQualityOverview,
  type DataQualitySource,
} from '../../api'
import { sourceTypeLabel, formatDateTime } from '../../utils/format'

const loading = ref(false)
const overview = ref<DataQualityOverview | null>(null)
const sources = ref<DataQualitySource[]>([])

function sourceStatusBadge(status: string): 'success' | 'warning' | 'error' | 'default' {
  const map: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    online: 'success',
    offline: 'warning',
    error: 'error',
  }
  return map[status] || 'default'
}

function sourceStatusText(status: string): string {
  const map: Record<string, string> = {
    online: '在线',
    offline: '离线',
    error: '异常',
  }
  return map[status] || status
}

function sourceTypeColor(type: string): string {
  const map: Record<string, string> = {
    xbond: 'blue',
    broker: 'purple',
    exchange: 'green',
    swap: 'cyan',
    futures: 'orange',
  }
  return map[type] || 'default'
}

function healthScoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return '#bfbfbf'
  if (score >= 80) return '#52c41a'
  if (score >= 60) return '#faad14'
  return '#ff4d4f'
}

function latencyClass(latency: number): string {
  if (latency >= 100) return 'text-red-600 font-medium'
  if (latency >= 50) return 'text-amber-600'
  return 'text-gray-700'
}

function getRowClassName(record: DataQualitySource): string {
  if (!record.is_enabled) return 'row-disabled'
  if (record.health_score !== null && record.health_score < 60) return 'row-critical'
  if (record.status === 'error') return 'row-critical'
  if (record.health_score !== null && record.health_score < 80) return 'row-warning'
  return ''
}

const columns = [
  { title: '行情源名称', dataIndex: 'name', key: 'name', width: 140, fixed: 'left' as const },
  { title: '类型', key: 'source_type', dataIndex: 'source_type', width: 120 },
  { title: '状态', key: 'status', dataIndex: 'status', width: 120 },
  { title: '综合健康分', key: 'health_score', dataIndex: 'health_score', width: 200 },
  { title: '平均报价延迟', key: 'avg_latency_ms', dataIndex: 'avg_latency_ms', width: 130 },
  { title: '当日缺失报价', key: 'today_missing_quotes', dataIndex: 'today_missing_quotes', width: 130 },
  { title: '买卖价倒挂次数', key: 'today_inverted_spreads', dataIndex: 'today_inverted_spreads', width: 140 },
  { title: '最近心跳时间', key: 'last_heartbeat', dataIndex: 'last_heartbeat', width: 180 },
  { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
]

async function fetchData() {
  loading.value = true
  try {
    const [overviewRes, sourcesRes] = await Promise.all([
      getDataQualityOverview(),
      getDataQualitySources(),
    ])
    overview.value = overviewRes
    sources.value = sourcesRes
  } catch {
    overview.value = null
    sources.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
:deep(.row-critical td) {
  background-color: #fff1f0 !important;
}

:deep(.row-warning td) {
  background-color: #fffbe6 !important;
}

:deep(.row-disabled td) {
  background-color: #f5f5f5 !important;
  color: #bfbfbf !important;
}

:deep(.row-disabled td .ant-tag) {
  opacity: 0.7;
}
</style>
