<template>
  <div class="chat-page">
    <!-- 头部 -->
    <van-nav-bar title="搬家助手" fixed />

    <!-- 消息列表 -->
    <div class="chat-content" ref="chatContent">
      <MessageList :messages="messages" :loading="loading" />

      <!-- 报价卡片 -->
      <QuoteCard
        v-if="quote && stage === 'quoting'"
        :quote="quote"
        @confirm="handleConfirmQuote"
      />

      <!-- 订单卡片 -->
      <OrderCard
        v-if="order"
        :order="order"
      />
    </div>

    <!-- 输入框 -->
    <MessageInput
      v-model="inputText"
      :disabled="loading || stage === 'completed'"
      @send="handleSend"
    />
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { showToast } from 'vant'
import MessageList from '../components/MessageList.vue'
import MessageInput from '../components/MessageInput.vue'
import QuoteCard from '../components/QuoteCard.vue'
import OrderCard from '../components/OrderCard.vue'
import { sendMessage, createOrder } from '../api/chat'

// 状态
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const sessionId = ref(null)
const stage = ref('collecting')
const quote = ref(null)
const order = ref(null)
const chatContent = ref(null)

// 生成会话ID
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatContent.value) {
      chatContent.value.scrollTop = chatContent.value.scrollHeight
    }
  })
}

// 发送消息
async function handleSend() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: text,
    timestamp: new Date().toISOString()
  })
  inputText.value = ''
  scrollToBottom()

  // 发送请求
  loading.value = true
  try {
    const response = await sendMessage(sessionId.value, text)

    // 更新会话ID
    sessionId.value = response.session_id

    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response.reply,
      timestamp: new Date().toISOString()
    })

    // 更新状态
    stage.value = response.stage

    // 如果可以报价，显示报价卡片
    if (response.can_quote && response.quote) {
      quote.value = response.quote
    }

    scrollToBottom()
  } catch (error) {
    console.error('发送失败:', error)
    showToast('发送失败，请重试')
    // 移除失败的用户消息
    messages.value.pop()
  } finally {
    loading.value = false
  }
}

// 确认报价，创建订单
async function handleConfirmQuote() {
  loading.value = true
  try {
    const orderData = await createOrder(sessionId.value)
    order.value = orderData
    stage.value = 'completed'
    quote.value = null

    // 添加确认消息
    messages.value.push({
      role: 'assistant',
      content: `太好了！订单已创建成功，订单号：${orderData.id.slice(0, 8)}。我们的工作人员会尽快与您联系确认搬家细节。感谢您的信任！`,
      timestamp: new Date().toISOString()
    })

    scrollToBottom()
  } catch (error) {
    console.error('创建订单失败:', error)
    showToast('创建订单失败，请重试')
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  sessionId.value = generateSessionId()

  // 添加欢迎消息
  messages.value.push({
    role: 'assistant',
    content: '你好！我是小搬，你的搬家助手。请告诉我你的搬家需求，比如从哪里搬到哪里，什么时候搬家？',
    timestamp: new Date().toISOString()
  })
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 60px 12px 70px;
}
</style>
