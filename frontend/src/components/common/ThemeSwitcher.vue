<template>
  <a-dropdown :trigger="['click']" placement="bottomRight">
    <a-button
      type="text"
      size="small"
      class="header-action-btn theme-toggle-btn"
    >
      <template #icon>
        <component :is="currentIcon" />
      </template>
      <span class="hidden md:inline">{{ currentThemeConfig.name }}</span>
    </a-button>
    <template #overlay>
      <a-menu class="theme-dropdown-menu" @click="handleMenuClick">
        <div class="theme-dropdown-header px-4 py-2 border-b border-gray-200">
          <span class="text-sm font-medium" :style="{ color: 'var(--theme-text-primary)' }">切换主题</span>
        </div>
        <a-menu-item
          v-for="theme in themeList"
          :key="theme.id"
          class="theme-dropdown-item"
          :class="{ 'theme-item-selected': currentTheme === theme.id }"
        >
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center gap-3">
              <div class="theme-preview-mini w-10 h-10 rounded overflow-hidden border"
                   :style="{ borderColor: 'var(--theme-border)' }">
                <div class="flex h-full">
                  <div class="w-2/5 h-full" :style="{ background: theme.preview.sider }"></div>
                  <div class="w-3/5 flex flex-col">
                    <div class="h-1/4" :style="{ background: theme.preview.header }"></div>
                    <div class="flex-1 p-1" :style="{ background: theme.preview.content }">
                      <div class="w-full h-full rounded-sm" :style="{ background: theme.preview.card }"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-start">
                <div class="flex items-center gap-2">
                  <component :is="getThemeIcon(theme.icon)" class="text-sm" />
                  <span class="text-sm font-medium">{{ theme.name }}</span>
                  <CheckOutlined
                    v-if="currentTheme === theme.id"
                    class="text-green-500 text-sm"
                  />
                </div>
                <span class="text-xs mt-0.5" :style="{ color: 'var(--theme-text-tertiary)' }">
                  {{ theme.description }}
                </span>
              </div>
            </div>
          </div>
        </a-menu-item>
        <a-menu-divider />
        <a-menu-item key="settings" @click="goToSettings">
          <div class="flex items-center gap-2">
            <SettingOutlined />
            <span class="text-sm">外观设置</span>
          </div>
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  MoonOutlined,
  SunOutlined,
  EyeOutlined,
  CheckOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'
import { useTheme } from '../../composables/useTheme'
import type { ThemeMode } from '../../types/theme'

const router = useRouter()
const { currentTheme, currentThemeConfig, themeList, changeTheme } = useTheme()

const iconMap: Record<string, any> = {
  MoonOutlined,
  SunOutlined,
  EyeOutlined,
}

const currentIcon = computed(() => iconMap[currentThemeConfig.value.icon] || MoonOutlined)

function getThemeIcon(iconName: string) {
  return iconMap[iconName] || MoonOutlined
}

function handleMenuClick({ key }: { key: string }) {
  if (key === 'settings') return
  changeTheme(key as ThemeMode)
}

function goToSettings() {
  router.push('/settings/appearance')
}
</script>

<style scoped>
.theme-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
}

.theme-toggle-btn:hover {
  background: var(--theme-table-hover-bg) !important;
}

.theme-dropdown-menu {
  min-width: 280px;
  padding: 0;
  background: var(--theme-card-bg) !important;
  border: 1px solid var(--theme-card-border) !important;
}

.theme-dropdown-menu :deep(.ant-dropdown-menu) {
  padding: 0;
}

.theme-dropdown-menu :deep(.ant-dropdown-menu-item) {
  padding: 10px 16px;
}

.theme-dropdown-menu :deep(.ant-dropdown-menu-item:hover) {
  background: var(--theme-table-hover-bg) !important;
}

.theme-item-selected {
  background: color-mix(in srgb, var(--theme-palette-primary) 10%, transparent) !important;
}

.theme-dropdown-header {
  border-bottom: 1px solid var(--theme-divider);
}
</style>
