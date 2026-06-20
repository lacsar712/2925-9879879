<template>
  <div class="appearance-settings p-6">
    <a-card title="外观设置" class="mb-6 rounded-lg">
      <p class="text-sm mb-0" :style="{ color: 'var(--theme-text-secondary)' }">
        选择您偏好的界面主题，设置将同时保存到本地与账户中。
      </p>
    </a-card>

    <a-card title="主题选择" class="mb-6 rounded-lg">
      <a-row :gutter="[20, 20]">
        <a-col :xs="24" :sm="12" :lg="8" v-for="theme in themeList" :key="theme.id">
          <div
            class="theme-card p-4 rounded-lg cursor-pointer border-2 transition-all duration-200"
            :class="{ 'theme-card-selected': currentTheme === theme.id }"
            @click="handleSelectTheme(theme.id)"
          >
            <div
              class="theme-preview h-44 rounded-lg overflow-hidden mb-4 border"
              :style="{ borderColor: theme.colors.border }"
            >
              <div class="flex h-full">
                <div
                  class="w-1/4 h-full"
                  :style="{ background: theme.preview.sider }"
                >
                  <div class="p-2 space-y-2">
                    <div
                      class="h-3 rounded"
                      :style="{ background: theme.colors.siderMenuBgActive }"
                    ></div>
                    <div
                      class="h-2 rounded w-3/4"
                      :style="{ background: theme.colors.siderMenuBgHover }"
                    ></div>
                    <div
                      class="h-2 rounded w-4/5"
                      :style="{ background: 'rgba(255,255,255,0.1)' }"
                    ></div>
                    <div
                      class="h-2 rounded w-2/3"
                      :style="{ background: 'rgba(255,255,255,0.1)' }"
                    ></div>
                  </div>
                </div>
                <div class="w-3/4 flex flex-col">
                  <div
                    class="h-8 px-3 flex items-center justify-between border-b"
                    :style="{
                      background: theme.preview.header,
                      borderColor: theme.colors.headerBorder
                    }"
                  >
                    <div class="flex gap-1.5">
                      <div
                        class="w-2 h-2 rounded-full"
                        :style="{ background: theme.colors.palette.danger }"
                      ></div>
                      <div
                        class="w-2 h-2 rounded-full"
                        :style="{ background: theme.colors.palette.warning }"
                      ></div>
                      <div
                        class="w-2 h-2 rounded-full"
                        :style="{ background: theme.colors.palette.success }"
                      ></div>
                    </div>
                    <div
                      class="w-6 h-2 rounded"
                      :style="{ background: theme.preview.accent, opacity: 0.6 }"
                    ></div>
                  </div>
                  <div
                    class="flex-1 p-2 space-y-2"
                    :style="{ background: theme.preview.content }"
                  >
                    <div
                      class="h-full rounded p-2 flex flex-col gap-2"
                      :style="{
                        background: theme.preview.card,
                        border: `1px solid ${theme.colors.cardBorder}`
                      }"
                    >
                      <div
                        class="h-3 rounded w-1/3"
                        :style="{ background: theme.colors.textPrimary, opacity: 0.85 }"
                      ></div>
                      <div class="grid grid-cols-2 gap-2 flex-1">
                        <div
                          class="rounded"
                          :style="{ background: theme.colors.chart.areaStart }"
                        >
                          <div
                            class="h-full flex items-end justify-center p-1"
                          >
                            <div
                              class="w-full"
                              :style="{
                                height: '60%',
                                background: `linear-gradient(180deg, ${theme.colors.chart.line} 0%, transparent 100%)`,
                                borderRadius: '2px'
                              }"
                            ></div>
                          </div>
                        </div>
                        <div class="flex flex-col gap-1 justify-center">
                          <div
                            class="h-1.5 rounded"
                            :style="{ background: theme.colors.tableHeaderBg }"
                          ></div>
                          <div
                            class="h-1.5 rounded w-5/6"
                            :style="{ background: theme.colors.tableRowBgAlt }"
                          ></div>
                          <div
                            class="h-1.5 rounded w-4/6"
                            :style="{ background: theme.colors.tableRowBgAlt }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <component :is="getThemeIcon(theme.icon)" class="text-lg" />
                <span class="font-semibold text-base">{{ theme.name }}</span>
                <CheckOutlined
                  v-if="currentTheme === theme.id"
                  class="text-green-500 text-lg"
                />
              </div>
              <a-tag
                v-if="defaultTheme === theme.id"
                color="blue"
                class="text-xs"
              >
                默认
              </a-tag>
            </div>
            <p
              class="text-sm mb-3 leading-relaxed"
              :style="{ color: theme.colors.textSecondary }"
            >
              {{ theme.description }}
            </p>

            <div class="flex gap-2">
              <a-button
                type="primary"
                size="small"
                block
                @click.stop="handleApplyTheme(theme.id)"
              >
                <template v-if="currentTheme === theme.id">
                  <template #icon><CheckOutlined /></template>
                  正在使用
                </template>
                <template v-else>
                  <template #icon><ThunderboltOutlined /></template>
                  应用主题
                </template>
              </a-button>
              <a-button
                size="small"
                @click.stop="handleSetDefault(theme.id)"
                :disabled="defaultTheme === theme.id"
              >
                <template #icon v-if="defaultTheme === theme.id"><CheckOutlined /></template>
                <template #icon-else><StarOutlined /></template>
                {{ defaultTheme === theme.id ? '已设默认' : '设为默认' }}
              </a-button>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <a-row :gutter="[20, 20]">
      <a-col :xs="24" :lg="14">
        <a-card title="当前主题色板" class="rounded-lg h-full">
          <div class="space-y-4">
            <div>
              <h4 class="text-sm font-medium mb-2">主色调</h4>
              <div class="grid grid-cols-3 gap-2">
                <ColorSwatch
                  label="主色"
                  :color="currentThemeConfig.colors.palette.primary"
                  :text-color="'#fff'"
                />
                <ColorSwatch
                  label="悬停"
                  :color="currentThemeConfig.colors.palette.primaryHover"
                  :text-color="'#fff'"
                />
                <ColorSwatch
                  label="激活"
                  :color="currentThemeConfig.colors.palette.primaryActive"
                  :text-color="'#fff'"
                />
              </div>
            </div>
            <div>
              <h4 class="text-sm font-medium mb-2">语义色</h4>
              <div class="grid grid-cols-4 gap-2">
                <ColorSwatch
                  label="成功"
                  :color="currentThemeConfig.colors.palette.success"
                  :text-color="'#fff'"
                />
                <ColorSwatch
                  label="警告"
                  :color="currentThemeConfig.colors.palette.warning"
                  :text-color="'#000'"
                />
                <ColorSwatch
                  label="错误"
                  :color="currentThemeConfig.colors.palette.danger"
                  :text-color="'#fff'"
                />
                <ColorSwatch
                  label="信息"
                  :color="currentThemeConfig.colors.palette.info"
                  :text-color="'#fff'"
                />
              </div>
            </div>
            <div>
              <h4 class="text-sm font-medium mb-2">图表系列色</h4>
              <div class="flex flex-wrap gap-2">
                <ColorSwatch
                  v-for="(color, idx) in currentThemeConfig.colors.chart.series.slice(0, 8)"
                  :key="idx"
                  :label="`S${idx + 1}`"
                  :color="color"
                  :text-color="'#fff'"
                  class="!h-10 !min-w-[60px]"
                />
              </div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :lg="10">
        <a-card title="操作提示" class="rounded-lg h-full">
          <a-alert
            type="info"
            show-icon
            class="mb-4"
            :message="'切换方式'"
            :description="'您也可以直接在顶栏点击主题按钮，下拉快速切换。'"
          />
          <a-alert
            type="success"
            show-icon
            class="mb-4"
            :message="'自动保存'"
            :description="'主题偏好将同时保存到本地浏览器与您的账户设置中。'"
          />
          <a-alert
            type="warning"
            show-icon
            :message="'高对比度模式'"
            :description="'高对比度模式适用于视力敏感用户，界面元素将使用强对比色。'"
          />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import {
  MoonOutlined,
  SunOutlined,
  EyeOutlined,
  CheckOutlined,
  StarOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons-vue'
import { useTheme } from '../../composables/useTheme'
import type { ThemeMode } from '../../types/theme'
import ColorSwatch from './components/ColorSwatch.vue'

const {
  currentTheme,
  defaultTheme,
  currentThemeConfig,
  themeList,
  changeTheme,
  setAsDefault,
} = useTheme()

const iconMap: Record<string, any> = {
  MoonOutlined,
  SunOutlined,
  EyeOutlined,
}

function getThemeIcon(iconName: string) {
  return iconMap[iconName] || MoonOutlined
}

function handleSelectTheme(mode: ThemeMode) {
  changeTheme(mode)
}

function handleApplyTheme(mode: ThemeMode) {
  changeTheme(mode)
}

function handleSetDefault(mode: ThemeMode) {
  setAsDefault(mode)
}
</script>

<style scoped>
.theme-card {
  border-color: var(--theme-border-secondary);
  background: var(--theme-card-bg);
}

.theme-card:hover {
  border-color: var(--theme-palette-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.theme-card-selected {
  border-color: var(--theme-palette-primary) !important;
  background: color-mix(in srgb, var(--theme-palette-primary) 5%, var(--theme-card-bg));
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--theme-palette-primary) 20%, transparent);
}
</style>
