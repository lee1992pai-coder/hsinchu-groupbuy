<template>
  <div>
    <div class="toolbar">
      <el-radio-group v-model="filter" @change="fetchMerchants">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="pending">待審核</el-radio-button>
        <el-radio-button value="approved">已核准</el-radio-button>
        <el-radio-button value="suspended">已停權</el-radio-button>
      </el-radio-group>
    </div>

    <el-table :data="merchants" v-loading="loading" stripe>
      <el-table-column prop="name" label="商家名稱" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="phone" label="電話" width="130" />
      <el-table-column label="抽成比例" width="120">
        <template #default="{ row }">
          {{ (row.commission_rate * 100).toFixed(0) }}%
        </template>
      </el-table-column>
      <el-table-column label="狀態" width="110">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'pending'"
            type="success" size="small"
            @click="approve(row.id)"
          >核准</el-button>
          <el-button
            v-if="row.status === 'approved'"
            type="danger" size="small"
            @click="suspend(row.id)"
          >停權</el-button>
          <el-button size="small" @click="openCommission(row)">調整抽成</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 調整抽成 Dialog -->
    <el-dialog v-model="commissionDialog" title="調整抽成比例" width="360px">
      <el-form label-width="100px">
        <el-form-item label="商家">{{ editMerchant?.name }}</el-form-item>
        <el-form-item label="抽成比例 (%)">
          <el-input-number v-model="newRate" :min="1" :max="50" />
          <span style="margin-left:8px">%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="commissionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCommission">儲存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const merchants = ref([])
const loading = ref(false)
const filter = ref('')
const commissionDialog = ref(false)
const editMerchant = ref(null)
const newRate = ref(10)

const STATUS_MAP = {
  pending: { label: '待審核', type: 'warning' },
  approved: { label: '已核准', type: 'success' },
  suspended: { label: '已停權', type: 'danger' },
}
const statusLabel = (s) => STATUS_MAP[s]?.label || s
const statusType = (s) => STATUS_MAP[s]?.type || ''

async function fetchMerchants() {
  loading.value = true
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/admin/merchants', { params })
  merchants.value = data
  loading.value = false
}

async function approve(id) {
  await api.put(`/admin/merchants/${id}/approve`)
  ElMessage.success('已核准')
  await fetchMerchants()
}

async function suspend(id) {
  await ElMessageBox.confirm('確定要停權此商家嗎？', '警告', { type: 'warning' })
  await api.put(`/admin/merchants/${id}/suspend`)
  ElMessage.success('已停權')
  await fetchMerchants()
}

function openCommission(merchant) {
  editMerchant.value = merchant
  newRate.value = Math.round(merchant.commission_rate * 100)
  commissionDialog.value = true
}

async function saveCommission() {
  await api.put(`/admin/merchants/${editMerchant.value.id}/commission?rate=${newRate.value / 100}`)
  ElMessage.success('已更新抽成比例')
  commissionDialog.value = false
  await fetchMerchants()
}

onMounted(fetchMerchants)
</script>

<style scoped>
.toolbar { margin-bottom: 20px; }
</style>
