import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '../stores/theme'
import type { ThemeMode } from '../types/theme'

export function useTheme() {
  const themeStore = useThemeStore()
  const { currentTheme, defaultTheme, currentThemeConfig, themeList } = storeToRefs(themeStore)

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
    currentTheme,
    defaultTheme,
    currentThemeConfig,
    themeList,
    changeTheme,
    cycleTheme,
    resetToDefault,
    setAsDefault,
    init,
    getChartColors,
  }
}
