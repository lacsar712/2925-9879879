<template>
  <a-config-provider :locale="zhCN" :theme="antdTheme">
    <router-view />
  </a-config-provider>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { theme as antd } from 'ant-design-vue'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
  themeStore.loadFromAccount()
})

const antdTheme = computed(() => {
  const colors = themeStore.currentThemeConfig.colors
  const isDark = themeStore.currentTheme === 'dark'
  const isHighContrast = themeStore.currentTheme === 'high-contrast'

  return {
    algorithm: isDark ? antd.darkAlgorithm : antd.defaultAlgorithm,
    token: {
      colorPrimary: colors.palette.primary,
      colorSuccess: colors.palette.success,
      colorWarning: colors.palette.warning,
      colorError: colors.palette.danger,
      colorInfo: colors.palette.primary,
      colorText: colors.textPrimary,
      colorTextSecondary: colors.textSecondary,
      colorTextTertiary: colors.textTertiary,
      colorTextQuaternary: colors.textDisabled,
      colorBgBase: colors.cardBg,
      colorBgContainer: colors.cardBg,
      colorBgElevated: colors.cardBg,
      colorBgLayout: colors.contentBg,
      colorBorder: colors.border,
      colorBorderSecondary: colors.borderSecondary,
      colorSplit: colors.divider,
      borderRadius: 6,
      colorLink: colors.palette.primary,
      colorLinkHover: colors.palette.primaryHover,
      colorLinkActive: colors.palette.primaryActive,
      fontWeightStrong: isHighContrast ? 600 : 600,
    },
    components: {
      Layout: {
        headerBg: colors.headerBg,
        headerColor: colors.headerText,
        headerHeight: 56,
        siderBg: colors.siderBg,
        bodyBg: colors.contentBg,
        triggerBg: colors.siderBg,
        zeroTriggerBg: colors.siderBg,
      },
      Menu: {
        darkItemBg: 'transparent',
        darkSubMenuItemBg: 'transparent',
        darkItemColor: colors.siderMenuText,
        darkItemSelectedColor: colors.siderMenuTextActive,
        darkItemSelectedBg: colors.siderMenuBgActive,
      },
      Table: {
        headerBg: colors.tableHeaderBg,
        headerColor: colors.textPrimary,
        rowHoverBg: colors.tableHoverBg,
        borderColor: colors.border,
      },
      Card: {
        background: colors.cardBg,
        headerBackground: 'transparent',
      },
      Modal: {
        headerBg: colors.cardBg,
        contentBg: colors.cardBg,
        footerBg: colors.cardBg,
      },
      Drawer: {
        headerBg: colors.cardBg,
        bodyBg: colors.cardBg,
        footerBg: colors.cardBg,
      },
    },
  }
})
</script>
