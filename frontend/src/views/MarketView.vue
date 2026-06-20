<template>
  <div class="market-view p-4">
    <!-- 筛选条件标签 -->
    <div v-if="hasActiveFilters" class="mb-4">
      <a-space :size="8" wrap>
        <span class="text-gray-500 text-sm">当前筛选:</span>
        <a-tag
          v-if="filters.bond_type"
          :color="bondTypeColor(filters.bond_type)"
          closable
          @close="clearFilter('bond_type')"
        >
          品种: {{ filters.bond_type }}
        </a-tag>
        <a-tag
          v-if="termBucketLabel"
          color="blue"
          closable
          @close="clearFilter('term_bucket')"
        >
          期限: {{ termBucketLabel }}
        </a-tag>
        <a-tag
          v-if="filters.credit_rating"
          color="purple"
          closable
          @close="clearFilter('credit_rating')"
        >
          评级: {{ filters.credit_rating }}
        </a-tag>
        <a-button type="link" size="small" @click="clearAllFilters">
          清除全部
        </a-button>
      </a-space>
    </div>

    <!-- 顶部筛选栏 -->
    <a-card class="mb-4 rounded-lg">
      <a-row :gutter="[16, 16]" align="middle">
        <a-col :flex="1">
          <a-input-search
            v-model:value="filters.keyword"
            placeholder="关键词搜索债券代码或简称"
            allow-clear
            enter-button="搜索"
            size="large"
            @search="handleSearch"
          />
        </a-col>
        <a-col>
          <a-select
            v-model:value="filters.bond_type"
            placeholder="债券类型"
            allow-clear
            style="width: 140px"
            :options="bondTypeOptions"
            @change="handleSearch"
          />
        </a-col>
        <a-col>
          <a-select
            v-model:value="filters.term_bucket"
            placeholder="剩余期限"
            allow-clear
            style="width: 120px"
            :options="termBucketOptions"
            @change="handleTermBucketChange"
          />
        </a-col>
        <a-col>
          <a-select
            v-model:value="filters.credit_rating"
            placeholder="信用评级"
            allow-clear
            style="width: 120px"
            :options="creditRatingOptions"
            @change="handleSearch"
          />
        </a-col>
        <a-col>
          <a-button type="primary" @click="handleSearch">
            搜索
          </a-button>
        </a-col>
      </a-row>
    </a-card>

    <!-- 债券列表表格 -->
    <a-card class="rounded-lg">
      <a-table
        :data-source="bonds"
        :columns="columns"
        :loading="loading"
        :pagination="false"
        :scroll="{ x: 'max-content' }"
        row-key="id"
        class="bond-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'code'">
            <router-link
              :to="`/market/${record.id}`"
              class="text-blue-600 hover:underline tabular-nums"
            >
              {{ record.code }}
            </router-link>
          </template>
          <template v-else-if="column.key === 'name'">
            <router-link
              :to="`/market/${record.id}`"
              class="text-blue-600 hover:underline"
            >
              {{ record.name }}
            </router-link>
          </template>
          <template v-else-if="column.key === 'type'">
            <a-tag :color="bondTypeColor(record.type)">
              {{ record.type }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'coupon_rate'">
            <span class="tabular-nums">{{ record.coupon_rate != null ? `${record.coupon_rate}%` : '--' }}</span>
          </template>
          <template v-else-if="column.key === 'remaining_term'">
            <span class="tabular-nums">{{ record.remaining_term ?? '--' }}</span>
          </template>
        </template>
      </a-table>

      <div class="flex justify-end mt-4">
        <a-pagination
          v-model:current="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :show-size-changer="true"
          :page-size-options="['10', '20', '50', '100']"
          show-total
          :show-quick-jumper="true"
          @change="handlePageChange"
        />
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { bondTypeColor } from '../utils/format'
import { BOND_TYPES, CREDIT_RATINGS } from '../utils/constants'

interface Bond {
  id: string
  code: string
  name: string
  type: string
  coupon_rate?: number
  remaining_term?: string
  rating?: string
  issuer?: string
}

interface BondsResponse {
  items: Bond[]
  total: number
  page?: number
  page_size?: number
}

const route = useRoute()

const TERM_BUCKETS: { label: string; value: string; min: number; max: number }[] = [
  { label: '1年以内', value: '1年以内', min: 0, max: 1 },
  { label: '1-3年', value: '1-3年', min: 1, max: 3 },
  { label: '3-5年', value: '3-5年', min: 3, max: 5 },
  { label: '5-10年', value: '5-10年', min: 5, max: 10 },
  { label: '10年以上', value: '10年以上', min: 10, max: 999 },
]

const loading = ref(false)
const bonds = ref<Bond[]>([])
const filters = reactive({
  keyword: '',
  bond_type: undefined as string | undefined,
  credit_rating: undefined as string | undefined,
  term_bucket: undefined as string | undefined,
  term_min: undefined as number | undefined,
  term_max: undefined as number | undefined,
})
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const bondTypeOptions = BOND_TYPES.map((t) => ({ label: t, value: t }))
const creditRatingOptions = CREDIT_RATINGS.map((r) => ({ label: r, value: r }))
const termBucketOptions = TERM_BUCKETS.map((t) => ({ label: t.label, value: t.value }))

const termBucketLabel = computed(() => filters.term_bucket)

const hasActiveFilters = computed(() => {
  return !!(filters.bond_type || filters.term_bucket || filters.credit_rating)
})

const columns = [
  { title: '代码', key: 'code', dataIndex: 'code', width: 120, fixed: 'left' },
  { title: '简称', key: 'name', dataIndex: 'name', width: 180 },
  { title: '品种', key: 'type', dataIndex: 'type', width: 100 },
  { title: '票面利率', key: 'coupon_rate', dataIndex: 'coupon_rate', width: 100 },
  { title: '剩余期限', key: 'remaining_term', dataIndex: 'remaining_term', width: 100 },
  { title: '评级', dataIndex: 'rating', key: 'rating', width: 80 },
  { title: '发行人', dataIndex: 'issuer', key: 'issuer', ellipsis: true },
]

async function fetchBonds() {
  loading.value = true
  try {
    const res = await api.get<BondsResponse>('/api/bonds', {
      params: {
        keyword: filters.keyword || undefined,
        bond_type: filters.bond_type,
        credit_rating: filters.credit_rating,
        term_min: filters.term_min,
        term_max: filters.term_max,
        page: pagination.page,
        page_size: pagination.pageSize,
      },
    })
    const data = res.data
    bonds.value = data.items ?? data as unknown as Bond[] ?? []
    pagination.total = data.total ?? bonds.value.length
  } catch {
    bonds.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

let searchTimer: ReturnType<typeof setTimeout> | null = null
function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    fetchBonds()
    searchTimer = null
  }, 300)
}

function handleTermBucketChange(value: string | undefined) {
  if (value) {
    const bucket = TERM_BUCKETS.find((b) => b.value === value)
    if (bucket) {
      filters.term_min = bucket.min
      filters.term_max = bucket.max
    }
  } else {
    filters.term_min = undefined
    filters.term_max = undefined
  }
  handleSearch()
}

function handlePageChange(page: number, pageSize: number) {
  pagination.page = page
  pagination.pageSize = pageSize
  fetchBonds()
}

function clearFilter(key: 'bond_type' | 'term_bucket' | 'credit_rating') {
  if (key === 'term_bucket') {
    filters.term_bucket = undefined
    filters.term_min = undefined
    filters.term_max = undefined
  } else {
    filters[key] = undefined
  }
  pagination.page = 1
  fetchBonds()
}

function clearAllFilters() {
  filters.bond_type = undefined
  filters.credit_rating = undefined
  filters.term_bucket = undefined
  filters.term_min = undefined
  filters.term_max = undefined
  pagination.page = 1
  fetchBonds()
}

function initFromRouteQuery() {
  const queryBondType = route.query.bond_type as string | undefined
  const queryTermBucket = route.query.term_bucket as string | undefined

  if (queryBondType && BOND_TYPES.includes(queryBondType)) {
    filters.bond_type = queryBondType
  }

  if (queryTermBucket) {
    const bucket = TERM_BUCKETS.find((b) => b.value === queryTermBucket)
    if (bucket) {
      filters.term_bucket = bucket.value
      filters.term_min = bucket.min
      filters.term_max = bucket.max
    }
  }
}

watch(
  () => [filters.keyword, filters.bond_type, filters.credit_rating, filters.term_bucket],
  () => {
    pagination.page = 1
  }
)

onMounted(() => {
  initFromRouteQuery()
  fetchBonds()
})
</script>

<style scoped>
.bond-table :deep(.ant-table-tbody > tr:hover > td) {
  background-color: rgb(239 246 255) !important;
}
</style>
