<template>
  <div class="order-card">
    <div class="order-header">
      <van-icon name="passed" size="20" color="#07c160" />
      <span>订单已创建</span>
    </div>

    <div class="order-info">
      <div class="info-item">
        <span class="label">订单号</span>
        <span class="value">{{ order.id.slice(0, 8) }}</span>
      </div>
      <div class="info-item">
        <span class="label">搬出地址</span>
        <span class="value">{{ order.address_from }}</span>
      </div>
      <div class="info-item">
        <span class="label">搬入地址</span>
        <span class="value">{{ order.address_to }}</span>
      </div>
      <div class="info-item">
        <span class="label">搬家日期</span>
        <span class="value">{{ order.moving_date }}</span>
      </div>
      <div class="info-item highlight">
        <span class="label">报价金额</span>
        <span class="value price">¥{{ order.quote_amount }}</span>
      </div>
    </div>

    <div class="order-status">
      <van-tag type="success">{{ statusText }}</van-tag>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  order: {
    type: Object,
    required: true
  }
})

const statusText = computed(() => {
  const statusMap = {
    pending: '待确认',
    confirmed: '已确认',
    cancelled: '已取消',
    completed: '已完成'
  }
  return statusMap[props.order.status] || props.order.status
})
</script>

<style scoped>
.order-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.order-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #07c160;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.order-info {
  padding: 12px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}

.info-item .label {
  color: #999;
}

.info-item .value {
  color: #333;
  max-width: 60%;
  text-align: right;
}

.info-item.highlight .value.price {
  color: #ee0a24;
  font-size: 18px;
  font-weight: 600;
}

.order-status {
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
}
</style>
