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

/**
 * 申请找回密码（发送邮件）
 * @param {Object} data - 包含 email 的对象
 */
export function forgotPassword(data) {
  return request({
    url: '/auth/forgot-password',
    method: 'post',
    data: data
  })
}

/**
 * 拿着 Token 真正去修改密码
 * @param {Object} data - 包含 token 和 new_password 的对象
 */
export function resetPassword(data) {
  return request({
    url: '/auth/reset-password',
    method: 'post',
    data: data
  })
}