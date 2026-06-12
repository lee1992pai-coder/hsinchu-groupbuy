<template>
  <div>
    <!-- 統計卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-label">總銷售額</div>
          <div class="stat-value">NT$ {{ fmt(stats.gross_amount) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card commission">
          <div class="stat-label">平台抽成</div>
          <div class="stat-value">NT$ {{ fmt(stats.total_commission) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card net">
          <div class="stat-label">商家實收</div>
          <div class="stat-value green">NT$ {{ fmt(stats.net_amount) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-loading="loading" style="margin-top:20px">
      <template #header>分潤說明</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="平台抽成比例">
          依個別合約，預設 10%
        </el-descriptions-item>
        <el-descriptions-item label="結算週期">
          每月 1 日自動結算上月帳款
        </el-descriptions-item>
        <el-descriptions-item label="撥款方式">
          透過綠界 ECPay 分帳直接撥入商家銀行帳戶
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const loading = ref(false)
const stats = reactive({ gross_amount: 0, total_commission: 0, net_amount: 0 })

const fmt = (n) => Number(n || 0).toLocaleString()

onMounted(async () => {
  loading.value = true
  const { data } = await api.get(`/merchant/${auth.merchantId}/revenue`)
  Object.assign(stats, data)
  loading.value = false
})
</script>

<style scoped>
.stat-row { margin-bottom: 20px; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-label { color: #909399; font-size: 14px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; }
.green { color: #67c23a; }
</style>
