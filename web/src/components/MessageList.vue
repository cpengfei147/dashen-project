<template>
  <div class="message-list">
    <div
      v-for="(msg, index) in messages"
      :key="index"
      class="message-item"
      :class="msg.role"
    >
      <!-- 头像 -->
      <div class="avatar">
        <van-icon v-if="msg.role === 'assistant'" name="service-o" size="24" />
        <van-icon v-else name="user-o" size="24" />
      </div>

      <!-- 消息气泡 -->
      <div class="bubble">
        {{ msg.content }}
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="message-item assistant">
      <div class="avatar">
        <van-icon name="service-o" size="24" />
      </div>
      <div class="bubble loading">
        <van-loading type="spinner" size="16" />
        <span>正在思考...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-item.assistant .avatar {
  background-color: #1989fa;
  color: #fff;
}

.message-item.user .avatar {
  background-color: #07c160;
  color: #fff;
}

.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-word;
}

.message-item.assistant .bubble {
  background-color: #fff;
  color: #333;
  border-top-left-radius: 4px;
}

.message-item.user .bubble {
  background-color: #1989fa;
  color: #fff;
  border-top-right-radius: 4px;
}

.bubble.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
}
</style>
