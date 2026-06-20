import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'

export interface Holding {
  id: string
  code: string
  name: string
  quantity: number
  costPrice: number
  buyDate: string
  modifiedDuration: number | null
}

export interface HoldingWithMarket extends Holding {
  latestPrice: number
  marketValue: number
  costValue: number
  floatingPnl: number
  floatingPnlRatio: number
  weight: number
  durationContribution: number
}

const STORAGE_KEY = 'bondview_simulated_holdings'

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function seededRandom(seed: string): number {
  let h = 0
  for (let i = 0; i < seed.length; i++) {
    h = (Math.imul(31, h) + seed.charCodeAt(i)) | 0
  }
  const x = Math.sin(h) * 10000
  return x - Math.floor(x)
}

function simulateLatestPrice(holding: Holding): number {
  const variation = (seededRandom(holding.code + dayjs().format('YYYY-MM-DD')) - 0.5) * 0.06
  return Math.round(holding.costPrice * (1 + variation) * 10000) / 10000
}

function estimateDuration(code: string): number | null {
  const match = code.match(/(\d+)/)
  if (!match) return null
  const yearPart = parseInt(match[1], 10)
  if (yearPart < 1) return null
  const years = yearPart > 100 ? (yearPart - new Date().getFullYear()) : yearPart
  if (years <= 0) return null
  return Math.round(years * 0.8 * 100) / 100
}

function loadFromStorage(): Holding[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    return JSON.parse(raw)
  } catch {
    return []
  }
}

function saveToStorage(items: Holding[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export const useHoldingsStore = defineStore('holdings', () => {
  const holdings = ref<Holding[]>(loadFromStorage())

  watch(holdings, (val) => saveToStorage(val), { deep: true })

  const holdingsWithMarket = computed<HoldingWithMarket[]>(() => {
    const totalMv = holdings.value.reduce((sum, h) => {
      const lp = simulateLatestPrice(h)
      return sum + lp * h.quantity
    }, 0)

    return holdings.value.map((h) => {
      const latestPrice = simulateLatestPrice(h)
      const marketValue = Math.round(latestPrice * h.quantity * 100) / 100
      const costValue = Math.round(h.costPrice * h.quantity * 100) / 100
      const floatingPnl = Math.round((marketValue - costValue) * 100) / 100
      const floatingPnlRatio = costValue !== 0 ? Math.round((floatingPnl / costValue) * 10000) / 100 : 0
      const weight = totalMv !== 0 ? marketValue / totalMv : 0
      const md = h.modifiedDuration ?? estimateDuration(h.code)
      const durationContribution = md !== null ? Math.round(weight * md * 10000) / 10000 : 0

      return {
        ...h,
        latestPrice,
        marketValue,
        costValue,
        floatingPnl,
        floatingPnlRatio,
        weight,
        durationContribution,
      }
    })
  })

  const totalMarketValue = computed(() =>
    holdingsWithMarket.value.reduce((s, h) => s + h.marketValue, 0)
  )

  const totalCostValue = computed(() =>
    holdingsWithMarket.value.reduce((s, h) => s + h.costValue, 0)
  )

  const totalFloatingPnl = computed(() =>
    Math.round((totalMarketValue.value - totalCostValue.value) * 100) / 100
  )

  const totalFloatingPnlRatio = computed(() => {
    if (totalCostValue.value === 0) return 0
    return Math.round((totalFloatingPnl.value / totalCostValue.value) * 10000) / 100
  })

  const portfolioDuration = computed(() =>
    Math.round(holdingsWithMarket.value.reduce((s, h) => s + h.durationContribution, 0) * 100) / 100
  )

  function addHolding(data: Omit<Holding, 'id'>) {
    holdings.value.push({ ...data, id: generateId() })
  }

  function updateHolding(id: string, data: Partial<Omit<Holding, 'id'>>) {
    const idx = holdings.value.findIndex((h) => h.id === id)
    if (idx !== -1) {
      holdings.value[idx] = { ...holdings.value[idx], ...data }
    }
  }

  function deleteHolding(id: string) {
    holdings.value = holdings.value.filter((h) => h.id !== id)
  }

  return {
    holdings,
    holdingsWithMarket,
    totalMarketValue,
    totalCostValue,
    totalFloatingPnl,
    totalFloatingPnlRatio,
    portfolioDuration,
    addHolding,
    updateHolding,
    deleteHolding,
  }
})
