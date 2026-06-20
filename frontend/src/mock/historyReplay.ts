import dayjs from 'dayjs'

export interface BondInfo {
  bond_id: string
  code: string
  name: string
  bond_type: string
  coupon_rate?: number
  remaining_term?: string
  credit_rating?: string
}

export interface SourceInfo {
  source_id: string
  name: string
  source_type: string
}

export interface QuoteCell {
  bid_price?: number
  ask_price?: number
  bid_volume?: number
  ask_volume?: number
  quote_time?: string
}

export interface TradeRecord {
  trade_id: string
  price: number
  volume: number
  direction: 'buy' | 'sell'
  trade_time: string
  source: string
}

export interface QuoteSnapshot {
  snapshot_id: string
  snapshot_time: string
  bond: BondInfo
  sources: SourceInfo[]
  quotes: Record<string, QuoteCell | undefined>
  trades: TradeRecord[]
}

export interface HistoryReplayData {
  bond: BondInfo
  snapshots: QuoteSnapshot[]
}

const hotBonds: BondInfo[] = [
  { bond_id: 'bond_001', code: '019695', name: '24附息国债02', bond_type: '国债', coupon_rate: 2.35, remaining_term: '9.8年', credit_rating: 'AAA' },
  { bond_id: 'bond_002', code: '019696', name: '24附息国债03', bond_type: '国债', coupon_rate: 2.45, remaining_term: '4.8年', credit_rating: 'AAA' },
  { bond_id: 'bond_003', code: '019700', name: '24附息国债05', bond_type: '国债', coupon_rate: 2.55, remaining_term: '2.8年', credit_rating: 'AAA' },
  { bond_id: 'bond_050', code: '240201', name: '24国开01', bond_type: '政金债', coupon_rate: 2.58, remaining_term: '9.7年', credit_rating: 'AAA' },
  { bond_id: 'bond_051', code: '240202', name: '24国开02', bond_type: '政金债', coupon_rate: 2.62, remaining_term: '4.7年', credit_rating: 'AAA' },
]

const sources: SourceInfo[] = [
  { source_id: 'src_001', name: '中诚宝捷', source_type: 'broker' },
  { source_id: 'src_002', name: '国际货币', source_type: 'broker' },
  { source_id: 'src_003', name: '平安利顺', source_type: 'broker' },
  { source_id: 'src_004', name: 'xBond', source_type: 'xbond' },
  { source_id: 'src_005', name: '上交所', source_type: 'exchange' },
]

function generateSnapshotsForBond(bond: BondInfo, startTime: string, count: number, intervalMinutes: number): QuoteSnapshot[] {
  const snapshots: QuoteSnapshot[] = []
  const baseTime = dayjs(startTime)
  
  for (let i = 0; i < count; i++) {
    const snapshotTime = baseTime.add(i * intervalMinutes, 'minute')
    const basePrice = bond.bond_type === '国债' ? 100 + Math.random() * 2 : 99 + Math.random() * 3
    
    const quotes: Record<string, QuoteCell | undefined> = {}
    sources.forEach((source, idx) => {
      const variance = (Math.random() - 0.5) * 0.3
      const hasQuote = Math.random() > 0.15
      
      if (hasQuote) {
        const bidPrice = basePrice + variance - 0.05 - idx * 0.01
        const askPrice = basePrice + variance + 0.05 + idx * 0.01
        quotes[source.source_id] = {
          bid_price: Math.round(bidPrice * 10000) / 10000,
          ask_price: Math.round(askPrice * 10000) / 10000,
          bid_volume: Math.floor(Math.random() * 5000 + 1000),
          ask_volume: Math.floor(Math.random() * 5000 + 1000),
          quote_time: snapshotTime.subtract(Math.floor(Math.random() * 60), 'second').format('YYYY-MM-DD HH:mm:ss'),
        }
      }
    })
    
    const trades: TradeRecord[] = []
    const tradeCount = Math.floor(Math.random() * 5)
    for (let j = 0; j < tradeCount; j++) {
      const tradeSource = sources[Math.floor(Math.random() * sources.length)]
      const tradeVariance = (Math.random() - 0.5) * 0.2
      trades.push({
        trade_id: `tr_${i}_${j}`,
        price: Math.round((basePrice + tradeVariance) * 10000) / 10000,
        volume: Math.floor(Math.random() * 2000 + 500),
        direction: Math.random() > 0.5 ? 'buy' : 'sell',
        trade_time: snapshotTime.subtract(Math.floor(Math.random() * intervalMinutes * 60), 'second').format('YYYY-MM-DD HH:mm:ss'),
        source: tradeSource.name,
      })
    }
    
    snapshots.push({
      snapshot_id: `snap_${bond.bond_id}_${i}`,
      snapshot_time: snapshotTime.format('YYYY-MM-DD HH:mm:ss'),
      bond,
      sources,
      quotes,
      trades,
    })
  }
  
  return snapshots
}

export const hotBondHistoryData: HistoryReplayData[] = hotBonds.map((bond) => ({
  bond,
  snapshots: generateSnapshotsForBond(bond, '2024-06-20 09:30:00', 12, 15),
}))

export function getHistoryReplayData(bondId: string): HistoryReplayData | undefined {
  return hotBondHistoryData.find((d) => d.bond.bond_id === bondId)
}

export function getHotBonds(): BondInfo[] {
  return hotBonds
}

export function getAllHistoryData(): HistoryReplayData[] {
  return hotBondHistoryData
}

export interface QuoteDiff {
  bid_price_diff?: number
  ask_price_diff?: number
  bid_price_change?: 'up' | 'down' | 'unchanged'
  ask_price_change?: 'up' | 'down' | 'unchanged'
}

export function calculateSnapshotDiff(
  current: QuoteSnapshot,
  previous: QuoteSnapshot | undefined
): Record<string, QuoteDiff> {
  if (!previous) return {}
  
  const diff: Record<string, QuoteDiff> = {}
  
  current.sources.forEach((source) => {
    const currentQuote = current.quotes[source.source_id]
    const previousQuote = previous.quotes[source.source_id]
    
    if (currentQuote && previousQuote) {
      const bidDiff = currentQuote.bid_price !== undefined && previousQuote.bid_price !== undefined
        ? currentQuote.bid_price - previousQuote.bid_price
        : undefined
      const askDiff = currentQuote.ask_price !== undefined && previousQuote.ask_price !== undefined
        ? currentQuote.ask_price - previousQuote.ask_price
        : undefined
      
      diff[source.source_id] = {
        bid_price_diff: bidDiff,
        ask_price_diff: askDiff,
        bid_price_change: bidDiff !== undefined
          ? bidDiff > 0 ? 'up' : bidDiff < 0 ? 'down' : 'unchanged'
          : undefined,
        ask_price_change: askDiff !== undefined
          ? askDiff > 0 ? 'up' : askDiff < 0 ? 'down' : 'unchanged'
          : undefined,
      }
    }
  })
  
  return diff
}
