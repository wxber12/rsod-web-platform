import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 🌟 优化：优先读取 message，其次读取 FastAPI 默认的 detail，最后保底服务器错误
    const errorMsg = error.response?.data?.message || error.response?.data?.detail || '服务器错误'

    ElMessage.error('请求失败：' + errorMsg)
    return Promise.reject(error)
  }
)

export default service