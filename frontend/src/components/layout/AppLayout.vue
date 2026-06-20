<template>
  <a-layout class="app-layout min-h-screen">
    <a-layout-sider
      v-model:collapsed="collapsed"
      :width="220"
      :collapsed-width="0"
      class="app-sider"
    >
      <div class="logo-wrap flex items-center justify-center h-16 px-4 border-b border-white/10">
        <span class="text-white font-bold text-xl tracking-wide">BondView</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        class="app-menu"
        @click="handleMenuClick"
      >
        <a-menu-item key="/dashboard">
          <template #icon>
            <DashboardOutlined />
          </template>
          行情看板
        </a-menu-item>
        <a-menu-item key="/calendar">
          <template #icon>
            <CalendarOutlined />
          </template>
          债券日历
        </a-menu-item>
        <a-menu-item key="/market">
          <template #icon>
            <StockOutlined />
          </template>
          聚合行情
        </a-menu-item>
        <a-menu-item key="/quote-board">
          <template #icon>
            <TableOutlined />
          </template>
          经纪商报价板
        </a-menu-item>
        <a-menu-item key="/history-replay">
          <template #icon>
            <HistoryOutlined />
          </template>
          历史行情回放
        </a-menu-item>
        <a-menu-item key="/trades">
          <template #icon>
            <SwapOutlined />
          </template>
          成交记录
        </a-menu-item>
        <a-menu-item key="/futures">
          <template #icon>
            <FundOutlined />
          </template>
          国债期货
        </a-menu-item>
        <a-menu-item key="/swaps">
          <template #icon>
            <TransactionOutlined />
          </template>
          收益互换
        </a-menu-item>
        <a-menu-item key="/research">
          <template #icon>
            <FileTextOutlined />
          </template>
          研报摘要
        </a-menu-item>
        <a-menu-item key="/favorites">
          <template #icon>
            <StarOutlined />
          </template>
          我的关注
        </a-menu-item>
        <a-sub-menu v-if="authStore.isAdmin()" key="admin">
          <template #icon>
            <SettingOutlined />
          </template>
          <template #title>系统管理</template>
          <a-menu-item key="/admin/users">用户管理</a-menu-item>
          <a-menu-item key="/admin/sources">行情源管理</a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="app-header flex items-center justify-between px-6 bg-white border-b border-gray-200">
        <div class="flex items-center gap-2">
          <a-button
            type="text"
            size="small"
            class="header-action-btn"
            @click="handleOpenSearch"
          >
            <template #icon>
              <SearchOutlined />
            </template>
            <span class="hidden md:inline">搜索</span>
            <kbd class="header-kbd hidden md:inline">Ctrl K</kbd>
          </a-button>
        </div>
        <div class="flex items-center gap-2">
          <a-button
            type="text"
            size="small"
            class="header-action-btn"
            @click="handleOpenCheatsheet"
          >
            <template #icon>
              <QuestionCircleOutlined />
            </template>
            <span class="hidden md:inline">快捷键</span>
            <kbd class="header-kbd hidden md:inline">?</kbd>
          </a-button>
          <span class="text-gray-600 ml-2">{{ authStore.user?.display_name || authStore.user?.username }}</span>
          <a-tag :color="roleColor">{{ roleLabel }}</a-tag>
          <a-button type="text" danger size="small" @click="handleLogout">
            退出
          </a-button>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content p-6 bg-gray-50">
        <router-view />
      </a-layout-content>
    </a-layout>
    <HotkeyCheatsheet />
    <GlobalSearch />
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  CalendarOutlined,
  StockOutlined,
  SwapOutlined,
  FundOutlined,
  TransactionOutlined,
  StarOutlined,
  SettingOutlined,
  FileTextOutlined,
  TableOutlined,
  HistoryOutlined,
  SearchOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { useHotkeysStore } from '../../stores/hotkeys'
import { useHotkeys } from '../../composables/useHotkeys'
import HotkeyCheatsheet from '../common/HotkeyCheatsheet.vue'
import GlobalSearch from '../common/GlobalSearch.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const hotkeysStore = useHotkeysStore()

useHotkeys()

const collapsed = ref(false)
const selectedKeys = ref<string[]>([route.path])

watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path]
    if (path.startsWith('/admin/')) {
      selectedKeys.value = [path]
    }
  },
  { immediate: true }
)

const roleLabel = computed(() => {
  const role = authStore.user?.role
  if (role === 'admin') return '管理员'
  if (role === 'trader') return '交易员'
  return role || '用户'
})

const roleColor = computed(() => {
  const role = authStore.user?.role
  if (role === 'admin') return 'red'
  if (role === 'trader') return 'blue'
  return 'default'
})

function handleMenuClick({ key }: { key: string }) {
  router.push(key)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function handleOpenCheatsheet() {
  hotkeysStore.openCheatsheet()
}

function handleOpenSearch() {
  hotkeysStore.openSearch()
}
</script>

<style scoped>
.app-layout :deep(.ant-layout-sider) {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
}

.app-menu :deep(.ant-menu) {
  background: transparent !important;
}

.app-menu :deep(.ant-menu-item),
.app-menu :deep(.ant-menu-submenu-title) {
  color: rgba(255, 255, 255, 0.85);
}

.app-menu :deep(.ant-menu-item-selected) {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
}

.app-menu :deep(.ant-menu-item:hover),
.app-menu :deep(.ant-menu-submenu-title:hover) {
  color: #fff !important;
}

.app-header {
  height: 56px;
  line-height: 56px;
}

.header-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
}

.header-action-btn:hover {
  background: #f5f5f5;
}

.header-kbd {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #6b7280;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-bottom-width: 2px;
  border-radius: 3px;
}
</style>
