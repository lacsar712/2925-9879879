import axios from 'axios'
import { message } from 'ant-design-vue'

const api = axios.create({
  baseURL: '',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('bondview_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    if (status === 401) {
      localStorage.removeItem('bondview_token')
      localStorage.removeItem('bondview_user')
      window.location.href = '/login'
      message.error('登录已过期，请重新登录')
    } else if (status === 403) {
      message.error(detail || '没有权限执行此操作')
    } else if (status === 404) {
      message.error(detail || '请求的资源不存在')
    } else if (status >= 500) {
      message.error('服务器错误，请稍后重试')
    } else {
      message.error(detail || '请求失败')
    }

    return Promise.reject(error)
  }
)

export interface RatingChange {
  id: string
  bond_id: string
  agency: string
  change_type: 'upgrade' | 'downgrade' | 'outlook'
  old_rating?: string
  new_rating?: string
  old_outlook?: string
  new_outlook?: string
  effective_date: string
  description?: string
  created_at?: string
  bond_code?: string
  bond_name?: string
}

export interface RatingChangeListResponse {
  items: RatingChange[]
  total: number
  page: number
  page_size: number
}

export async function getRatingChanges(params?: {
  change_type?: string
  page?: number
  page_size?: number
}): Promise<RatingChangeListResponse> {
  const response = await api.get('/api/rating-changes', { params })
  return response.data
}

export async function getRatingChange(id: string): Promise<RatingChange> {
  const response = await api.get(`/api/rating-changes/${id}`)
  return response.data
}

export interface DataQualityOverview {
  total_sources: number
  enabled_sources: number
  disabled_sources: number
  online_sources: number
  offline_sources: number
  error_sources: number
  healthy_sources: number
  warning_sources: number
  critical_sources: number
  avg_latency_ms: number
  total_missing_quotes: number
  total_inverted_spreads: number
  avg_health_score: number
}

export interface DataQualitySource {
  id: string
  name: string
  source_type: string
  status: 'online' | 'offline' | 'error'
  is_enabled: boolean
  last_heartbeat: string | null
  avg_latency_ms: number | null
  today_missing_quotes: number
  today_inverted_spreads: number
  health_score: number | null
  description?: string
}

export async function getDataQualityOverview(): Promise<DataQualityOverview> {
  const response = await api.get('/api/admin/data-quality/overview')
  return response.data
}

export async function getDataQualitySources(): Promise<DataQualitySource[]> {
  const response = await api.get('/api/admin/data-quality/sources')
  return response.data
}

export default api
