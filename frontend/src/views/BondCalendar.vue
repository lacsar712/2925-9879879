<template>
  <div class="bond-calendar p-4">
    <a-card class="rounded-lg">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-4">
          <h2 class="text-lg font-semibold text-gray-800">债券日历</h2>
          <a-select
            v-model:value="selectedBondType"
            placeholder="债券品种"
            style="width: 140px"
            allow-clear
            @change="fetchMonthEvents"
          >
            <a-select-option v-for="t in bondTypes" :key="t" :value="t">
              {{ t }}
            </a-select-option>
          </a-select>
          <a-select
            v-model:value="selectedEventType"
            placeholder="事件类型"
            style="width: 140px"
            allow-clear
            @change="fetchMonthEvents"
          >
            <a-select-option value="issue">新发债</a-select-option>
            <a-select-option value="maturity">到期日</a-select-option>
          </a-select>
        </div>
        <div class="flex items-center gap-2">
          <a-button @click="goToPrevMonth">
            <template #icon><LeftOutlined /></template>
            上月
          </a-button>
          <span class="text-lg font-medium min-w-[140px] text-center">
            {{ currentYear }}年{{ currentMonth }}月
          </span>
          <a-button @click="goToNextMonth">
            下月
            <template #icon><RightOutlined /></template>
          </a-button>
          <a-button type="primary" ghost @click="goToToday">今天</a-button>
        </div>
      </div>

      <div class="legend flex items-center gap-6 mb-4 text-sm">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-green-500"></span>
          <span class="text-gray-600">新发债</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-red-500"></span>
          <span class="text-gray-600">到期日</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-blue-500"></span>
          <span class="text-gray-600">多事件</span>
        </div>
      </div>

      <div class="calendar-grid border border-gray-200 rounded-lg overflow-hidden">
        <div class="calendar-header grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          <div
            v-for="day in weekDays"
            :key="day"
            class="py-2 text-center text-sm font-medium text-gray-600"
          >
            {{ day }}
          </div>
        </div>
        <div class="calendar-body grid grid-cols-7">
          <div
            v-for="(day, idx) in calendarDays"
            :key="idx"
            class="calendar-day min-h-[100px] p-2 border-r border-b border-gray-100 cursor-pointer hover:bg-blue-50 transition-colors"
            :class="{
              'bg-gray-50': !day.isCurrentMonth,
              'bg-blue-50/50': day.isToday,
              'border-l-0': idx % 7 === 0,
            }"
            @click="handleDayClick(day)"
          >
            <div class="flex items-center justify-between mb-1">
              <span
                class="text-sm font-medium"
                :class="{
                  'text-gray-400': !day.isCurrentMonth,
                  'text-blue-600 font-bold': day.isToday,
                  'text-gray-700': day.isCurrentMonth && !day.isToday,
                }"
              >
                {{ day.date.date() }}
              </span>
              <span
                v-if="day.eventCount > 0"
                class="text-xs px-1.5 py-0.5 rounded-full text-white"
                :class="getDayBadgeClass(day)"
              >
                {{ day.eventCount }}
              </span>
            </div>
            <div class="event-dots flex flex-wrap gap-1">
              <span
                v-for="(evt, eIdx) in day.previewEvents"
                :key="eIdx"
                class="w-2 h-2 rounded-full"
                :class="getEventDotClass(evt.event_type)"
              ></span>
            </div>
            <div class="event-preview mt-1 space-y-0.5">
              <div
                v-for="(evt, eIdx) in day.previewEvents.slice(0, 2)"
                :key="eIdx"
                class="text-xs truncate text-gray-600"
              >
                <span
                  class="inline-block w-1.5 h-1.5 rounded-full mr-1 align-middle"
                  :class="getEventDotClass(evt.event_type)"
                ></span>
                {{ evt.bond_name }}
              </div>
              <div v-if="day.eventCount > 2" class="text-xs text-gray-400">
                等 {{ day.eventCount }} 条事件
              </div>
            </div>
          </div>
        </div>
      </div>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :footer="null"
      width="720px"
    >
      <div class="day-events-modal">
        <a-empty v-if="!dayEventsLoading && dayEvents.length === 0" description="当日暂无事件" />
        <div v-else class="space-y-4">
          <div v-for="group in groupedEvents" :key="group.type" class="event-group">
            <div class="flex items-center gap-2 mb-2">
              <span
                class="w-3 h-3 rounded-full"
                :class="getEventDotClass(group.type)"
              ></span>
              <span class="font-medium text-gray-700">{{ group.label }}</span>
              <a-tag color="default" class="ml-2">{{ group.events.length }} 只</a-tag>
            </div>
            <a-table
              :data-source="group.events"
              :pagination="false"
              :row-key="(r) => r.id"
              size="small"
              class="event-table"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'bond_code'">
                  <router-link
                    :to="`/market/${record.bond_id}`"
                    class="text-blue-600 hover:underline tabular-nums"
                    @click="modalVisible = false"
                  >
                    {{ record.bond_code }}
                  </router-link>
                </template>
                <template v-else-if="column.key === 'bond_name'">
                  <router-link
                    :to="`/market/${record.bond_id}`"
                    class="text-blue-600 hover:underline"
                    @click="modalVisible = false"
                  >
                    {{ record.bond_name }}
                  </router-link>
                </template>
                <template v-else-if="column.key === 'bond_type'">
                  <a-tag :color="bondTypeColor(record.bond_type)">
                    {{ record.bond_type }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'coupon_rate'">
                  <span class="tabular-nums">
                    {{ record.coupon_rate != null ? record.coupon_rate.toFixed(2) + '%' : '--' }}
                  </span>
                </template>
                <template v-else-if="column.key === 'issuer'">
                  <span class="text-gray-600">{{ record.issuer || '--' }}</span>
                </template>
              </template>
            </a-table>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs, { Dayjs } from 'dayjs'
import { LeftOutlined, RightOutlined } from '@ant-design/icons-vue'
import api from '../api'
import { BOND_TYPES } from '../utils/constants'
import { bondTypeColor } from '../utils/format'

const router = useRouter()

interface CalendarEvent {
  id: string
  bond_id: string
  bond_code: string
  bond_name: string
  bond_type: string
  event_type: string
  event_date: string
  event_title: string
  coupon_rate?: number
  issuer?: string
}

interface CalendarDay {
  date: Dayjs
  isCurrentMonth: boolean
  isToday: boolean
  eventCount: number
  events: CalendarEvent[]
  previewEvents: CalendarEvent[]
}

const bondTypes = BOND_TYPES
const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const currentDate = ref(dayjs())
const selectedBondType = ref<string | undefined>(undefined)
const selectedEventType = ref<string | undefined>(undefined)
const monthEvents = ref<Record<string, CalendarEvent[]>>({})
const monthLoading = ref(false)

const modalVisible = ref(false)
const selectedDay = ref<Dayjs | null>(null)
const dayEvents = ref<CalendarEvent[]>([])
const dayEventsLoading = ref(false)

const currentYear = computed(() => currentDate.value.year())
const currentMonth = computed(() => currentDate.value.month() + 1)

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.year()
  const month = currentDate.value.month()
  const firstDay = dayjs(new Date(year, month, 1))
  const startDay = firstDay.subtract(firstDay.day(), 'day')
  const today = dayjs().startOf('day')

  const days: CalendarDay[] = []
  for (let i = 0; i < 42; i++) {
    const d = startDay.add(i, 'day')
    const dateKey = d.format('YYYY-MM-DD')
    const events = monthEvents.value[dateKey] || []
    const isCurrentMonth = d.month() === month

    days.push({
      date: d,
      isCurrentMonth,
      isToday: d.isSame(today, 'day'),
      eventCount: events.length,
      events,
      previewEvents: events.slice(0, 3),
    })
  }
  return days
})

const modalTitle = computed(() => {
  if (!selectedDay.value) return ''
  return `${selectedDay.value.format('YYYY年MM月DD日')} 债券事件`
})

const groupedEvents = computed(() => {
  const groups: Array<{ type: string; label: string; events: CalendarEvent[] }> = []
  const issueEvents = dayEvents.value.filter((e) => e.event_type === 'issue')
  const maturityEvents = dayEvents.value.filter((e) => e.event_type === 'maturity')

  if (issueEvents.length > 0) {
    groups.push({ type: 'issue', label: '新发债', events: issueEvents })
  }
  if (maturityEvents.length > 0) {
    groups.push({ type: 'maturity', label: '到期日', events: maturityEvents })
  }
  return groups
})

function getEventDotClass(eventType: string): string {
  if (eventType === 'issue') return 'bg-green-500'
  if (eventType === 'maturity') return 'bg-red-500'
  return 'bg-gray-400'
}

function getDayBadgeClass(day: CalendarDay): string {
  const hasIssue = day.events.some((e) => e.event_type === 'issue')
  const hasMaturity = day.events.some((e) => e.event_type === 'maturity')
  if (hasIssue && hasMaturity) return 'bg-blue-500'
  if (hasIssue) return 'bg-green-500'
  if (hasMaturity) return 'bg-red-500'
  return 'bg-gray-400'
}

async function fetchMonthEvents() {
  monthLoading.value = true
  try {
    const params: Record<string, any> = {
      year: currentDate.value.year(),
      month: currentDate.value.month() + 1,
    }
    if (selectedBondType.value) {
      params.bond_type = selectedBondType.value
    }
    if (selectedEventType.value) {
      params.event_type = selectedEventType.value
    }

    const res = await api.get<{ days: Array<{ date: string; events: CalendarEvent[]; event_count: number }> }>(
      '/api/calendar/month',
      { params }
    )

    const eventsMap: Record<string, CalendarEvent[]> = {}
    for (const day of res.data.days) {
      eventsMap[day.date] = day.events
    }
    monthEvents.value = eventsMap
  } catch {
    monthEvents.value = {}
  } finally {
    monthLoading.value = false
  }
}

async function fetchDayEvents(date: Dayjs) {
  dayEventsLoading.value = true
  try {
    const params: Record<string, any> = {
      target_date: date.format('YYYY-MM-DD'),
    }
    if (selectedBondType.value) {
      params.bond_type = selectedBondType.value
    }
    if (selectedEventType.value) {
      params.event_type = selectedEventType.value
    }

    const res = await api.get<CalendarEvent[]>('/api/calendar/day', { params })
    dayEvents.value = res.data
  } catch {
    dayEvents.value = []
  } finally {
    dayEventsLoading.value = false
  }
}

function goToPrevMonth() {
  currentDate.value = currentDate.value.subtract(1, 'month')
  fetchMonthEvents()
}

function goToNextMonth() {
  currentDate.value = currentDate.value.add(1, 'month')
  fetchMonthEvents()
}

function goToToday() {
  currentDate.value = dayjs()
  fetchMonthEvents()
}

function handleDayClick(day: CalendarDay) {
  if (day.eventCount === 0) return
  selectedDay.value = day.date
  modalVisible.value = true
  fetchDayEvents(day.date)
}

onMounted(() => {
  fetchMonthEvents()
})
</script>

<style scoped>
.calendar-day {
  min-height: 100px;
}

.calendar-day:hover {
  background-color: #eff6ff;
}

.event-table :deep(.ant-table-thead > tr > th) {
  background: #f9fafb;
  font-weight: 600;
}
</style>
