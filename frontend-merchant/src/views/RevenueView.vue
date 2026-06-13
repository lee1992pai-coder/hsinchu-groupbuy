<template>
  <div class="rev-wrap" ref="reportRef">

    <!-- 頁首 -->
    <div class="page-header no-print">
      <div class="page-title">
        <span class="title-icon">📊</span>
        <div>
          <h2>我的營收報表</h2>
          <p class="subtitle">銷售趨勢 · 商品分析 · 分潤明細</p>
        </div>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange" type="daterange"
          range-separator="至" start-placeholder="開始" end-placeholder="結束"
          format="YYYY/MM/DD" value-format="YYYY-MM-DD"
          :shortcuts="shortcuts" style="width:270px"
          @change="loadAll"
        />
        <el-dropdown @command="exportExcel" trigger="click">
          <el-button type="success" :loading="exporting.excel">
            ⬇ Excel <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="all">📁 完整報表</el-dropdown-item>
              <el-dropdown-item command="product">📦 商品明細</el-dropdown-item>
              <el-dropdown-item command="orders">📋 訂單流水</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="danger" :loading="exporting.pdf" @click="exportPDF">
          📄 PDF 匯出
        </el-button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid" v-loading="loading.summary">
      <div class="kpi-card" v-for="k in kpis" :key="k.label">
        <div class="kpi-icon" :style="{ background: k.bg }">{{ k.icon }}</div>
        <div class="kpi-body">
          <div class="kpi-label">{{ k.label }}</div>
          <div class="kpi-value" :style="{ color: k.color }">{{ k.val }}</div>
          <div class="kpi-sub" v-if="k.sub">{{ k.sub }}</div>
        </div>
      </div>
    </div>

    <!-- 趨勢折線圖 + 分類餅圖 -->
    <div class="chart-row">
      <el-card class="chart-card trend-card" v-loading="loading.trend">
        <template #header>
          <div class="card-head">
            <span>📈 每日銷售趨勢</span>
            <el-radio-group v-model="trendMode" size="small" @change="renderTrend">
              <el-radio-button value="gross">銷售額</el-radio-button>
              <el-radio-button value="net">實收</el-radio-button>
              <el-radio-button value="orders">訂單數</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="trendChartEl" class="chart-el" />
      </el-card>

      <el-card class="chart-card pie-card" v-loading="loading.category">
        <template #header><span>🥧 分類銷售佔比</span></template>
        <div ref="pieChartEl" class="chart-el" />
      </el-card>
    </div>

    <!-- 商品銷售排行 -->
    <el-card class="section-card" v-loading="loading.product">
      <template #header>
        <div class="card-head">
          <span>📦 商品銷售排行</span>
          <el-tag type="info">{{ productRows.length }} 項</el-tag>
        </div>
      </template>
      <el-table :data="productRows" stripe border
        :default-sort="{ prop: 'revenue', order: 'descending' }"
        show-summary :summary-method="productSummary">
        <el-table-column label="排名" width="62" align="center">
          <template #default="{ $index }">
            <span class="rank" :class="rankCls($index)">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名稱" min-width="160" />
        <el-table-column prop="category" label="分類" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="catType(row.category)">{{ catLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="group_price" label="單價" width="100" align="right">
          <template #default="{ row }">NT$ {{ row.group_price }}</template>
        </el-table-column>
        <el-table-column prop="qty" label="銷售件數" width="90" align="center" sortable>
          <template #default="{ row }"><b>{{ row.qty }}</b> 件</template>
        </el-table-column>
        <el-table-column prop="revenue" label="銷售金額" width="130" align="right" sortable>
          <template #default="{ row }">{{ fmt(row.revenue) }}</template>
        </el-table-column>
        <el-table-column label="佔比" width="110" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="totalProductRevenue ? Math.round(row.revenue / totalProductRevenue * 100) : 0"
              :stroke-width="6" :format="p => p + '%'"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 訂單流水帳 -->
    <el-card class="section-card" v-loading="loading.orders">
      <template #header>
        <div class="card-head">
          <span>📋 訂單流水帳</span>
          <el-select v-model="orderStatus" clearable placeholder="全部狀態" style="width:120px" @change="loadOrders">
            <el-option v-for="s in statusOpts" :key="s.v" :label="s.l" :value="s.v" />
          </el-select>
        </div>
      </template>
      <el-table :data="orderRows" stripe border max-height="380">
        <el-table-column prop="created_at" label="時間" width="155">
          <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="order_id" label="訂單號" width="105">
          <template #default="{ row }"><span class="mono">{{ row.order_id.slice(0,8) }}…</span></template>
        </el-table-column>
        <el-table-column prop="user_name" label="消費者" width="95" />
        <el-table-column prop="status" label="狀態" width="88" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLbl(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="delivery_type" label="取貨" width="68" align="center">
          <template #default="{ row }">{{ row.delivery_type === 'pickup' ? '自取' : '配送' }}</template>
        </el-table-column>
        <el-table-column prop="gross" label="訂單金額" width="115" align="right">
          <template #default="{ row }">{{ fmt(row.gross) }}</template>
        </el-table-column>
        <el-table-column prop="commission" label="平台抽成" width="105" align="right">
          <template #default="{ row }"><span class="c-red">{{ fmt(row.commission) }}</span></template>
        </el-table-column>
        <el-table-column prop="net" label="商家實收" width="115" align="right">
          <template #default="{ row }"><span class="c-green">{{ fmt(row.net) }}</span></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分潤說明 -->
    <el-card class="section-card">
      <template #header>💡 分潤機制說明</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="平台抽成比例">依個別合約，預設 10%</el-descriptions-item>
        <el-descriptions-item label="結算週期">每月 1 日自動結算上月帳款</el-descriptions-item>
        <el-descriptions-item label="撥款方式">透過綠界 ECPay 分帳直接撥入商家銀行帳戶</el-descriptions-item>
        <el-descriptions-item label="撥款時間">結算後 3 個工作天</el-descriptions-item>
        <el-descriptions-item label="法規依據" :span="2">符合台灣《電子支付機構管理條例》，子帳戶分帳機制</el-descriptions-item>
      </el-descriptions>
    </el-card>

  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import * as XLSX from 'xlsx'
import api from '../api'
import { useAuthStore } from '../stores/auth'

echarts.use([LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const auth = useAuthStore()
const mid = computed(() => auth.merchantId)

// ── refs ───────────────────────────────────────────────────
const reportRef = ref(null)
const trendChartEl = ref(null)
const pieChartEl = ref(null)
let trendChart = null
let pieChart = null

// ── 狀態 ──────────────────────────────────────────────────
const dateRange = ref(null)
const trendMode = ref('gross')
const orderStatus = ref(null)
const exporting = ref({ excel: false, pdf: false })
const loading = ref({ summary: false, trend: false, category: false, product: false, orders: false })

const summary = ref({ gross: 0, commission: 0, net: 0, order_count: 0, avg_order_value: 0 })
const trendData = ref([])
const categoryData = ref([])
const productRows = ref([])
const orderRows = ref([])

// ── KPI ───────────────────────────────────────────────────
const kpis = computed(() => {
  const s = summary.value
  const rate = s.gross ? ((s.commission / s.gross) * 100).toFixed(1) : 0
  return [
    { icon: '💰', label: '總銷售額', val: fmt(s.gross), bg: '#EFF6FF', color: '#2563EB', sub: '' },
    { icon: '🏦', label: '平台抽成', val: fmt(s.commission), bg: '#FEF2F2', color: '#DC2626', sub: `佔比 ${rate}%` },
    { icon: '✅', label: '商家實收', val: fmt(s.net), bg: '#F0FDF4', color: '#16A34A', sub: `佔比 ${s.gross ? (100 - rate) + '%' : '0%'}` },
    { icon: '📦', label: '訂單數', val: `${s.order_count} 筆`, bg: '#FFF7ED', color: '#EA580C', sub: '' },
    { icon: '💳', label: '平均客單價', val: fmt(s.avg_order_value), bg: '#F5F3FF', color: '#7C3AED', sub: '' },
  ]
})
const totalProductRevenue = computed(() => productRows.value.reduce((s, r) => s + r.revenue, 0))

// ── 日期快捷 ─────────────────────────────────────────────
const shortcuts = [
  { text: '本月', value: () => { const n = new Date(); return [new Date(n.getFullYear(), n.getMonth(), 1), n] } },
  { text: '上月', value: () => { const n = new Date(); return [new Date(n.getFullYear(), n.getMonth() - 1, 1), new Date(n.getFullYear(), n.getMonth(), 0)] } },
  { text: '近30天', value: () => { const n = new Date(), s = new Date(); s.setDate(s.getDate() - 29); return [s, n] } },
  { text: '今年', value: () => [new Date(new Date().getFullYear(), 0, 1), new Date()] },
]
const dateParams = () => (!dateRange.value ? {} : { start: dateRange.value[0], end: dateRange.value[1] })

// ── 載入 ──────────────────────────────────────────────────
async function loadSummary() {
  loading.value.summary = true
  try { const { data } = await api.get(`/merchant/${mid.value}/revenue/summary`, { params: dateParams() }); summary.value = data }
  finally { loading.value.summary = false }
}
async function loadTrend() {
  loading.value.trend = true
  try { const { data } = await api.get(`/merchant/${mid.value}/revenue/trend`, { params: dateParams() }); trendData.value = data; renderTrend() }
  finally { loading.value.trend = false }
}
async function loadCategory() {
  loading.value.category = true
  try { const { data } = await api.get(`/merchant/${mid.value}/revenue/by-category`, { params: dateParams() }); categoryData.value = data; renderPie() }
  finally { loading.value.category = false }
}
async function loadProduct() {
  loading.value.product = true
  try { const { data } = await api.get(`/merchant/${mid.value}/revenue/by-product`, { params: dateParams() }); productRows.value = data }
  finally { loading.value.product = false }
}
async function loadOrders() {
  loading.value.orders = true
  try {
    const { data } = await api.get(`/merchant/${mid.value}/revenue/orders`, { params: { ...dateParams(), status: orderStatus.value || undefined } })
    orderRows.value = data
  } finally { loading.value.orders = false }
}
function loadAll() { loadSummary(); loadTrend(); loadCategory(); loadProduct(); loadOrders() }

// ── ECharts ───────────────────────────────────────────────
const COLORS = ['#2563EB', '#16A34A', '#EA580C', '#7C3AED', '#0891B2', '#D97706']
const catMap = {
  food: '熟食料理', drink: '飲品茶飲', dessert: '甜點烘焙', fresh: '生鮮蔬果',
  snack: '零食點心', frozen: '冷凍食品', health: '健康養生', brunch: '早午餐',
  international: '異國料理', gift: '伴手禮',
  daily: '生活日用', cleaning: '清潔衛生', beauty: '美妝保養', baby: '母嬰用品',
  pet: '寵物用品', electronics: '3C家電', home: '居家用品',
  stationery: '文具玩具', fashion: '服飾配件', sports: '運動戶外',
}

function renderTrend() {
  if (!trendChartEl.value) return
  if (!trendChart) trendChart = echarts.init(trendChartEl.value)
  const labels = trendData.value.map(d => d.date.slice(5))
  const values = trendData.value.map(d => d[trendMode.value])
  const isAmount = trendMode.value !== 'orders'
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: (p) => `${p[0].name}<br/>${isAmount ? 'NT$ ' + p[0].value.toLocaleString() : p[0].value + ' 筆'}` },
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 35, fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { formatter: isAmount ? v => 'NT$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) : v => v + '筆' } },
    series: [{
      type: 'line', data: values, smooth: true, symbol: 'circle', symbolSize: 5,
      lineStyle: { color: '#2563EB', width: 2.5 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(37,99,235,.25)' }, { offset: 1, color: 'rgba(37,99,235,.02)' }] } },
      itemStyle: { color: '#2563EB' },
    }],
  })
}

function renderPie() {
  if (!pieChartEl.value) return
  if (!pieChart) pieChart = echarts.init(pieChartEl.value)
  const pieData = categoryData.value.map((d, i) => ({
    name: catMap[d.category] || d.category,
    value: d.revenue,
    itemStyle: { color: COLORS[i % COLORS.length] },
  }))
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: p => `${p.name}<br/>NT$ ${p.value.toLocaleString()}<br/>${p.percent}%` },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie', radius: ['42%', '70%'], center: ['40%', '50%'],
      data: pieData.length ? pieData : [{ name: '暫無資料', value: 1, itemStyle: { color: '#e2e8f0' } }],
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 12 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,.2)' } },
    }],
  })
}

// ── 格式化 ────────────────────────────────────────────────
const fmt = n => `NT$ ${Number(n || 0).toLocaleString('zh-TW')}`
const fmtDate = s => new Date(s).toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
const catLabel = c => catMap[c] || c
const catType = c => ({
  food: '', drink: 'success', dessert: 'warning', fresh: 'danger',
  snack: 'info', frozen: 'info', health: 'success', brunch: '', international: 'warning', gift: 'danger',
}[c] || 'info')
const rankCls = i => i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : ''
const statusOpts = [
  { v: 'pending_payment', l: '待付款' }, { v: 'paid', l: '已付款' },
  { v: 'preparing', l: '備貨中' }, { v: 'ready_pickup', l: '待取貨' },
  { v: 'completed', l: '已完成' }, { v: 'cancelled', l: '已取消' },
]
const statusLbl = v => statusOpts.find(o => o.v === v)?.l || v
const statusType = v => ({ paid: 'success', completed: 'success', cancelled: 'danger', pending_payment: 'warning' }[v] || 'info')

function productSummary({ columns, data }) {
  return columns.map((col, i) => {
    if (i === 0) return '合計'
    if (col.property === 'qty') return data.reduce((s, r) => s + r.qty, 0) + ' 件'
    if (col.property === 'revenue') return fmt(data.reduce((s, r) => s + r.revenue, 0))
    return ''
  })
}

// ── Excel 匯出 ────────────────────────────────────────────
function exportExcel(type) {
  exporting.value.excel = true
  try {
    const wb = XLSX.utils.book_new()
    const period = dateRange.value ? `${dateRange.value[0]}～${dateRange.value[1]}` : '全部時間'
    const s = summary.value

    if (type === 'all') {
      const infoWs = XLSX.utils.aoa_to_sheet([
        ['新竹團購平台 — 商家營收報表'], ['匯出時間', new Date().toLocaleString('zh-TW')],
        ['查詢區間', period], [],
        ['總銷售額', s.gross], ['平台抽成', s.commission],
        ['商家實收', s.net], ['訂單數', s.order_count],
        ['平均客單價', s.avg_order_value],
      ])
      XLSX.utils.book_append_sheet(wb, infoWs, '報表摘要')
    }

    if (type === 'all' || type === 'product') {
      const rows = [
        ['排名', '商品名稱', '分類', '單價(NT$)', '銷售件數', '銷售金額(NT$)', '佔比'],
        ...productRows.value.map((r, i) => [
          i + 1, r.product_name, catLabel(r.category), r.group_price, r.qty, r.revenue,
          totalProductRevenue.value ? (r.revenue / totalProductRevenue.value * 100).toFixed(1) + '%' : '0%',
        ]),
        [], ['', '合計', '', '', productRows.value.reduce((s, r) => s + r.qty, 0), productRows.value.reduce((s, r) => s + r.revenue, 0), '100%'],
      ]
      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = [{ wch: 6 }, { wch: 24 }, { wch: 8 }, { wch: 10 }, { wch: 10 }, { wch: 14 }, { wch: 8 }]
      XLSX.utils.book_append_sheet(wb, ws, '商品銷售排行')
    }

    if (type === 'all' || type === 'orders') {
      const rows = [
        ['時間', '訂單編號', '消費者', '狀態', '取貨方式', '訂單金額(NT$)', '平台抽成(NT$)', '商家實收(NT$)'],
        ...orderRows.value.map(r => [
          fmtDate(r.created_at), r.order_id, r.user_name, statusLbl(r.status),
          r.delivery_type === 'pickup' ? '自取' : '配送',
          r.gross, r.commission, r.net,
        ]),
      ]
      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = [{ wch: 18 }, { wch: 38 }, { wch: 10 }, { wch: 8 }, { wch: 8 }, { wch: 14 }, { wch: 12 }, { wch: 12 }]
      XLSX.utils.book_append_sheet(wb, ws, '訂單流水帳')
    }

    if (type === 'all') {
      const trendRows = [
        ['日期', '銷售額(NT$)', '實收(NT$)', '訂單數'],
        ...trendData.value.map(d => [d.date, d.gross, d.net, d.orders]),
      ]
      const ws = XLSX.utils.aoa_to_sheet(trendRows)
      ws['!cols'] = [{ wch: 12 }, { wch: 14 }, { wch: 14 }, { wch: 8 }]
      XLSX.utils.book_append_sheet(wb, ws, '每日趨勢')
    }

    XLSX.writeFile(wb, `商家營收報表_${new Date().toISOString().slice(0, 10)}.xlsx`)
  } finally { exporting.value.excel = false }
}

// ── PDF 匯出 ──────────────────────────────────────────────
async function exportPDF() {
  exporting.value.pdf = true
  try {
    const { default: html2canvas } = await import('html2canvas')
    const { default: jsPDF } = await import('jspdf')
    const el = reportRef.value
    const canvas = await html2canvas(el, { scale: 1.5, useCORS: true, backgroundColor: '#f8fafc' })
    const imgData = canvas.toDataURL('image/jpeg', 0.92)
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()
    const imgH = (canvas.height * pageW) / canvas.width
    let y = 0
    while (y < imgH) {
      if (y > 0) pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, -y, pageW, imgH)
      y += pageH
    }
    pdf.save(`商家營收報表_${new Date().toISOString().slice(0, 10)}.pdf`)
  } finally { exporting.value.pdf = false }
}

// ── 生命週期 ──────────────────────────────────────────────
onMounted(async () => {
  await nextTick()
  loadAll()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  trendChart?.dispose(); pieChart?.dispose()
  window.removeEventListener('resize', onResize)
})
function onResize() { trendChart?.resize(); pieChart?.resize() }
</script>

<style scoped>
.rev-wrap { display: flex; flex-direction: column; gap: 24px; padding-bottom: 24px; }

/* 頁首 */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }
.page-title { display: flex; align-items: center; gap: 14px; }
.title-icon { font-size: 34px; }
.page-title h2 { font-size: 20px; font-weight: 700; margin: 0; color: #0f172a; }
.subtitle { font-size: 13px; color: #64748b; margin: 3px 0 0; }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.kpi-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; display: flex; gap: 14px; align-items: center; box-shadow: 0 1px 3px rgba(15,23,42,.05); }
.kpi-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
.kpi-label { font-size: 12px; color: #64748b; margin-bottom: 5px; }
.kpi-value { font-size: 18px; font-weight: 700; line-height: 1.2; }
.kpi-sub { font-size: 11px; color: #94a3b8; margin-top: 3px; }

/* Charts */
.chart-row { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }
.chart-el { height: 280px; }
.card-head { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; }

/* Tables */
.section-card { border-radius: 14px; }
.rank { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 12px; font-weight: 700; background: #f1f5f9; color: #64748b; }
.rank.gold { background: #fef3c7; color: #92400e; }
.rank.silver { background: #e2e8f0; color: #475569; }
.rank.bronze { background: #ffedd5; color: #c2410c; }
.mono { font-family: monospace; font-size: 12px; color: #94a3b8; }
.c-green { color: #16a34a; font-weight: 600; }
.c-red { color: #dc2626; font-weight: 600; }

@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 800px) {
  .kpi-grid { grid-template-columns: 1fr 1fr; }
  .chart-row { grid-template-columns: 1fr; }
}
@media (max-width: 500px) { .kpi-grid { grid-template-columns: 1fr; } }

@media print {
  .no-print { display: none !important; }
}
</style>
