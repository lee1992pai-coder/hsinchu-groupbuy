<template>
  <div class="revenue-wrap" ref="reportRef">

    <!-- 頁首 + 日期篩選 + 匯出 -->
    <div class="page-header">
      <div class="page-title">
        <span class="title-icon">📊</span>
        <div>
          <h2>帳務報表</h2>
          <p class="subtitle">平台收支 · 商家分潤 · 商品銷售全覽</p>
        </div>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="開始日期"
          end-placeholder="結束日期"
          format="YYYY/MM/DD"
          value-format="YYYY-MM-DD"
          :shortcuts="dateShortcuts"
          style="width:280px"
          @change="loadAll"
        />
        <el-dropdown @command="exportExcel" trigger="click">
          <el-button type="success" :loading="exporting.excel">
            <span>⬇ Excel</span>
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="all">📁 完整報表（多工作表）</el-dropdown-item>
              <el-dropdown-item command="merchant">🏪 商家明細</el-dropdown-item>
              <el-dropdown-item command="product">📦 商品銷售</el-dropdown-item>
              <el-dropdown-item command="orders">📋 訂單流水帳</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="danger" :loading="exporting.pdf" @click="exportPDF">📄 PDF</el-button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid" v-loading="loading.summary">
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#EFF6FF">💰</div>
        <div class="kpi-body">
          <div class="kpi-label">總交易金額</div>
          <div class="kpi-value">{{ fmt(summary.gross_revenue) }}</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#F0FDF4">🏦</div>
        <div class="kpi-body">
          <div class="kpi-label">平台收入（抽成）</div>
          <div class="kpi-value green">{{ fmt(summary.platform_income) }}</div>
          <div class="kpi-sub">佔比 {{ pct(summary.platform_income, summary.gross_revenue) }}</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#FFF7ED">🏪</div>
        <div class="kpi-body">
          <div class="kpi-label">商家實收</div>
          <div class="kpi-value orange">{{ fmt(summary.merchant_payout) }}</div>
          <div class="kpi-sub">佔比 {{ pct(summary.merchant_payout, summary.gross_revenue) }}</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#FDF4FF">📦</div>
        <div class="kpi-body">
          <div class="kpi-label">訂單總數</div>
          <div class="kpi-value purple">{{ summary.order_count }} 筆</div>
          <div class="kpi-sub">已付款 {{ summary.paid_order_count }} 筆</div>
        </div>
      </div>
    </div>

    <!-- 趨勢圖 + 餅圖 -->
    <div class="chart-row">
      <el-card class="chart-card" v-loading="loading.trend">
        <template #header>
          <div class="section-header">
            <span>📈 每日銷售趨勢</span>
            <el-radio-group v-model="trendMode" size="small" @change="renderTrend">
              <el-radio-button value="gross">交易額</el-radio-button>
              <el-radio-button value="commission">抽成</el-radio-button>
              <el-radio-button value="orders">訂單數</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="trendChartEl" class="chart-el" />
      </el-card>

      <el-card class="chart-card pie-wrap" v-loading="loading.category">
        <template #header><div class="section-header"><span>🥧 分類銷售佔比</span></div></template>
        <div ref="pieChartEl" class="chart-el" />
      </el-card>

      <el-card class="chart-card pie-wrap" v-loading="loading.merchant">
        <template #header><div class="section-header"><span>🏪 商家收入佔比</span></div></template>
        <div ref="merchantPieEl" class="chart-el" />
      </el-card>
    </div>

    <!-- 商家營收明細 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span>🏪 各商家營收明細</span>
          <el-tag type="info">{{ merchantRows.length }} 家商家</el-tag>
        </div>
      </template>
      <el-table :data="merchantRows" stripe border v-loading="loading.merchant"
        :default-sort="{ prop: 'gross', order: 'descending' }" show-summary :summary-method="merchantSummary">
        <el-table-column prop="rank" label="排名" width="60" align="center">
          <template #default="{ $index }">
            <span class="rank-badge" :class="rankClass($index)">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="merchant_name" label="商家名稱" min-width="130" />
        <el-table-column prop="merchant_email" label="帳號Email" min-width="160" />
        <el-table-column prop="order_count" label="訂單數" width="80" align="center" sortable />
        <el-table-column prop="gross" label="銷售總額" width="130" align="right" sortable>
          <template #default="{ row }">{{ fmt(row.gross) }}</template>
        </el-table-column>
        <el-table-column prop="commission" label="平台抽成" width="120" align="right" sortable>
          <template #default="{ row }">
            <span class="text-green">{{ fmt(row.commission) }}</span>
            <el-tag size="small" type="info" style="margin-left:4px">{{ pct(row.commission, row.gross) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payout" label="商家實收" width="130" align="right" sortable>
          <template #default="{ row }"><span class="text-orange">{{ fmt(row.payout) }}</span></template>
        </el-table-column>
        <el-table-column prop="commission_rate" label="抽成率" width="80" align="center">
          <template #default="{ row }">{{ (row.commission_rate * 100).toFixed(0) }}%</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 商品銷售排行 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span>📦 商品銷售排行</span>
          <el-tag type="info">{{ productRows.length }} 項商品</el-tag>
        </div>
      </template>
      <el-table :data="productRows" stripe border v-loading="loading.product"
        :default-sort="{ prop: 'revenue', order: 'descending' }" show-summary :summary-method="productSummary">
        <el-table-column prop="rank" label="排名" width="60" align="center">
          <template #default="{ $index }">
            <span class="rank-badge" :class="rankClass($index)">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名稱" min-width="160" />
        <el-table-column prop="merchant_name" label="所屬商家" width="120" />
        <el-table-column prop="category" label="分類" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="catType(row.category)">{{ catLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="group_price" label="團購價" width="100" align="right">
          <template #default="{ row }">NT$ {{ row.group_price }}</template>
        </el-table-column>
        <el-table-column prop="qty" label="銷售數量" width="90" align="center" sortable>
          <template #default="{ row }"><strong>{{ row.qty }}</strong> 件</template>
        </el-table-column>
        <el-table-column prop="revenue" label="銷售金額" width="130" align="right" sortable>
          <template #default="{ row }">{{ fmt(row.revenue) }}</template>
        </el-table-column>
        <el-table-column label="佔比" width="120" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="totalRevenue ? Math.round((row.revenue / totalRevenue) * 100) : 0"
              :stroke-width="6"
              :show-text="true"
              :format="(p) => p + '%'"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 訂單流水帳 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span>📋 訂單流水帳</span>
          <div style="display:flex;gap:8px;align-items:center">
            <el-select v-model="orderFilter.merchant" clearable placeholder="全部商家" style="width:130px" @change="loadOrders">
              <el-option v-for="m in merchantRows" :key="m.merchant_id" :label="m.merchant_name" :value="m.merchant_id" />
            </el-select>
            <el-select v-model="orderFilter.status" clearable placeholder="全部狀態" style="width:120px" @change="loadOrders">
              <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
            <el-tag type="info">最近 200 筆</el-tag>
          </div>
        </div>
      </template>
      <el-table :data="orderRows" stripe border v-loading="loading.orders" max-height="420">
        <el-table-column prop="created_at" label="建立時間" width="165">
          <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="order_id" label="訂單編號" width="110">
          <template #default="{ row }">
            <span class="mono">{{ row.order_id.slice(0,8) }}…</span>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="消費者" width="100" />
        <el-table-column prop="merchant_name" label="商家" width="120" />
        <el-table-column prop="status" label="狀態" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="delivery_type" label="取貨方式" width="80" align="center">
          <template #default="{ row }">{{ row.delivery_type === 'pickup' ? '自取' : '配送' }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="訂單金額" width="110" align="right">
          <template #default="{ row }">{{ fmt(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="commission" label="平台抽成" width="110" align="right">
          <template #default="{ row }"><span class="text-green">{{ fmt(row.commission) }}</span></template>
        </el-table-column>
        <el-table-column prop="merchant_payout" label="商家實收" width="110" align="right">
          <template #default="{ row }"><span class="text-orange">{{ fmt(row.merchant_payout) }}</span></template>
        </el-table-column>
      </el-table>
    </el-card>

  </div>
</template>

<script setup>
import { onMounted, onUnmounted, nextTick, ref, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import * as XLSX from 'xlsx'
import api from '../api'

echarts.use([LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

// ── 狀態 ──────────────────────────────────────────────────
const reportRef = ref(null)
const trendChartEl = ref(null)
const pieChartEl = ref(null)
const merchantPieEl = ref(null)
let trendChart = null, pieChart = null, merchantPieChart = null

const dateRange = ref(null)
const trendMode = ref('gross')
const exporting = ref({ excel: false, pdf: false })
const loading = ref({ summary: false, merchant: false, product: false, orders: false, trend: false, category: false })
const summary = ref({ gross_revenue: 0, platform_income: 0, merchant_payout: 0, order_count: 0, paid_order_count: 0 })
const merchantRows = ref([])
const productRows = ref([])
const orderRows = ref([])
const trendData = ref([])
const categoryData = ref([])
const orderFilter = ref({ merchant: null, status: null })

const totalRevenue = computed(() => productRows.value.reduce((s, r) => s + r.revenue, 0))

// ── 日期快捷 ─────────────────────────────────────────────
const dateShortcuts = [
  { text: '本月', value: () => { const n = new Date(); return [new Date(n.getFullYear(), n.getMonth(), 1), n] } },
  { text: '上月', value: () => { const n = new Date(); return [new Date(n.getFullYear(), n.getMonth() - 1, 1), new Date(n.getFullYear(), n.getMonth(), 0)] } },
  { text: '近 7 天', value: () => { const n = new Date(); const s = new Date(); s.setDate(s.getDate() - 6); return [s, n] } },
  { text: '近 30 天', value: () => { const n = new Date(); const s = new Date(); s.setDate(s.getDate() - 29); return [s, n] } },
  { text: '今年', value: () => [new Date(new Date().getFullYear(), 0, 1), new Date()] },
]

// ── 查詢 params ───────────────────────────────────────────
function dateParams() {
  if (!dateRange.value) return {}
  return { start: dateRange.value[0], end: dateRange.value[1] }
}

// ── 資料載入 ──────────────────────────────────────────────
async function loadSummary() {
  loading.value.summary = true
  try { const { data } = await api.get('/admin/revenue/summary', { params: dateParams() }); summary.value = data }
  finally { loading.value.summary = false }
}

async function loadMerchant() {
  loading.value.merchant = true
  try { const { data } = await api.get('/admin/revenue/by-merchant', { params: dateParams() }); merchantRows.value = data }
  finally { loading.value.merchant = false }
}

async function loadProduct() {
  loading.value.product = true
  try { const { data } = await api.get('/admin/revenue/by-product', { params: dateParams() }); productRows.value = data }
  finally { loading.value.product = false }
}

async function loadOrders() {
  loading.value.orders = true
  try {
    const { data } = await api.get('/admin/revenue/orders', {
      params: { ...dateParams(), merchant_id: orderFilter.value.merchant || undefined, status: orderFilter.value.status || undefined }
    })
    orderRows.value = data
  } finally { loading.value.orders = false }
}

async function loadTrend() {
  loading.value.trend = true
  try { const { data } = await api.get('/admin/revenue/trend', { params: dateParams() }); trendData.value = data; renderTrend() }
  finally { loading.value.trend = false }
}
async function loadCategory() {
  loading.value.category = true
  try { const { data } = await api.get('/admin/revenue/by-category', { params: dateParams() }); categoryData.value = data; renderPie(); renderMerchantPie() }
  finally { loading.value.category = false }
}
function loadAll() { loadSummary(); loadMerchant(); loadProduct(); loadOrders(); loadTrend(); loadCategory() }

// ── ECharts ───────────────────────────────────────────────
const COLORS = ['#2563EB', '#16A34A', '#EA580C', '#7C3AED', '#0891B2', '#D97706', '#DB2777']
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
  const isAmt = trendMode.value !== 'orders'
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: p => `${p[0].name}<br/>${isAmt ? 'NT$ ' + p[0].value.toLocaleString() : p[0].value + ' 筆'}` },
    grid: { left: 65, right: 20, top: 20, bottom: 45 },
    xAxis: { type: 'category', data: trendData.value.map(d => d.date.slice(5)), axisLabel: { rotate: 35, fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { formatter: isAmt ? v => 'NT$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) : v => v + '筆' } },
    series: [{
      type: 'line', data: trendData.value.map(d => d[trendMode.value]), smooth: true,
      lineStyle: { color: '#2563EB', width: 2.5 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(37,99,235,.3)' }, { offset: 1, color: 'rgba(37,99,235,.02)' }] } },
      itemStyle: { color: '#2563EB' }, symbol: 'circle', symbolSize: 5,
    }],
  })
}

function renderPie() {
  if (!pieChartEl.value) return
  if (!pieChart) pieChart = echarts.init(pieChartEl.value)
  const data = categoryData.value.map((d, i) => ({ name: catMap[d.category] || d.category, value: d.revenue, itemStyle: { color: COLORS[i % COLORS.length] } }))
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: p => `${p.name}<br/>NT$ ${p.value.toLocaleString()}<br/>${p.percent}%` },
    legend: { orient: 'vertical', right: 5, top: 'center', textStyle: { fontSize: 11 } },
    series: [{ type: 'pie', radius: ['42%', '68%'], center: ['38%', '50%'], data: data.length ? data : [{ name: '暫無', value: 1, itemStyle: { color: '#e2e8f0' } }], label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,.2)' } } }],
  })
}

function renderMerchantPie() {
  if (!merchantPieEl.value) return
  if (!merchantPieChart) merchantPieChart = echarts.init(merchantPieEl.value)
  const top6 = [...merchantRows.value].sort((a, b) => b.gross - a.gross).slice(0, 6)
  const data = top6.map((m, i) => ({ name: m.merchant_name, value: m.gross, itemStyle: { color: COLORS[i % COLORS.length] } }))
  merchantPieChart.setOption({
    tooltip: { trigger: 'item', formatter: p => `${p.name}<br/>NT$ ${p.value.toLocaleString()}<br/>${p.percent}%` },
    legend: { orient: 'vertical', right: 5, top: 'center', textStyle: { fontSize: 11 } },
    series: [{ type: 'pie', radius: ['42%', '68%'], center: ['38%', '50%'], data: data.length ? data : [{ name: '暫無', value: 1, itemStyle: { color: '#e2e8f0' } }], label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 }, emphasis: { itemStyle: { shadowBlur: 8 } } }],
  })
}

function onResize() { trendChart?.resize(); pieChart?.resize(); merchantPieChart?.resize() }

// ── 格式化 ────────────────────────────────────────────────
const fmt = (n) => `NT$ ${Number(n || 0).toLocaleString('zh-TW')}`
const pct = (a, b) => b ? (a / b * 100).toFixed(1) + '%' : '0%'
const fmtDate = (s) => new Date(s).toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
const fmtRaw = (n) => Number(n || 0).toLocaleString('zh-TW')

// ── 商品分類 ──────────────────────────────────────────────
const catMap = {
  food: '熟食料理', drink: '飲品茶飲', dessert: '甜點烘焙', fresh: '生鮮蔬果',
  snack: '零食點心', frozen: '冷凍食品', health: '健康養生', brunch: '早午餐',
  international: '異國料理', gift: '伴手禮',
  daily: '生活日用', cleaning: '清潔衛生', beauty: '美妝保養', baby: '母嬰用品',
  pet: '寵物用品', electronics: '3C家電', home: '居家用品',
  stationery: '文具玩具', fashion: '服飾配件', sports: '運動戶外',
}
const catLabel = (c) => catMap[c] || c
const catType = (c) => ({
  food: '', drink: 'success', dessert: 'warning', fresh: 'danger',
  snack: 'info', frozen: 'info', health: 'success', brunch: '', international: 'warning', gift: 'danger',
}[c] || 'info')

// ── 訂單狀態 ──────────────────────────────────────────────
const statusOptions = [
  { value: 'pending_payment', label: '待付款' }, { value: 'paid', label: '已付款' },
  { value: 'preparing', label: '備貨中' }, { value: 'ready_pickup', label: '待取貨' },
  { value: 'completed', label: '已完成' }, { value: 'cancelled', label: '已取消' },
]
const statusLabel = (s) => statusOptions.find(o => o.value === s)?.label || s
const statusTagType = (s) => ({ paid: 'success', completed: 'success', cancelled: 'danger', pending_payment: 'warning' }[s] || 'info')

// ── 排名樣式 ──────────────────────────────────────────────
const rankClass = (i) => i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : ''

// ── 表格合計 ──────────────────────────────────────────────
function merchantSummary({ columns, data }) {
  return columns.map((col, i) => {
    if (i === 0) return '合計'
    if (col.property === 'order_count') return data.reduce((s, r) => s + r.order_count, 0) + ' 筆'
    if (col.property === 'gross') return fmt(data.reduce((s, r) => s + r.gross, 0))
    if (col.property === 'commission') return fmt(data.reduce((s, r) => s + r.commission, 0))
    if (col.property === 'payout') return fmt(data.reduce((s, r) => s + r.payout, 0))
    return ''
  })
}

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
  exporting.value = true
  try {
    const wb = XLSX.utils.book_new()
    const period = dateRange.value ? `${dateRange.value[0]}～${dateRange.value[1]}` : '全部時間'

    if (type === 'all' || type === 'merchant') {
      const rows = [
        ['商家名稱', '帳號Email', '訂單數', '銷售總額(NT$)', '平台抽成(NT$)', '抽成率', '商家實收(NT$)'],
        ...merchantRows.value.map(r => [
          r.merchant_name, r.merchant_email, r.order_count,
          r.gross, r.commission,
          (r.commission_rate * 100).toFixed(0) + '%',
          r.payout,
        ]),
        [],
        ['合計', '',
          merchantRows.value.reduce((s, r) => s + r.order_count, 0),
          merchantRows.value.reduce((s, r) => s + r.gross, 0),
          merchantRows.value.reduce((s, r) => s + r.commission, 0),
          '', merchantRows.value.reduce((s, r) => s + r.payout, 0),
        ],
      ]
      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = [{ wch: 16 }, { wch: 24 }, { wch: 8 }, { wch: 14 }, { wch: 14 }, { wch: 8 }, { wch: 14 }]
      XLSX.utils.book_append_sheet(wb, ws, '商家營收明細')
    }

    if (type === 'all' || type === 'product') {
      const rows = [
        ['排名', '商品名稱', '所屬商家', '分類', '團購價(NT$)', '銷售數量(件)', '銷售金額(NT$)', '佔比'],
        ...productRows.value.map((r, i) => [
          i + 1, r.product_name, r.merchant_name, catLabel(r.category),
          r.group_price, r.qty, r.revenue,
          totalRevenue.value ? (r.revenue / totalRevenue.value * 100).toFixed(1) + '%' : '0%',
        ]),
        [],
        ['', '合計', '', '', '',
          productRows.value.reduce((s, r) => s + r.qty, 0),
          productRows.value.reduce((s, r) => s + r.revenue, 0),
          '100%',
        ],
      ]
      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = [{ wch: 6 }, { wch: 22 }, { wch: 16 }, { wch: 8 }, { wch: 10 }, { wch: 12 }, { wch: 14 }, { wch: 8 }]
      XLSX.utils.book_append_sheet(wb, ws, '商品銷售排行')
    }

    if (type === 'all' || type === 'orders') {
      const rows = [
        ['建立時間', '訂單編號', '消費者', '消費者Email', '商家', '狀態', '取貨方式', '訂單金額(NT$)', '平台抽成(NT$)', '商家實收(NT$)'],
        ...orderRows.value.map(r => [
          fmtDate(r.created_at), r.order_id,
          r.user_name, r.user_email, r.merchant_name,
          statusLabel(r.status),
          r.delivery_type === 'pickup' ? '自取' : '配送',
          r.total_amount, r.commission, r.merchant_payout,
        ]),
      ]
      const ws = XLSX.utils.aoa_to_sheet(rows)
      ws['!cols'] = [{ wch: 18 }, { wch: 38 }, { wch: 10 }, { wch: 24 }, { wch: 16 }, { wch: 8 }, { wch: 8 }, { wch: 14 }, { wch: 12 }, { wch: 12 }]
      XLSX.utils.book_append_sheet(wb, ws, '訂單流水帳')
    }

    if (type === 'all') {
      const infoRows = [
        ['新竹團購平台 — 帳務報表'],
        ['匯出時間', new Date().toLocaleString('zh-TW')],
        ['查詢區間', period],
        [],
        ['總交易金額', summary.value.gross_revenue],
        ['平台收入', summary.value.platform_income],
        ['商家實收', summary.value.merchant_payout],
        ['訂單總數', summary.value.order_count],
        ['已付款訂單', summary.value.paid_order_count],
      ]
      const ws = XLSX.utils.aoa_to_sheet(infoRows)
      ws['!cols'] = [{ wch: 16 }, { wch: 20 }]
      XLSX.utils.book_append_sheet(wb, ws, '報表說明')
      // 把說明移到第一頁
      wb.SheetNames.unshift(wb.SheetNames.pop())
    }

    const filename = `新竹團購_帳務報表_${new Date().toISOString().slice(0, 10)}.xlsx`
    XLSX.writeFile(wb, filename)
  } finally {
    exporting.value = false
  }
}

// ── PDF 匯出 ──────────────────────────────────────────────
async function exportPDF() {
  exporting.value.pdf = true
  try {
    const { default: html2canvas } = await import('html2canvas')
    const { default: jsPDF } = await import('jspdf')
    const canvas = await html2canvas(reportRef.value, { scale: 1.5, useCORS: true, backgroundColor: '#f8fafc' })
    const imgData = canvas.toDataURL('image/jpeg', 0.92)
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pw = pdf.internal.pageSize.getWidth()
    const ph = pdf.internal.pageSize.getHeight()
    const ih = (canvas.height * pw) / canvas.width
    let y = 0
    while (y < ih) { if (y > 0) pdf.addPage(); pdf.addImage(imgData, 'JPEG', 0, -y, pw, ih); y += ph }
    pdf.save(`平台帳務報表_${new Date().toISOString().slice(0, 10)}.pdf`)
  } finally { exporting.value.pdf = false }
}

onMounted(async () => {
  await nextTick()
  loadAll()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  trendChart?.dispose(); pieChart?.dispose(); merchantPieChart?.dispose()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.revenue-wrap { display: flex; flex-direction: column; gap: 24px; }

/* 頁首 */
.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  flex-wrap: wrap; gap: 16px;
}
.page-title { display: flex; align-items: center; gap: 14px; }
.title-icon { font-size: 36px; }
.page-title h2 { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0; }
.subtitle { font-size: 13px; color: #64748b; margin: 4px 0 0; }
.header-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: 20px 20px; display: flex; gap: 16px; align-items: center;
  box-shadow: 0 1px 3px rgba(15,23,42,.06);
  transition: box-shadow .2s;
}
.kpi-card:hover { box-shadow: 0 4px 16px rgba(15,23,42,.10); }
.kpi-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.kpi-body { flex: 1; }
.kpi-label { font-size: 13px; color: #64748b; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.kpi-value.green { color: #16a34a; }
.kpi-value.orange { color: #ea580c; }
.kpi-value.purple { color: #7c3aed; }
.kpi-sub { font-size: 12px; color: #94a3b8; margin-top: 4px; }

/* Section cards */
.section-card { border-radius: 14px; }
.section-header { display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: 600; }

/* Rank badge */
.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 50%;
  font-size: 12px; font-weight: 700;
  background: #f1f5f9; color: #64748b;
}
.rank-badge.gold { background: #fef3c7; color: #92400e; }
.rank-badge.silver { background: #f1f5f9; color: #475569; }
.rank-badge.bronze { background: #fef3c7; color: #b45309; opacity: .7; }

.text-green { color: #16a34a; font-weight: 600; }
.text-orange { color: #ea580c; font-weight: 600; }
.mono { font-family: monospace; font-size: 12px; color: #64748b; }

@media (max-width: 900px) {
  .kpi-grid { grid-template-columns: 1fr 1fr; }
}
/* 圖表 */
.chart-row { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 16px; }
.chart-card { border-radius: 14px; }
.chart-el { height: 280px; }
.pie-wrap .chart-el { height: 280px; }

@media (max-width: 1100px) { .chart-row { grid-template-columns: 1fr 1fr; } }
@media (max-width: 700px) { .chart-row { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .kpi-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 500px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; }
}
</style>
