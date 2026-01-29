import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 发送消息
 */
export async function sendMessage(sessionId, message) {
  const response = await api.post('/chat', {
    session_id: sessionId,
    message: message,
  })
  return response.data
}

/**
 * 获取会话信息
 */
export async function getSession(sessionId) {
  const response = await api.get(`/sessions/${sessionId}`)
  return response.data
}

/**
 * 获取报价
 */
export async function getQuote(sessionId) {
  const response = await api.post(`/sessions/${sessionId}/quote`)
  return response.data
}

/**
 * 创建订单
 */
export async function createOrder(sessionId) {
  const response = await api.post(`/sessions/${sessionId}/order`)
  return response.data
}

/**
 * 确认订单
 */
export async function confirmOrder(orderId, confirmed = true) {
  const response = await api.post(`/orders/${orderId}/confirm`, {
    confirmed: confirmed,
  })
  return response.data
}

/**
 * 获取订单信息
 */
export async function getOrder(orderId) {
  const response = await api.get(`/orders/${orderId}`)
  return response.data
}

export default api
