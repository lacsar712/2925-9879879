<template>
  <a-modal
    :open="visible"
    :footer="null"
    :centered="true"
    :width="600"
    :closable="true"
    @cancel="handleClose"
    :body-style="{ padding: '12px' }"
    class="global-search-modal"
  >
    <div class="search-input-wrap">
      <a-input
        ref="inputRef"
        v-model:value="searchValue"
        size="large"
        placeholder="搜索页面、功能... (Ctrl+K)"
        :prefix="searchIcon"
        allow-clear
        @input="handleSearch"
        @press-enter="handleEnter"
      />
    </div>

    <div class="search-results mt-3">
      <div v-if="searchValue && results.length === 0" class="no-results">
        未找到匹配的结果
      </div>
      <template v-else>
        <div
          v-for="(item, idx) in results"
          :key="item.path"
          class="result-item"
          :class="{ active: activeIndex === idx }"
          @click="navigateTo(item.path)"
          @mouseenter="activeIndex = idx"
        >
          <component :is="item.icon" class="result-icon" />
          <div class="result-content">
            <div class="result-title">{{ item.title }}</div>
            <div class="result-path">{{ item.path }}</div>
          </div>
          <kbd class="kbd">Enter</kbd>
        </div>
      </template>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, h } from 'vue'
import { useRouter } from 'vue-router'
import { useHotkeysStore } from '../../stores/hotkeys'
import {
  DashboardOutlined,
  CalendarOutlined,
  StockOutlined,
  TableOutlined,
  HistoryOutlined,
  SwapOutlined,
  FundOutlined,
  TransactionOutlined,
  FileTextOutlined,
  StarOutlined,
  SearchOutlined,
  QuestionCircleOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'

interface SearchItem {
  title: string
  path: string
  keywords: string[]
  icon: any
}

const searchableItems: SearchItem[] = [
  { title: '行情看板', path: '/dashboard', keywords: ['dashboard', '看板', '首页', '概览'], icon: DashboardOutlined },
  { title: '债券日历', path: '/calendar', keywords: ['calendar', '日历', '债券'], icon: CalendarOutlined },
  { title: '聚合行情', path: '/market', keywords: ['market', '行情', '聚合'], icon: StockOutlined },
  { title: '经纪商报价板', path: '/quote-board', keywords: ['quote', '报价', '经纪商'], icon: TableOutlined },
  { title: '历史行情回放', path: '/history-replay', keywords: ['history', '历史', '回放'], icon: HistoryOutlined },
  { title: '成交记录', path: '/trades', keywords: ['trades', '成交', '交易'], icon: SwapOutlined },
  { title: '国债期货', path: '/futures', keywords: ['futures', '期货', '国债'], icon: FundOutlined },
  { title: '收益互换', path: '/swaps', keywords: ['swaps', '互换', '收益'], icon: TransactionOutlined },
  { title: '研报摘要', path: '/research', keywords: ['research', '研报', '研究'], icon: FileTextOutlined },
  { title: '我的关注', path: '/favorites', keywords: ['favorites', '收藏', '关注'], icon: StarOutlined },
  { title: '快捷键说明', path: '/shortcuts', keywords: ['shortcuts', '快捷键', '帮助', '热键'], icon: QuestionCircleOutlined },
  { title: '用户管理', path: '/admin/users', keywords: ['admin', 'users', '用户'], icon: SettingOutlined },
  { title: '行情源管理', path: '/admin/sources', keywords: ['admin', 'sources', '行情源'], icon: SettingOutlined },
]

const router = useRouter()
const hotkeysStore = useHotkeysStore()
const inputRef = ref<any>(null)
const searchValue = ref('')
const activeIndex = ref(0)

const visible = computed(() => hotkeysStore.searchVisible)

const searchIcon = h(SearchOutlined)

const results = computed(() => {
  if (!searchValue.value.trim()) return searchableItems.slice(0, 8)
  const q = searchValue.value.toLowerCase().trim()
  return searchableItems
    .filter(item => {
      if (item.title.toLowerCase().includes(q)) return true
      if (item.path.toLowerCase().includes(q)) return true
      return item.keywords.some(k => k.toLowerCase().includes(q))
    })
    .slice(0, 8)
})

watch(visible, (v) => {
  if (v) {
    nextTick(() => {
      searchValue.value = ''
      activeIndex.value = 0
      inputRef.value?.focus()
    })
  }
})

watch(results, () => {
  activeIndex.value = 0
})

function handleSearch() {
  activeIndex.value = 0
}

function handleEnter() {
  if (results.value[activeIndex.value]) {
    navigateTo(results.value[activeIndex.value].path)
  }
}

function navigateTo(path: string) {
  hotkeysStore.closeSearch()
  router.push(path)
}

function handleClose() {
  hotkeysStore.closeSearch()
}
</script>

<style scoped>
.global-search-modal :deep(.ant-modal-content) {
  border-radius: 12px;
  overflow: hidden;
}

.global-search-modal :deep(.ant-modal-body) {
  padding: 12px !important;
}

.search-input-wrap :deep(.ant-input-affix-wrapper) {
  border-radius: 8px;
  padding: 4px 12px;
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
  margin: 0 -12px;
  padding: 4px 0;
}

.no-results {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.result-item:hover,
.result-item.active {
  background: #f5f5f5;
}

.result-icon {
  font-size: 18px;
  color: #1890ff;
  flex-shrink: 0;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.result-path {
  font-size: 12px;
  color: #999;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.kbd {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  font-size: 11px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #6b7280;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-bottom-width: 2px;
  border-radius: 4px;
  text-align: center;
}
</style>
