import { onMounted, watch } from 'vue'
import { useThemeStore } from '../stores/theme'
import type { ThemeMode } from '../types/theme'

export function useTheme() {
  const themeStore = useThemeStore()

  function changeTheme(mode: ThemeMode, persistToAccount = true) {
    themeStore.setTheme(mode, persistToAccount)
  }

  function cycleTheme() {
    themeStore.cycleTheme()
  }

  function resetToDefault() {
    themeStore.resetTheme()
  }

  function setAsDefault(mode: ThemeMode) {
    themeStore.setDefaultTheme(mode)
  }

  function init() {
    themeStore.initTheme()
    themeStore.loadFromAccount()
  }

  function getChartColors() {
    return themeStore.getChartColors()
  }

  onMounted(() => {
    init()
  })

  watch(
    () => themeStore.currentTheme,
    () => {
      themeStore.applyThemeToDOM()
    },
    { deep: false }
  )

  return {
    currentTheme: themeStore.currentTheme,
    defaultTheme: themeStore.defaultTheme,
    currentThemeConfig: themeStore.currentThemeConfig,
    themeList: themeStore.themeList,
    changeTheme,
    cycleTheme,
    resetToDefault,
    setAsDefault,
    init,
    getChartColors,
  }
}
