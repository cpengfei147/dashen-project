<template>
  <div class="quote-card">
    <div class="quote-header">
      <van-icon name="balance-list-o" size="20" />
      <span>搬家报价</span>
    </div>

    <div class="quote-details">
      <div
        v-for="(item, index) in quote.details"
        :key="index"
        class="quote-item"
      >
        <span class="item-name">{{ item.item }}</span>
        <span class="item-desc" v-if="item.description">{{ item.description }}</span>
        <span class="item-amount">¥{{ item.amount }}</span>
      </div>
    </div>

    <div class="quote-total">
      <span>总计</span>
      <span class="total-amount">¥{{ quote.total }}</span>
    </div>

    <div class="quote-footer">
      <p class="valid-tip">{{ quote.valid_until }}</p>
      <van-button type="primary" block @click="handleConfirm">
        确认预约
      </van-button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  quote: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['confirm'])

function handleConfirm() {
  emit('confirm')
}
</script>

<style scoped>
.quote-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.quote-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1989fa;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.quote-details {
  padding: 12px 0;
}

.quote-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.item-name {
  color: #333;
}

.item-desc {
  color: #999;
  margin-left: 8px;
  font-size: 12px;
}

.item-amount {
  margin-left: auto;
  color: #333;
}

.quote-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #eee;
  font-size: 16px;
  font-weight: 600;
}

.total-amount {
  color: #ee0a24;
  font-size: 20px;
}

.quote-footer {
  padding-top: 12px;
}

.valid-tip {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-bottom: 12px;
}
</style>
