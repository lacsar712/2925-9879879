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

export default api
