<template>
  <div>
    <!-- 即時接單通知 badge -->
    <el-alert
      v-if="newOrderAlert"
      type="success"
      :title="`🔔 新訂單！${newOrderAlert}`"
      :closable="true"
      @close="newOrderAlert = ''"
      class="new-order-alert"
    />

    <div class="toolbar">
      <el-radio-group v-model="statusFilter" @change="fetchOrders">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="paid">新訂單</el-radio-button>
        <el-radio-button value="preparing">備貨中</el-radio-button>
        <el-radio-button value="ready_pickup">待取貨</el-radio-button>
        <el-radio-button value="completed">已完成</el-radio-button>
      </el-radio-group>
      <el-button @click="fetchOrders" :loading="loading">重新整理</el-button>
    </div>

    <el-table :data="orders" v-loading="loading" stripe>
      <el-table-column prop="id" label="訂單編號" width="130">
        <template #default="{ row }">
          <code>{{ row.id.slice(0, 8).toUpperCase() }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="金額" width="110">
        <template #default="{ row }">NT$ {{ row.total_amount }}</template>
      </el-table-column>
      <el-table-column label="物流" width="90">
        <template #default="{ row }">
          <el-tag :type="row.delivery_type === 'pickup' ? 'info' : 'warning'" size="small">
            {{ row.delivery_type === 'pickup' ? '自取' : '配送' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="取貨/收件資訊" min-width="180">
        <template #default="{ row }">
          <span v-if="row.delivery_type === 'pickup'">
            {{ row.pickup_location }}
            <span v-if="row.pickup_time_slot" class="slot-tag">{{ row.pickup_time_slot }}</span>
          </span>
          <span v-else>{{ row.delivery_address }}</span>
        </template>
      </el-table-column>
      <el-table-column label="狀態" width="110">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下單時間" width="140">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="品項" min-width="160">
        <template #default="{ row }">
          <div v-for="item in row.items" :key="item.product_id" class="item-line">
            {{ item.product_name }} × {{ item.quantity }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="更新狀態" width="150">
        <template #default="{ row }">
          <el-select :model-value="row.status" size="small" @change="(v) => updateStatus(row, v)">
            <el-option label="備貨中" value="preparing" />
            <el-option label="待取貨" value="ready_pickup" />
            <el-option label="配送中" value="shipping" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const orders = ref([])
const loading = ref(false)
const statusFilter = ref('')
const newOrderAlert = ref('')
let ws = null
let reconnectDelay = 2000

const STATUS_MAP = {
  pending_payment: { label: '待付款', type: 'warning' },
  paid: { label: '新訂單', type: 'danger' },
  preparing: { label: '備貨中', type: 'primary' },
  ready_pickup: { label: '待取貨', type: 'success' },
  shipping: { label: '配送中', type: 'warning' },
  completed: { label: '已完成', type: 'info' },
}
const statusLabel = (s) => STATUS_MAP[s]?.label || s
const statusType = (s) => STATUS_MAP[s]?.type || ''
const formatDate = (d) => dayjs(d).format('MM/DD HH:mm')

async function fetchOrders() {
  loading.value = true
  const params = statusFilter.value ? { status: statusFilter.value } : {}
  const { data } = await api.get(`/merchant/${auth.merchantId}/orders`, { params })
  orders.value = data
  loading.value = false
}

async function updateStatus(order, status) {
  await api.put(`/merchant/${auth.merchantId}/orders/${order.id}/status?new_status=${status}`)
  order.status = status
  ElMessage.success('狀態已更新')
}

function connectWs() {
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  // 取出 host 部分（去掉路徑），替換協議
  const origin = new URL(base).origin.replace(/^http/, 'ws')
  ws = new WebSocket(`${origin}/ws/merchant/${auth.merchantId}`)
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data)
    if (msg.type === 'new_order') {
      newOrderAlert.value = `訂單 #${msg.order.id.slice(0, 8).toUpperCase()}，金額 NT$ ${msg.order.total_amount}`
      fetchOrders()
    }
  }
  ws.onopen = () => { reconnectDelay = 2000 }
  ws.onclose = () => {
    reconnectDelay = Math.min(reconnectDelay * 2, 30000)
    setTimeout(connectWs, reconnectDelay)
  }
}

onMounted(() => { fetchOrders(); connectWs() })
onUnmounted(() => ws?.close())
</script>

<style scoped>
.new-order-alert { margin-bottom: 16px; }
.toolbar { margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.slot-tag { font-size: 12px; color: #909399; margin-left: 6px; }
code { font-family: monospace; }
.item-line { font-size: 13px; line-height: 1.6; }
</style>
