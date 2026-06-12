<template>
  <div v-if="product" class="detail-wrap">
    <el-row :gutter="32">
      <!-- 圖片區 -->
      <el-col :span="12">
        <el-carousel height="380px" :autoplay="false" class="img-carousel">
          <el-carousel-item v-for="img in allImages" :key="img">
            <img :src="img" class="detail-img" />
          </el-carousel-item>
        </el-carousel>
      </el-col>

      <!-- 資訊區 -->
      <el-col :span="12">
        <div class="tags-row">
          <el-tag v-for="tag in product.tags" :key="tag" type="warning" effect="dark">{{ tag }}</el-tag>
        </div>
        <h1 class="product-name">{{ product.name }}</h1>
        <div class="price-block">
          <span class="group-price">NT$ {{ selectedVariantPrice }}</span>
          <span class="original">NT$ {{ product.original_price }}</span>
        </div>

        <!-- 規格選擇 -->
        <div v-if="variants.length" class="variant-section">
          <div class="variant-label">規格選擇</div>
          <div class="variant-options">
            <div
              v-for="v in variants"
              :key="v.id"
              class="variant-btn"
              :class="{ selected: selectedVariant?.id === v.id, disabled: v.stock === 0 }"
              @click="v.stock > 0 && (selectedVariant = v)"
            >
              {{ v.name }}
              <span v-if="v.extra_price > 0" class="extra">+NT${{ v.extra_price }}</span>
              <span v-if="v.stock === 0" class="sold-out">售完</span>
            </div>
          </div>
        </div>

        <!-- 數量 -->
        <div class="qty-section">
          <span class="variant-label">數量</span>
          <el-input-number v-model="quantity" :min="1" :max="maxStock" size="large" />
          <span class="stock-hint">庫存 {{ maxStock }} 件</span>
        </div>

        <!-- 成團進度 -->
        <div v-if="activeGroupBuy" class="group-progress">
          <div class="gp-header">
            <span>🔥 拼團中 — 還差 {{ activeGroupBuy.target_count - activeGroupBuy.current_count }} 件成團</span>
            <span class="countdown">{{ timeLeft }}</span>
          </div>
          <el-progress :percentage="groupPct" :stroke-width="12" />
        </div>

        <!-- 加入購物車 -->
        <div class="action-row">
          <el-button type="primary" size="large" style="flex:1" @click="addToCart">
            加入購物車
          </el-button>
          <el-button size="large" style="flex:1" type="success" @click="joinGroupBuy" v-if="activeGroupBuy">
            立即參團
          </el-button>
        </div>

        <div class="meta-row">
          <span>最低成團：{{ product.min_group_size }} 件</span>
          <span>分類：{{ product.category }}</span>
        </div>
      </el-col>
    </el-row>

    <!-- 商品描述 -->
    <el-card class="desc-card">
      <template #header>商品介紹</template>
      <p>{{ product.description || '暫無說明' }}</p>
    </el-card>
  </div>

  <div v-else-if="loading" class="loading">
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

const product = ref(null)
const variants = ref([])
const activeGroupBuy = ref(null)
const selectedVariant = ref(null)
const quantity = ref(1)
const loading = ref(true)
const timeLeft = ref('')
let timer = null

const allImages = computed(() => {
  const imgs = product.value?.images?.length ? product.value.images : []
  if (product.value?.image_url) imgs.unshift(product.value.image_url)
  return imgs.length ? imgs : ['https://placehold.co/600x400/f0f4ff/409eff?text=商品圖']
})

const selectedVariantPrice = computed(() => {
  const base = product.value?.group_price || 0
  return base + (selectedVariant.value?.extra_price || 0)
})

const maxStock = computed(() => selectedVariant.value?.stock ?? product.value?.stock ?? 99)

const groupPct = computed(() => {
  if (!activeGroupBuy.value) return 0
  return Math.min(100, Math.round(
    (activeGroupBuy.value.current_count / activeGroupBuy.value.target_count) * 100
  ))
})

function updateCountdown() {
  if (!activeGroupBuy.value) return
  const diff = dayjs(activeGroupBuy.value.deadline).diff(dayjs())
  if (diff <= 0) { timeLeft.value = '已截止'; return }
  const d = dayjs.duration(diff)
  timeLeft.value = `${d.hours()}h ${d.minutes()}m ${d.seconds()}s`
}

function addToCart() {
  if (!authStore.token) return router.push('/login')
  cartStore.addItem(
    { ...product.value, group_price: selectedVariantPrice.value },
    quantity.value,
    selectedVariant.value?.id,
  )
  ElMessage.success('已加入購物車')
}

async function joinGroupBuy() {
  if (!authStore.token) return router.push('/login')
  try {
    await api.post(`/group-buys/${activeGroupBuy.value.id}/join`, {
      user_id: authStore.user?.id,
      quantity: quantity.value,
      pickup_location_id: '新竹火車站前廣場',
    })
    ElMessage.success('已成功參團！')
    activeGroupBuy.value.current_count += quantity.value
  } catch {
    ElMessage.error('參團失敗，請稍後再試')
  }
}

onMounted(async () => {
  const pid = route.params.id
  const [pRes, vRes, gbRes] = await Promise.all([
    api.get(`/products/${pid}`),
    api.get(`/products/${pid}/variants`),
    api.get('/group-buys/').catch(() => ({ data: [] })),
  ])
  product.value = pRes.data
  variants.value = vRes.data
  if (variants.value.length) selectedVariant.value = variants.value[0]
  activeGroupBuy.value = gbRes.data.find(
    (gb) => gb.product_id === pid && gb.status === 'open'
  ) || null
  loading.value = false
  if (activeGroupBuy.value) {
    updateCountdown()
    timer = setInterval(updateCountdown, 1000)
  }
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.detail-wrap { max-width: 1000px; margin: 0 auto; }
.detail-img { width: 100%; height: 380px; object-fit: cover; border-radius: 12px; }
.img-carousel { border-radius: 12px; overflow: hidden; }
.tags-row { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.product-name { font-size: 24px; font-weight: bold; margin-bottom: 12px; line-height: 1.4; }
.price-block { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px; }
.group-price { font-size: 32px; font-weight: bold; color: #f56c6c; }
.original { font-size: 16px; color: #c0c4cc; text-decoration: line-through; }

.variant-section { margin-bottom: 20px; }
.variant-label { font-size: 14px; font-weight: 600; color: #606266; margin-bottom: 8px; }
.variant-options { display: flex; flex-wrap: wrap; gap: 8px; }
.variant-btn {
  padding: 6px 16px; border-radius: 8px; border: 2px solid #e4e7ed;
  cursor: pointer; font-size: 14px; transition: all .2s; position: relative;
}
.variant-btn.selected { border-color: #409eff; color: #409eff; background: #ecf5ff; }
.variant-btn.disabled { opacity: .4; cursor: not-allowed; }
.extra { font-size: 11px; color: #e6a23c; margin-left: 4px; }
.sold-out { font-size: 11px; color: #c0c4cc; margin-left: 4px; }

.qty-section { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.stock-hint { font-size: 13px; color: #909399; }

.group-progress { background: #fff7e6; border-radius: 10px; padding: 14px; margin-bottom: 20px; }
.gp-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }
.countdown { color: #e6a23c; font-weight: 600; }

.action-row { display: flex; gap: 12px; margin-bottom: 16px; }

.meta-row { display: flex; gap: 20px; font-size: 13px; color: #909399; }

.desc-card { margin-top: 28px; }
.loading { padding: 40px; }
</style>
