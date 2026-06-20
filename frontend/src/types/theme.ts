export type ThemeMode = 'dark' | 'light' | 'high-contrast'

export interface ThemePalette {
  primary: string
  primaryHover: string
  primaryActive: string
  secondary: string
  success: string
  warning: string
  danger: string
  info: string
}

export interface ThemeColors {
  siderBg: string
  siderBgStart: string
  siderBgEnd: string
  siderMenuText: string
  siderMenuTextActive: string
  siderMenuBgActive: string
  siderMenuBgHover: string
  headerBg: string
  headerText: string
  headerBorder: string
  contentBg: string
  cardBg: string
  cardBorder: string
  textPrimary: string
  textSecondary: string
  textTertiary: string
  textDisabled: string
  border: string
  borderSecondary: string
  divider: string
  tableHeaderBg: string
  tableRowBg: string
  tableRowBgAlt: string
  tableHoverBg: string
  scrollbarThumb: string
  scrollbarTrack: string
  profitColor: string
  lossColor: string
  palette: ThemePalette
  chart: {
    line: string
    areaStart: string
    areaEnd: string
    grid: string
    axis: string
    tooltipBg: string
    tooltipText: string
    series: string[]
  }
}

export interface ThemeConfig {
  id: ThemeMode
  name: string
  description: string
  icon: string
  colors: ThemeColors
  preview: {
    sider: string
    header: string
    content: string
    card: string
    accent: string
  }
}

export interface ThemeSettings {
  currentTheme: ThemeMode
  defaultTheme: ThemeMode
}
