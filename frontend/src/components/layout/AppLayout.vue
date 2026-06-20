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
        <a-menu-item key="/rating-changes">
          <template #icon>
            <RiseOutlined />
          </template>
          评级变动
        </a-menu-item>
        <a-menu-item key="/favorites">
          <template #icon>
            <StarOutlined />
          </template>
          我的关注
        </a-menu-item>
        <a-menu-item key="/holdings">
          <template #icon>
            <WalletOutlined />
          </template>
          模拟持仓
        </a-menu-item>
        <a-menu-item key="/settings/appearance">
          <template #icon>
            <BgColorsOutlined />
          </template>
          外观设置
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
          <ThemeSwitcher />
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
          <span class="ml-2" :style="{ color: 'var(--theme-text-secondary)' }">
            {{ authStore.user?.display_name || authStore.user?.username }}
          </span>
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
  BgColorsOutlined,
  RiseOutlined,
  WalletOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { useHotkeysStore } from '../../stores/hotkeys'
import { useHotkeys } from '../../composables/useHotkeys'
import HotkeyCheatsheet from '../common/HotkeyCheatsheet.vue'
import GlobalSearch from '../common/GlobalSearch.vue'
import ThemeSwitcher from '../common/ThemeSwitcher.vue'

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
  background: linear-gradient(180deg, var(--theme-sider-bg-start) 0%, var(--theme-sider-bg-start) 50%, var(--theme-sider-bg-end) 100%) !important;
}

.app-menu :deep(.ant-menu) {
  background: transparent !important;
}

.app-menu :deep(.ant-menu-item),
.app-menu :deep(.ant-menu-submenu-title) {
  color: var(--theme-sider-menu-text);
}

.app-menu :deep(.ant-menu-item-selected) {
  background: var(--theme-sider-menu-bg-active) !important;
  color: var(--theme-sider-menu-text-active) !important;
}

.app-menu :deep(.ant-menu-item:hover),
.app-menu :deep(.ant-menu-submenu-title:hover) {
  color: var(--theme-sider-menu-text-active) !important;
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
  background: var(--theme-table-hover-bg);
}

.header-kbd {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: var(--theme-text-tertiary);
  background: var(--theme-table-row-bg-alt);
  border: 1px solid var(--theme-border-secondary);
  border-bottom-width: 2px;
  border-radius: 3px;
}
</style>
