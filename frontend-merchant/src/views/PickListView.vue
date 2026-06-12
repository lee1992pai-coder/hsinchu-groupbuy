<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" plain @click="fetchPickList">重新整理</el-button>
      <el-button-group>
        <el-button @click="exportFile('excel')">
          <el-icon><Document /></el-icon> 匯出 Excel
        </el-button>
        <el-button @click="exportFile('pdf')">
          <el-icon><Printer /></el-icon> 匯出 PDF
        </el-button>
      </el-button-group>
      <el-button @click="printPage">🖨️ 直接列印</el-button>
    </div>

    <el-alert type="info" :closable="false" class="info-bar">
      以下為所有「已付款」訂單的品項彙總，請依數量備貨
    </el-alert>

    <el-table :data="pickList" v-loading="loading" stripe id="pick-table">
      <el-table-column type="index" label="項次" width="70" />
      <el-table-column prop="product" label="商品名稱" min-width="180" />
      <el-table-column prop="variant" label="規格" width="130">
        <template #default="{ row }">
          <el-tag v-if="row.variant !== '-'" size="small">{{ row.variant }}</el-tag>
          <span v-else class="text-gray">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="需備數量" width="130">
        <template #default="{ row }">
          <span class="qty-badge">{{ row.quantity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="備貨確認" width="110">
        <template #default="{ row }">
          <el-checkbox v-model="row.done" @change="updateProgress" />
        </template>
      </el-table-column>
    </el-table>

    <div v-if="!loading && !pickList.length" class="empty">目前沒有待備貨的訂單</div>

    <!-- 進度 -->
    <div v-if="pickList.length" class="progress-bar">
      <span>備貨進度 {{ doneCount }} / {{ pickList.length }}</span>
      <el-progress :percentage="progressPct" style="flex:1;margin-left:16px" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Document, Printer } from '@element-plus/icons-vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const pickList = ref([])
const loading = ref(false)
const doneCount = computed(() => pickList.value.filter((i) => i.done).length)
const progressPct = computed(() =>
  pickList.value.length ? Math.round((doneCount.value / pickList.value.length) * 100) : 0
)

async function fetchPickList() {
  loading.value = true
  const { data } = await api.get(`/merchant/${auth.merchantId}/pick-list`)
  pickList.value = data.map((item) => ({ ...item, done: false }))
  loading.value = false
}

async function exportFile(fmt) {
  const url = `/api/v1/merchant/${auth.merchantId}/pick-list/export?fmt=${fmt}`
  const link = document.createElement('a')
  link.href = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + `/api/v1/merchant/${auth.merchantId}/pick-list/export?fmt=${fmt}`
  link.download = `pick_list.${fmt === 'excel' ? 'xlsx' : 'pdf'}`
  link.click()
}

function printPage() { window.print() }
function updateProgress() {}

onMounted(fetchPickList)
</script>

<style scoped>
.toolbar { margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.info-bar { margin-bottom: 16px; }
.empty { text-align: center; padding: 40px; color: #909399; }
.qty-badge { font-size: 20px; font-weight: bold; color: #409eff; }
.text-gray { color: #c0c4cc; }
.progress-bar { display: flex; align-items: center; margin-top: 16px; }

@media print {
  .toolbar, .info-bar, .progress-bar { display: none; }
}
</style>
