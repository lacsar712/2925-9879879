<template>
  <div class="research-detail">
    <a-breadcrumb class="mb-4">
      <a-breadcrumb-item>
        <router-link to="/research">研报摘要</router-link>
      </a-breadcrumb-item>
      <a-breadcrumb-item>研报详情</a-breadcrumb-item>
    </a-breadcrumb>

    <a-spin :spinning="loading">
      <template v-if="report">
        <a-card class="mb-4">
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-2xl font-bold text-gray-800">{{ report.title }}</h2>
            <a-tag :color="ratingColor(report.rating)" class="text-base px-4 py-1">
              {{ report.rating }}
            </a-tag>
          </div>

          <div class="flex items-center gap-6 text-gray-500 mb-6 pb-6 border-b border-gray-100">
            <span class="flex items-center gap-2">
              <BankOutlined />
              <span>{{ report.institution }}</span>
            </span>
            <span class="flex items-center gap-2">
              <CalendarOutlined />
              <span>{{ report.publish_date }}</span>
            </span>
          </div>

          <div class="prose max-w-none">
            <div
              v-for="(paragraph, index) in contentParagraphs"
              :key="index"
              class="mb-4 text-gray-700 leading-relaxed"
            >
              {{ paragraph }}
            </div>
          </div>
        </a-card>

        <a-card title="相关债券">
          <div class="flex flex-wrap gap-3">
            <router-link
              v-for="bond in report.bonds"
              :key="bond.id"
              :to="`/market/${bond.id}`"
              class="no-underline"
            >
              <a-tag color="blue" class="text-base px-4 py-2 cursor-pointer hover:opacity-80">
                <span class="font-medium">{{ bond.name }}</span>
                <span class="ml-1 text-blue-300 tabular-nums">{{ bond.code }}</span>
              </a-tag>
            </router-link>
          </div>
          <p class="text-gray-500 text-sm mt-4">
            点击债券标签可跳转至债券详情页面查看完整行情信息
          </p>
        </a-card>
      </template>
      <template v-else-if="!loading && error">
        <a-result status="404" title="研报不存在" sub-title="请检查研报 ID 是否正确" />
      </template>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { BankOutlined, CalendarOutlined } from '@ant-design/icons-vue'
import { getResearchReportById, type ResearchReport } from '../mock/research'

const route = useRoute()
const reportId = computed(() => route.params.id as string)

const loading = ref(false)
const error = ref(false)
const report = ref<ResearchReport | null>(null)

const contentParagraphs = computed(() => {
  if (!report.value) return []
  return report.value.content.split('\n').filter((p) => p.trim() !== '')
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

function fetchReport() {
  if (!reportId.value) return
  loading.value = true
  error.value = false

  setTimeout(() => {
    const data = getResearchReportById(reportId.value)
    if (data) {
      report.value = data
    } else {
      error.value = true
      report.value = null
    }
    loading.value = false
  }, 100)
}

watch(reportId, fetchReport, { immediate: true })
</script>

<style scoped>
.prose {
  line-height: 1.8;
}

.prose .mb-4 {
  margin-bottom: 1rem;
}
</style>
