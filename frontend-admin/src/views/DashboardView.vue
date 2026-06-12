<template>
  <div>
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="kpi in kpis" :key="kpi.label">
        <el-card class="kpi-card" shadow="hover">
          <div class="kpi-icon" :style="{ background: kpi.color }">{{ kpi.icon }}</div>
          <div class="kpi-body">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value">{{ kpi.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <!-- 待審核商家 -->
      <el-col :span="6">
        <el-card>
          <template #header>
            <span>🏪 待審核商家</span>
            <el-tag type="warning" style="margin-left:8px">{{ pendingMerchants.length }}</el-tag>
          </template>
          <el-table :data="pendingMerchants" size="small">
            <el-table-column prop="name" label="商家名稱" />
            <el-table-column prop="email" label="Email" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="success" size="small" @click="approve(row.id)">核准</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!pendingMerchants.length" description="無待審核商家" :image-size="60" />
        </el-card>
      </el-col>

      <!-- 商家銷售排行 -->
      <el-col :span="6">
        <el-card>
          <template #header>🏆 商家銷售排行</template>
          <el-empty v-if="!ranking.length" description="暫無數據" :image-size="50" />
          <div v-for="(r, idx) in ranking.slice(0,5)" :key="r.merchant" class="rank-item">
            <span class="rank-no">{{ idx + 1 }}</span>
            <span class="rank-name">{{ r.merchant }}</span>
            <span class="rank-val">NT$ {{ Number(r.total).toLocaleString() }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 平台分潤快覽 -->
      <el-col :span="6">
        <el-card>
          <template #header>💰 平台分潤快覽</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="總交易金額">
              NT$ {{ fmt(revenue.gross_revenue) }}
            </el-descriptions-item>
            <el-descriptions-item label="平台收入（抽成）">
              <span style="color:#409eff;font-weight:bold">NT$ {{ fmt(revenue.platform_income) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="商家已撥款">
              NT$ {{ fmt(revenue.merchant_payout) }}
            </el-descriptions-item>
            <el-descriptions-item label="交易筆數">
              {{ revenue.transaction_count }} 筆
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const pendingMerchants = ref([])
const revenue = reactive({ gross_revenue: 0, platform_income: 0, merchant_payout: 0, transaction_count: 0 })

const kpis = ref([
  { label: '商家總數', value: '-', icon: '🏪', color: '#dbeafe' },
  { label: '平台總收入', value: '-', icon: '💰', color: '#dcfce7' },
  { label: '總交易金額', value: '-', icon: '📊', color: '#fef9c3' },
  { label: '待審核商家', value: '-', icon: '⏳', color: '#fee2e2' },
])

const fmt = (n) => Number(n || 0).toLocaleString()

const ranking = ref([])

async function loadData() {
  const [merchantsRes, revenueRes, rankingRes] = await Promise.all([
    api.get('/admin/merchants'),
    api.get('/admin/revenue'),
    api.get('/admin/revenue/merchant-ranking').catch(() => ({ data: [] })),
  ])
  ranking.value = rankingRes.data
  const merchants = merchantsRes.data
  Object.assign(revenue, revenueRes.data)
  pendingMerchants.value = merchants.filter((m) => m.status === 'pending')

  kpis.value[0].value = merchants.length
  kpis.value[1].value = `NT$ ${fmt(revenue.platform_income)}`
  kpis.value[2].value = `NT$ ${fmt(revenue.gross_revenue)}`
  kpis.value[3].value = pendingMerchants.value.length
}

async function approve(id) {
  await api.put(`/admin/merchants/${id}/approve`)
  ElMessage.success('已核准商家')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.kpi-row { margin-bottom: 0; }
.kpi-card { display: flex; }
.kpi-card :deep(.el-card__body) { display: flex; align-items: center; gap: 16px; padding: 20px; }
.kpi-icon {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; flex-shrink: 0;
}
.kpi-label { font-size: 13px; color: #64748b; margin-bottom: 4px; }
.kpi-value { font-size: 22px; font-weight: bold; color: #1e293b; }
.rank-item { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
.rank-no { width: 24px; height: 24px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; margin-right: 8px; flex-shrink: 0; }
.rank-item:nth-child(1) .rank-no { background: #fbbf24; color: #fff; }
.rank-item:nth-child(2) .rank-no { background: #94a3b8; color: #fff; }
.rank-item:nth-child(3) .rank-no { background: #b45309; color: #fff; }
.rank-name { flex: 1; font-size: 14px; }
.rank-val { font-size: 13px; color: #2563eb; font-weight: 600; }
</style>
