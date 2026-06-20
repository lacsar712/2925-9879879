<template>
  <div class="research-list">
    <a-card class="mb-4 rounded-lg">
      <a-row :gutter="[16, 16]" align="middle">
        <a-col :flex="1">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索研报标题、机构、内容或债券代码/名称"
            allow-clear
            enter-button="搜索"
            size="large"
            @search="handleSearch"
          />
        </a-col>
        <a-col>
          <a-select
            v-model:value="ratingFilter"
            placeholder="评级观点"
            allow-clear
            style="width: 140px"
            :options="ratingOptions"
          />
        </a-col>
        <a-col>
          <a-button type="primary" @click="handleSearch">
            搜索
          </a-button>
        </a-col>
      </a-row>
    </a-card>

    <div class="space-y-4">
      <a-card
        v-for="report in reports"
        :key="report.id"
        class="research-card hover:shadow-md transition-shadow cursor-pointer"
        @click="goToDetail(report.id)"
      >
        <div class="flex justify-between items-start mb-3">
          <h3 class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors">
            {{ report.title }}
          </h3>
          <a-tag :color="ratingColor(report.rating)">
            {{ report.rating }}
          </a-tag>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500 mb-3">
          <span class="flex items-center gap-1">
            <BankOutlined />
            {{ report.institution }}
          </span>
          <span class="flex items-center gap-1">
            <CalendarOutlined />
            {{ report.publish_date }}
          </span>
        </div>

        <p class="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
          {{ report.summary }}
        </p>

        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-sm text-gray-500">关联债券：</span>
          <a-tag
            v-for="bond in report.bonds"
            :key="bond.id"
            color="blue"
            class="cursor-pointer hover:opacity-80"
            @click.stop="goToBond(bond.id)"
          >
            {{ bond.name }} ({{ bond.code }})
          </a-tag>
        </div>
      </a-card>
    </div>

    <div v-if="reports.length === 0" class="text-center py-12">
      <a-empty description="暂无研报数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BankOutlined, CalendarOutlined } from '@ant-design/icons-vue'
import { getResearchReports, type ResearchReport } from '../mock/research'

const router = useRouter()

const keyword = ref('')
const ratingFilter = ref<string | undefined>(undefined)

const ratingOptions = [
  { label: '推荐', value: '推荐' },
  { label: '增持', value: '增持' },
  { label: '中性', value: '中性' },
  { label: '减持', value: '减持' },
  { label: '卖出', value: '卖出' },
]

const allReports = ref<ResearchReport[]>([])

const reports = computed(() => {
  let results = [...allReports.value]

  if (ratingFilter.value) {
    results = results.filter((r) => r.rating === ratingFilter.value)
  }

  return results
})

function ratingColor(rating: string): string {
  const map: Record<string, string> = {
    '推荐': 'green',
    '增持': 'blue',
    '中性': 'default',
    '减持': 'orange',
    '卖出': 'red',
  }
  return map[rating] || 'default'
}

function handleSearch() {
  allReports.value = getResearchReports(keyword.value || undefined)
}

function goToDetail(id: string) {
  router.push(`/research/${id}`)
}

function goToBond(id: string) {
  router.push(`/market/${id}`)
}

onMounted(() => {
  allReports.value = getResearchReports()
})
</script>

<style scoped>
.research-card {
  border-radius: 8px;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
