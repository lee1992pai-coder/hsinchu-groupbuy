<template>
  <div>
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px">
      <template #header>📋 帳務說明</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="結算週期">每月 1 日自動結算</el-descriptions-item>
        <el-descriptions-item label="金流服務商">綠界 ECPay Marketplace</el-descriptions-item>
        <el-descriptions-item label="預設抽成">10%（可個別調整）</el-descriptions-item>
        <el-descriptions-item label="撥款時間">結算後 3 個工作天</el-descriptions-item>
        <el-descriptions-item label="法規依據" :span="2">
          符合台灣《電子支付機構管理條例》，分帳由綠界特約商店子帳戶機制處理
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const stats = ref([
  { label: '總交易金額', value: '-', color: '#1e293b' },
  { label: '平台收入', value: '-', color: '#2563eb' },
  { label: '商家撥款', value: '-', color: '#16a34a' },
  { label: '總筆數', value: '-', color: '#d97706' },
])

const fmt = (n) => `NT$ ${Number(n || 0).toLocaleString()}`

onMounted(async () => {
  const { data } = await api.get('/admin/revenue')
  stats.value[0].value = fmt(data.gross_revenue)
  stats.value[1].value = fmt(data.platform_income)
  stats.value[2].value = fmt(data.merchant_payout)
  stats.value[3].value = `${data.transaction_count} 筆`
})
</script>

<style scoped>
.stat-card { text-align: center; padding: 12px 0; }
.stat-label { color: #64748b; font-size: 14px; margin-bottom: 10px; }
.stat-value { font-size: 26px; font-weight: bold; }
</style>
