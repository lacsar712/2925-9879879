import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ThemeMode, ThemeConfig, ThemeSettings } from '../types/theme'
import { THEMES, THEME_LIST, DEFAULT_THEME } from '../config/themes'
import api from '../api'
import { useAuthStore } from './auth'

const STORAGE_KEY = 'bondview_theme_settings'
const USER_SETTINGS_KEY = 'bondview_user_theme'

export const useThemeStore = defineStore('theme', () => {
  const authStore = useAuthStore()

  const currentTheme = ref<ThemeMode>(DEFAULT_THEME)
  const defaultTheme = ref<ThemeMode>(DEFAULT_THEME)

  function loadSettingsFromStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const settings: ThemeSettings = JSON.parse(saved)
        if (settings.currentTheme && THEMES[settings.currentTheme]) {
          currentTheme.value = settings.currentTheme
        }
        if (settings.defaultTheme && THEMES[settings.defaultTheme]) {
          defaultTheme.value = settings.defaultTheme
        }
      } else {
        const userTheme = localStorage.getItem(USER_SETTINGS_KEY) as ThemeMode | null
        if (userTheme && THEMES[userTheme]) {
          currentTheme.value = userTheme
          defaultTheme.value = userTheme
        }
      }
    } catch {
      currentTheme.value = DEFAULT_THEME
      defaultTheme.value = DEFAULT_THEME
    }
  }

  function saveToStorage() {
    const settings: ThemeSettings = {
      currentTheme: currentTheme.value,
      defaultTheme: defaultTheme.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
    localStorage.setItem(USER_SETTINGS_KEY, currentTheme.value)
  }

  async function saveToAccount(mode: ThemeMode) {
    if (!authStore.token) return
    try {
      await api.put('/api/user/settings', { theme: mode })
    } catch {
    }
  }

  async function loadFromAccount() {
    if (!authStore.token) return
    try {
      const res = await api.get('/api/user/settings')
      if (res.data?.theme && THEMES[res.data.theme as ThemeMode]) {
        const serverTheme = res.data.theme as ThemeMode
        currentTheme.value = serverTheme
        defaultTheme.value = serverTheme
        saveToStorage()
      }
    } catch {
    }
  }

  const currentThemeConfig = computed<ThemeConfig>(() => THEMES[currentTheme.value])
  const themeList = computed(() => THEME_LIST)

  function setTheme(mode: ThemeMode, persistToAccount = true) {
    if (!THEMES[mode]) return
    currentTheme.value = mode
    saveToStorage()
    applyThemeToDOM()
    if (persistToAccount) {
      saveToAccount(mode)
    }
  }

  function setDefaultTheme(mode: ThemeMode) {
    if (!THEMES[mode]) return
    defaultTheme.value = mode
    saveToStorage()
    saveToAccount(mode)
  }

  function applyThemeToDOM() {
    const theme = currentThemeConfig.value.colors
    const root = document.documentElement

    root.style.setProperty('--theme-sider-bg', theme.siderBg)
    root.style.setProperty('--theme-sider-bg-start', theme.siderBgStart)
    root.style.setProperty('--theme-sider-bg-end', theme.siderBgEnd)
    root.style.setProperty('--theme-sider-menu-text', theme.siderMenuText)
    root.style.setProperty('--theme-sider-menu-text-active', theme.siderMenuTextActive)
    root.style.setProperty('--theme-sider-menu-bg-active', theme.siderMenuBgActive)
    root.style.setProperty('--theme-sider-menu-bg-hover', theme.siderMenuBgHover)
    root.style.setProperty('--theme-header-bg', theme.headerBg)
    root.style.setProperty('--theme-header-text', theme.headerText)
    root.style.setProperty('--theme-header-border', theme.headerBorder)
    root.style.setProperty('--theme-content-bg', theme.contentBg)
    root.style.setProperty('--theme-card-bg', theme.cardBg)
    root.style.setProperty('--theme-card-border', theme.cardBorder)
    root.style.setProperty('--theme-text-primary', theme.textPrimary)
    root.style.setProperty('--theme-text-secondary', theme.textSecondary)
    root.style.setProperty('--theme-text-tertiary', theme.textTertiary)
    root.style.setProperty('--theme-text-disabled', theme.textDisabled)
    root.style.setProperty('--theme-border', theme.border)
    root.style.setProperty('--theme-border-secondary', theme.borderSecondary)
    root.style.setProperty('--theme-divider', theme.divider)
    root.style.setProperty('--theme-table-header-bg', theme.tableHeaderBg)
    root.style.setProperty('--theme-table-row-bg', theme.tableRowBg)
    root.style.setProperty('--theme-table-row-bg-alt', theme.tableRowBgAlt)
    root.style.setProperty('--theme-table-hover-bg', theme.tableHoverBg)
    root.style.setProperty('--theme-scrollbar-thumb', theme.scrollbarThumb)
    root.style.setProperty('--theme-scrollbar-track', theme.scrollbarTrack)
    root.style.setProperty('--theme-profit-color', theme.profitColor)
    root.style.setProperty('--theme-loss-color', theme.lossColor)
    root.style.setProperty('--theme-palette-primary', theme.palette.primary)
    root.style.setProperty('--theme-palette-primary-hover', theme.palette.primaryHover)
    root.style.setProperty('--theme-palette-primary-active', theme.palette.primaryActive)
    root.style.setProperty('--theme-palette-success', theme.palette.success)
    root.style.setProperty('--theme-palette-warning', theme.palette.warning)
    root.style.setProperty('--theme-palette-danger', theme.palette.danger)
    root.style.setProperty('--theme-chart-line', theme.chart.line)
    root.style.setProperty('--theme-chart-area-start', theme.chart.areaStart)
    root.style.setProperty('--theme-chart-area-end', theme.chart.areaEnd)
    root.style.setProperty('--theme-chart-grid', theme.chart.grid)
    root.style.setProperty('--theme-chart-axis', theme.chart.axis)
    root.style.setProperty('--theme-chart-tooltip-bg', theme.chart.tooltipBg)
    root.style.setProperty('--theme-chart-tooltip-text', theme.chart.tooltipText)

    root.setAttribute('data-theme', currentTheme.value)
  }

  function initTheme() {
    loadSettingsFromStorage()
    applyThemeToDOM()
  }

  function resetTheme() {
    setTheme(defaultTheme.value)
  }

  function cycleTheme() {
    const modes: ThemeMode[] = ['dark', 'light', 'high-contrast']
    const currentIndex = modes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % modes.length
    setTheme(modes[nextIndex])
  }

  function getChartColors() {
    return currentThemeConfig.value.colors.chart
  }

  return {
    currentTheme,
    defaultTheme,
    currentThemeConfig,
    themeList,
    initTheme,
    setTheme,
    setDefaultTheme,
    applyThemeToDOM,
    resetTheme,
    cycleTheme,
    loadFromAccount,
    getChartColors,
  }
})
