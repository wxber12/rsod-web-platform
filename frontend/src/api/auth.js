import request from '../utils/request' // 👈 走你现有的基础网络封装实例

/**
 * 真实登录网络请求
 * @param {Object} data - 包含 username 和 password 的表单对象
 */
export function login(data) {
  return request({
    url: '/auth/login', // 对应 FastAPI 后端的路由
    method: 'post',
    data: data
  })
}

/**
 * 真实注册网络请求
 * @param {Object} data - 包含 username 和 password 的注册对象
 */
export function register(data) {
  return request({
    url: '/auth/register', // 对应 FastAPI 后端的注册路由
    method: 'post',
    data: data
  })
}