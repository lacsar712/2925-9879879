export type HotkeyCategory = 'search' | 'navigation' | 'help' | 'action'

export interface HotkeyItem {
  id: string
  keys: string[]
  description: string
  category: HotkeyCategory
  route?: string
  sequence?: string[]
  pauseOnInput?: boolean
}

export const HOTKEY_LIST: HotkeyItem[] = [
  {
    id: 'global-search',
    keys: ['ctrl', 'k'],
    description: '唤起全局搜索',
    category: 'search',
    pauseOnInput: false,
  },
  {
    id: 'go-dashboard',
    keys: ['g', 'd'],
    description: '跳转行情看板',
    category: 'navigation',
    route: '/dashboard',
    sequence: ['g', 'd'],
    pauseOnInput: true,
  },
  {
    id: 'go-market',
    keys: ['g', 'm'],
    description: '跳转聚合行情',
    category: 'navigation',
    route: '/market',
    sequence: ['g', 'm'],
    pauseOnInput: true,
  },
  {
    id: 'go-calendar',
    keys: ['g', 'c'],
    description: '跳转债券日历',
    category: 'navigation',
    route: '/calendar',
    sequence: ['g', 'c'],
    pauseOnInput: true,
  },
  {
    id: 'go-quote-board',
    keys: ['g', 'q'],
    description: '跳转经纪商报价板',
    category: 'navigation',
    route: '/quote-board',
    sequence: ['g', 'q'],
    pauseOnInput: true,
  },
  {
    id: 'go-history-replay',
    keys: ['g', 'h'],
    description: '跳转历史行情回放',
    category: 'navigation',
    route: '/history-replay',
    sequence: ['g', 'h'],
    pauseOnInput: true,
  },
  {
    id: 'go-trades',
    keys: ['g', 't'],
    description: '跳转成交记录',
    category: 'navigation',
    route: '/trades',
    sequence: ['g', 't'],
    pauseOnInput: true,
  },
  {
    id: 'go-research',
    keys: ['g', 'r'],
    description: '跳转研报摘要',
    category: 'navigation',
    route: '/research',
    sequence: ['g', 'r'],
    pauseOnInput: true,
  },
  {
    id: 'go-favorites',
    keys: ['g', 'f'],
    description: '跳转我的关注',
    category: 'navigation',
    route: '/favorites',
    sequence: ['g', 'f'],
    pauseOnInput: true,
  },
  {
    id: 'show-cheatsheet',
    keys: ['?'],
    description: '显示快捷键速查面板',
    category: 'help',
    pauseOnInput: false,
  },
]

export const CATEGORY_LABELS: Record<HotkeyCategory, string> = {
  search: '搜索',
  navigation: '导航',
  help: '帮助',
  action: '操作',
}

export function normalizeKey(e: KeyboardEvent): string {
  const key = e.key.toLowerCase()
  if (key === 'control') return 'ctrl'
  if (key === 'meta') return 'ctrl'
  if (key === ' ') return 'space'
  return key
}

export function isInputElement(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false
  const tag = target.tagName.toLowerCase()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return true
  if (target.isContentEditable) return true
  return false
}

export function formatKeyDisplay(key: string): string {
  const map: Record<string, string> = {
    ctrl: 'Ctrl',
    alt: 'Alt',
    shift: 'Shift',
    meta: '⌘',
    space: 'Space',
    escape: 'Esc',
    enter: 'Enter',
    arrowup: '↑',
    arrowdown: '↓',
    arrowleft: '←',
    arrowright: '→',
  }
  const k = key.toLowerCase()
  return map[k] || key.toUpperCase()
}
