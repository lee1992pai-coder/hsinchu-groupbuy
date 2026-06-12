<template>
  <div v-if="gb && product" class="detail-wrap">
    <el-row :gutter="32">
      <!-- 圖片 -->
      <el-col :span="11">
        <img
          :src="product.image_url || 'https://placehold.co/500x380/f0f4ff/409eff?text=拼團商品'"
          class="main-img"
        />
      </el-col>

      <!-- 資訊 -->
      <el-col :span="13">
        <el-tag type="danger" effect="dark" class="gb-badge">🔥 限時拼團</el-tag>
        <h1 class="product-name">{{ product.name }}</h1>

        <div class="price-row">
          <span class="group-price">NT$ {{ product.group_price }}</span>
          <span class="original">NT$ {{ product.original_price }}</span>
          <el-tag type="danger" size="small">
            {{ Math.round(product.group_price / product.original_price * 10) }} 折
          </el-tag>
        </div>

        <!-- 拼團進度 -->
        <div class="progress-block">
          <div class="progress-header">
            <span class="progress-label">
              已有 <b>{{ gb.current_count }}</b> 人參團，目標 <b>{{ gb.target_count }}</b> 人
            </span>
            <span class="countdown" :class="{ urgent: isUrgent }">⏰ {{ timeLeft }}</span>
          </div>
          <el-progress
            :percentage="progressPct"
            :stroke-width="16"
            :status="progressPct >= 100 ? 'success' : undefined"
          />
          <div class="progress-hint">
            還差 <b>{{ Math.max(0, gb.target_count - gb.current_count) }}</b> 人即可成團！
          </div>
        </div>

        <!-- 規格 -->
        <div v-if="variants.length" class="variant-section">
          <div class="section-label">選擇規格</div>
          <div class="variant-options">
            <div
              v-for="v in variants" :key="v.id"
              class="variant-btn"
              :class="{ selected: selected?.id === v.id, disabled: v.stock === 0 }"
              @click="v.stock > 0 && (selected = v)"
            >
              {{ v.name }}
              <span v-if="v.extra_price > 0" class="extra">+NT${{ v.extra_price }}</span>
            </div>
          </div>
        </div>

        <!-- 數量 -->
        <div class="qty-row">
          <span class="section-label">數量</span>
          <el-input-number v-model="qty" :min="1" :max="product.stock" size="large" />
        </div>

        <!-- 動作 -->
        <div class="action-row">
          <el-button type="primary" size="large" style="flex:1" @click="joinGroup" :loading="joining">
            立即參團
          </el-button>
          <el-button size="large" @click="addCart">加入購物車</el-button>
        </div>

        <div class="meta-info">
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="成團門檻">{{ product.min_group_size }} 件</el-descriptions-item>
            <el-descriptions-item label="庫存">{{ product.stock }} 件</el-descriptions-item>
            <el-descriptions-item label="截止時間" :span="2">
              {{ formatDate(gb.deadline) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>

    <!-- 商品說明 -->
    <el-card class="desc-card">
      <template #header>商品介紹</template>
      <p>{{ product.description || '暫無說明' }}</p>
    </el-card>
  </div>

  <div v-else class="loading-wrap">
    <el-skeleton :rows="6" animated />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)
import api from '../api'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const gb = ref(null)
const product = ref(null)
const variants = ref([])
const selected = ref(null)
const qty = ref(1)
const joining = ref(false)
const timeLeft = ref('')
let timer = null

const progressPct = computed(() =>
  gb.value ? Math.min(100, Math.round(gb.value.current_count / gb.value.target_count * 100)) : 0
)
const isUrgent = computed(() => {
  if (!gb.value) return false
  return dayjs(gb.value.deadline).diff(dayjs(), 'hour') < 3
})

function updateCountdown() {
  if (!gb.value) return
  const diff = dayjs(gb.value.deadline).diff(dayjs())
  if (diff <= 0) { timeLeft.value = '已截止'; return }
  const d = dayjs.duration(diff)
  timeLeft.value = `${d.hours()}h ${d.minutes()}m ${d.seconds()}s`
}

const formatDate = (d) => dayjs(d).format('YYYY/MM/DD HH:mm')

async function joinGroup() {
  if (!authStore.token) return router.push('/login')
  joining.value = true
  try {
    await api.post(`/group-buys/${gb.value.id}/join`, {
      user_id: authStore.user?.id || '00000000-0000-0000-0000-000000000001',
      quantity: qty.value,
      pickup_location_id: '新竹火車站前廣場',
    })
    gb.value.current_count += qty.value
    ElMessage.success('🎉 已成功參團！成團後會推播通知您')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '參團失敗')
  } finally {
    joining.value = false
  }
}

function addCart() {
  if (!product.value) return
  cartStore.addItem(
    { ...product.value, group_price: product.value.group_price + (selected.value?.extra_price || 0) },
    qty.value,
    selected.value?.id,
    selected.value?.name,
  )
  ElMessage.success('已加入購物車')
}

onMounted(async () => {
  const id = route.params.id
  const { data: gbData } = await api.get(`/group-buys/${id}`)
  gb.value = gbData
  const [pRes, vRes] = await Promise.all([
    api.get(`/products/${gbData.product_id}`),
    api.get(`/products/${gbData.product_id}/variants`),
  ])
  product.value = pRes.data
  variants.value = vRes.data
  if (variants.value.length) selected.value = variants.value[0]
  updateCountdown()
  timer = setInterval(updateCountdown, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.detail-wrap { max-width: 1000px; margin: 0 auto; }
.main-img { width: 100%; border-radius: 14px; object-fit: cover; max-height: 400px; }
.gb-badge { margin-bottom: 12px; }
.product-name { font-size: 24px; font-weight: bold; margin: 10px 0; line-height: 1.4; }
.price-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px; }
.group-price { font-size: 32px; font-weight: bold; color: #f56c6c; }
.original { font-size: 15px; color: #c0c4cc; text-decoration: line-through; }

.progress-block {
  background: linear-gradient(135deg, #fff7e6, #fffbe6);
  border: 1px solid #ffd666; border-radius: 12px;
  padding: 16px; margin-bottom: 20px;
}
.progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.progress-label { font-size: 14px; }
.countdown { font-size: 14px; font-weight: bold; color: #e6a23c; }
.countdown.urgent { color: #f56c6c; animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: .5; } }
.progress-hint { margin-top: 8px; font-size: 13px; color: #606266; text-align: center; }

.section-label { font-size: 14px; font-weight: 600; color: #606266; margin-bottom: 8px; display: block; }
.variant-section { margin-bottom: 16px; }
.variant-options { display: flex; flex-wrap: wrap; gap: 8px; }
.variant-btn {
  padding: 7px 16px; border-radius: 8px; border: 2px solid #e4e7ed;
  cursor: pointer; font-size: 14px; transition: all .15s;
}
.variant-btn.selected { border-color: #409eff; color: #409eff; background: #ecf5ff; }
.variant-btn.disabled { opacity: .4; cursor: not-allowed; }
.extra { font-size: 11px; color: #e6a23c; }

.qty-row { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.action-row { display: flex; gap: 12px; margin-bottom: 20px; }
.meta-info { margin-bottom: 20px; }
.desc-card { margin-top: 28px; }
.loading-wrap { padding: 40px; }
</style>
