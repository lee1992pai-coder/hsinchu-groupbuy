<template>
  <div>
    <h2 class="page-title">📦 我的訂單</h2>
    <div v-loading="loading">
      <el-empty v-if="!orders.length && !loading" description="尚無訂單紀錄" />

      <el-card v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-id">訂單 #{{ order.id.slice(0, 8).toUpperCase() }}</span>
          <el-tag :type="statusType(order.status)">{{ statusLabel(order.status) }}</el-tag>
        </div>

        <!-- 狀態進度條 -->
        <el-steps :active="stepIndex(order.status)" finish-status="success" class="steps" size="small">
          <el-step title="已付款" />
          <el-step title="備貨中" />
          <el-step :title="order.delivery_type === 'delivery' ? '配送中' : '待取貨'" />
          <el-step title="已完成" />
        </el-steps>

        <!-- 品項列表 -->
        <div v-if="order.items?.length" class="order-items">
          <div v-for="item in order.items" :key="item.product_id" class="order-item-row">
            <img :src="item.product_image || 'https://placehold.co/48x48/f0f4ff/409eff?text=商品'" class="item-thumb" />
            <span class="item-name">{{ item.product_name }}</span>
            <span class="item-qty">× {{ item.quantity }}</span>
            <span class="item-price">NT$ {{ item.unit_price }}</span>
          </div>
        </div>

        <div class="order-meta">
          <span v-if="order.delivery_type === 'pickup'">
            📍 取貨地點：{{ order.pickup_location }}
            <span v-if="order.pickup_time_slot">（{{ order.pickup_time_slot }}）</span>
          </span>
          <span v-else>🚚 配送至：{{ order.delivery_address }}</span>
        </div>

        <div class="order-footer">
          <span class="order-time">{{ formatDate(order.created_at) }}</span>
          <span class="order-amount">NT$ {{ order.total_amount }}</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const orders = ref([])
const loading = ref(true)

const STATUS_STEPS = ['paid', 'preparing', 'shipping', 'ready_pickup', 'completed']
const STATUS_MAP = {
  pending_payment: { label: '待付款', type: 'warning' },
  paid: { label: '已付款', type: 'primary' },
  preparing: { label: '備貨中', type: 'primary' },
  shipping: { label: '配送中', type: 'warning' },
  ready_pickup: { label: '待取貨', type: 'success' },
  completed: { label: '已完成', type: 'info' },
  refunded: { label: '已退款', type: 'danger' },
}
const statusLabel = (s) => STATUS_MAP[s]?.label || s
const statusType = (s) => STATUS_MAP[s]?.type || ''
const stepIndex = (s) => Math.max(0, STATUS_STEPS.indexOf(s))
const formatDate = (d) => dayjs(d).format('YYYY/MM/DD HH:mm')

onMounted(async () => {
  // 開發期間用 mock user id
  const userId = authStore.user?.id || '00000000-0000-0000-0000-000000000001'
  const { data } = await api.get(`/orders/user/${userId}`).catch(() => ({ data: [] }))
  orders.value = data
  loading.value = false
})
</script>

<style scoped>
.page-title { margin-bottom: 24px; }
.order-card { margin-bottom: 16px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.order-id { font-family: monospace; font-size: 13px; color: #606266; }
.steps { margin-bottom: 16px; }
.order-meta { font-size: 14px; color: #606266; margin-bottom: 12px; }
.order-footer { display: flex; justify-content: space-between; align-items: center; }
.order-time { font-size: 13px; color: #909399; }
.order-amount { font-size: 18px; font-weight: bold; color: #f56c6c; }
.order-items { border: 1px solid #f0f2f5; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; }
.order-item-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; }
.item-thumb { width: 48px; height: 48px; object-fit: cover; border-radius: 4px; flex-shrink: 0; }
.item-name { flex: 1; font-size: 14px; }
.item-qty { font-size: 13px; color: #909399; }
.item-price { font-size: 14px; color: #f56c6c; font-weight: 500; min-width: 70px; text-align: right; }
</style>
