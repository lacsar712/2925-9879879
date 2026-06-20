<template>
  <div class="rating-changes p-4">
    <a-spin :spinning="loading" tip="加载中...">
      <a-card class="rounded-lg">
        <template #title>
          <div class="flex items-center gap-2">
            <RiseOutlined class="text-blue-500" />
            <span>评级变动追踪</span>
          </div>
        </template>
        <template #extra>
          <div class="flex items-center gap-3">
            <span class="text-sm text-gray-500">筛选：</span>
            <a-segmented
              v-model:value="filterType"
              :options="filterOptions"
              size="small"
              @change="handleFilterChange"
            />
          </div>
        </template>

        <div class="mt-4">
          <a-empty v-if="!loading && ratingChanges.length === 0" description="暂无评级变动数据" />

          <div v-else class="relative">
            <div
              v-for="(group, groupIndex) in groupedChanges"
              :key="group.date"
              class="mb-6"
            >
              <div class="flex items-center gap-2 mb-3">
                <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                <span class="text-sm font-medium text-gray-600">{{ group.date }}</span>
                <a-tag color="blue" class="ml-2">{{ group.items.length }} 条变动</a-tag>
              </div>

              <div class="ml-4 pl-6 border-l-2 border-gray-200 relative">
                <div
                  v-for="(item, index) in group.items"
                  :key="item.id"
                  class="mb-4 relative"
                >
                  <div
                    class="absolute -left-[34px] top-3 w-4 h-4 rounded-full border-3 bg-white flex items-center justify-center"
                    :class="getDotClass(item.change_type)"
                  >
                    <component :is="getIcon(item.change_type)" :class="getIconClass(item.change_type)" />
                  </div>

                  <a-card
                    hoverable
                    class="cursor-pointer transition-all duration-200 hover:shadow-md"
                    :class="getCardClass(item.change_type)"
                    @click="handleItemClick(item)"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                          <a-tag
                            :color="getChangeTypeColor(item.change_type)"
                            class="font-medium"
                          >
                            {{ getChangeTypeLabel(item.change_type) }}
                          </a-tag>
                          <span class="text-sm text-gray-500">{{ item.agency }}</span>
                        </div>

                        <div class="flex items-center gap-3 mb-2">
                          <router-link
                            :to="`/market/${item.bond_id}`"
                            class="text-base font-semibold text-blue-600 hover:underline"
                            @click.stop
                          >
                            {{ item.bond_name }}
                          </router-link>
                          <span class="text-sm text-gray-500 tabular-nums">{{ item.bond_code }}</span>
                        </div>

                        <div class="flex items-center gap-4 text-sm">
                          <template v-if="item.change_type !== 'outlook'">
                            <div class="flex items-center gap-2">
                              <span class="text-gray-500">评级：</span>
                              <span
                                class="font-medium tabular-nums px-2 py-0.5 rounded"
                                :class="getOldRatingClass(item)"
                              >
                                {{ item.old_rating }}
                              </span>
                              <ArrowRightOutlined class="text-gray-400" />
                              <span
                                class="font-medium tabular-nums px-2 py-0.5 rounded"
                                :class="getNewRatingClass(item)"
                              >
                                {{ item.new_rating }}
                              </span>
                            </div>
                          </template>

                          <div class="flex items-center gap-2">
                            <span class="text-gray-500">展望：</span>
                            <span
                              class="font-medium px-2 py-0.5 rounded"
                              :class="getOldOutlookClass(item)"
                            >
                              {{ item.old_outlook }}
                            </span>
                            <ArrowRightOutlined class="text-gray-400" />
                            <span
                              class="font-medium px-2 py-0.5 rounded"
                              :class="getNewOutlookClass(item)"
                            >
                              {{ item.new_outlook }}
                            </span>
                          </div>
                        </div>

                        <p v-if="item.description" class="mt-2 text-sm text-gray-500 line-clamp-1">
                          {{ item.description }}
                        </p>
                      </div>

                      <div class="flex-shrink-0 ml-4">
                        <span class="text-xs text-gray-400">{{ formatDate(item.effective_date) }}</span>
                      </div>
                    </div>
                  </a-card>
                </div>
              </div>
            </div>
          </div>

          <div v-if="total > 0" class="mt-6 flex justify-center">
            <a-pagination
              v-model:current="pagination.page"
              v-model:pageSize="pagination.pageSize"
              :total="total"
              :show-size-changer="false"
              :show-quick-jumper="false"
              :page-size-options="['10', '20', '50']"
              show-total
              @change="handlePageChange"
            />
          </div>
        </div>
      </a-card>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  RiseOutlined,
  ArrowRightOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons-vue'
import { getRatingChanges, type RatingChange } from '../api'
import { formatDate } from '../utils/format'

const router = useRouter()

const loading = ref(false)
const ratingChanges = ref<RatingChange[]>([])
const total = ref(0)
const filterType = ref<string>('all')

const pagination = ref({
  page: 1,
  pageSize: 20,
})

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '上调', value: 'upgrade' },
  { label: '下调', value: 'downgrade' },
  { label: '展望变动', value: 'outlook' },
]

interface GroupedChanges {
  date: string
  items: RatingChange[]
}

const groupedChanges = computed<GroupedChanges[]>(() => {
  const groups: Record<string, RatingChange[]> = {}
  for (const item of ratingChanges.value) {
    const date = formatDate(item.effective_date)
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(item)
  }
  return Object.entries(groups)
    .map(([date, items]) => ({ date, items }))
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

async function fetchData() {
  loading.value = true
  try {
    const params: { change_type?: string; page: number; page_size: number } = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
    }
    if (filterType.value !== 'all') {
      params.change_type = filterType.value
    }
    const response = await getRatingChanges(params)
    ratingChanges.value = response.items
    total.value = response.total
  } catch {
    ratingChanges.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  pagination.value.page = 1
  fetchData()
}

function handlePageChange(page: number, pageSize: number) {
  pagination.value.page = page
  pagination.value.pageSize = pageSize
  fetchData()
}

function handleItemClick(item: RatingChange) {
  router.push(`/market/${item.bond_id}`)
}

function getChangeTypeLabel(type: string): string {
  const map: Record<string, string> = {
    upgrade: '评级上调',
    downgrade: '评级下调',
    outlook: '展望变动',
  }
  return map[type] || type
}

function getChangeTypeColor(type: string): string {
  const map: Record<string, string> = {
    upgrade: 'green',
    downgrade: 'red',
    outlook: 'orange',
  }
  return map[type] || 'default'
}

function getDotClass(type: string): string {
  const map: Record<string, string> = {
    upgrade: 'border-green-500',
    downgrade: 'border-red-500',
    outlook: 'border-orange-500',
  }
  return map[type] || 'border-gray-500'
}

function getCardClass(type: string): string {
  const map: Record<string, string> = {
    upgrade: 'border-l-4 border-l-green-500',
    downgrade: 'border-l-4 border-l-red-500',
    outlook: 'border-l-4 border-l-orange-500',
  }
  return map[type] || ''
}

function getIcon(type: string) {
  const map: Record<string, any> = {
    upgrade: ArrowUpOutlined,
    downgrade: ArrowDownOutlined,
    outlook: InfoCircleOutlined,
  }
  return map[type] || InfoCircleOutlined
}

function getIconClass(type: string): string {
  const map: Record<string, string> = {
    upgrade: 'text-green-500 text-[10px]',
    downgrade: 'text-red-500 text-[10px]',
    outlook: 'text-orange-500 text-[10px]',
  }
  return map[type] || 'text-gray-500 text-[10px]'
}

function getOldRatingClass(item: RatingChange): string {
  if (item.change_type === 'downgrade') {
    return 'bg-red-50 text-red-600'
  }
  return 'bg-gray-100 text-gray-600'
}

function getNewRatingClass(item: RatingChange): string {
  if (item.change_type === 'upgrade') {
    return 'bg-green-50 text-green-600'
  }
  if (item.change_type === 'downgrade') {
    return 'bg-red-50 text-red-600'
  }
  return 'bg-gray-100 text-gray-600'
}

function getOldOutlookClass(item: RatingChange): string {
  if (item.old_outlook === '负面') {
    return 'bg-red-50 text-red-600'
  }
  if (item.old_outlook === '正面') {
    return 'bg-green-50 text-green-600'
  }
  return 'bg-gray-100 text-gray-600'
}

function getNewOutlookClass(item: RatingChange): string {
  if (item.new_outlook === '负面') {
    return 'bg-red-50 text-red-600'
  }
  if (item.new_outlook === '正面') {
    return 'bg-green-50 text-green-600'
  }
  return 'bg-gray-100 text-gray-600'
}

onMounted(fetchData)
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.border-l-4 {
  border-left-width: 4px;
}

.border-3 {
  border-width: 3px;
}
</style>
