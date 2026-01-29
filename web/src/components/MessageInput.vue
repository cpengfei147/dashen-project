<template>
  <div class="message-input">
    <van-field
      v-model="text"
      :disabled="disabled"
      placeholder="输入消息..."
      type="textarea"
      autosize
      rows="1"
      @keypress.enter.exact.prevent="handleSend"
    />
    <van-button
      type="primary"
      size="small"
      :disabled="disabled || !text.trim()"
      @click="handleSend"
    >
      发送
    </van-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'send'])

const text = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

function handleSend() {
  if (text.value.trim() && !props.disabled) {
    emit('send')
  }
}
</script>

<style scoped>
.message-input {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 8px 12px;
  background-color: #fff;
  border-top: 1px solid #eee;
}

.message-input :deep(.van-field) {
  flex: 1;
  background-color: #f5f5f5;
  border-radius: 20px;
  padding: 8px 16px;
}

.message-input :deep(.van-field__control) {
  max-height: 100px;
}

.message-input .van-button {
  flex-shrink: 0;
  border-radius: 20px;
  padding: 0 16px;
  height: 36px;
}
</style>
