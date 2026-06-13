<template>
  <div v-if="product" class="detail-page">

    <!-- 麵包屑 -->
    <nav class="breadcrumb">
      <router-link to="/">首頁</router-link>
      <span class="sep">›</span>
      <router-link to="/products">商品列表</router-link>
      <span class="sep">›</span>
      <span class="current">{{ product.name }}</span>
    </nav>

    <div class="detail-body">
      <!-- ── 左：圖片區 ── -->
      <div class="img-section">
        <!-- 主圖 -->
        <div class="main-img-wrap">
          <img :src="displayImg" :alt="product.name" class="main-img" />
          <div class="img-discount-badge">{{ discountPct }}折</div>
          <div class="img-save-badge" v-if="savingAmt > 0">省 NT${{ savingAmt }}</div>
          <div class="img-tags">
            <span v-for="tag in product.tags" :key="tag" class="img-tag">{{ tag }}</span>
          </div>
        </div>
        <!-- 縮圖列 -->
        <div class="thumb-strip" v-if="allImages.length > 1">
          <div
            v-for="(img, i) in allImages" :key="i"
            class="thumb"
            :class="{ active: displayImg === img }"
            @click="displayImg = img"
          >
            <img :src="img" :alt="`圖片${i+1}`" />
          </div>
        </div>
        <!-- 分享列 -->
        <div class="share-row">
          <span class="share-label">分享：</span>
          <button class="share-btn" @click="copyLink">📋 複製連結</button>
        </div>
      </div>

      <!-- ── 右：購買資訊區 ── -->
      <div class="buy-section">

        <!-- 商家 -->
        <div class="merchant-badge" v-if="product.merchant_name">
          <span>🏪</span> {{ product.merchant_name }}
        </div>

        <!-- 商品名稱 -->
        <h1 class="product-name">{{ product.name }}</h1>

        <!-- 評分 (靜態佔位) -->
        <div class="rating-row">
          <span class="stars">★★★★☆</span>
          <span class="rating-count">4.2（{{ ratingCount }} 則評價）</span>
          <span class="sold-count" v-if="soldHint">已售 {{ soldHint }}</span>
        </div>

        <!-- 價格區塊 -->
        <div class="price-box">
          <div class="price-main-row">
            <span class="price-label">團購價</span>
            <span class="group-price">NT$<em>{{ selectedVariantPrice }}</em></span>
          </div>
          <div class="price-sub-row">
            <span class="original-price">原價 NT${{ product.original_price }}</span>
            <span class="saving-tag">省 NT${{ savingAmt }} ({{ discountPct }}折)</span>
          </div>
        </div>

        <!-- 配送資訊列 -->
        <div class="delivery-row">
          <div class="delivery-item">
            <span class="d-icon">📦</span>
            <div>
              <div class="d-title">新竹限定自取</div>
              <div class="d-desc">多點取貨，方便靈活</div>
            </div>
          </div>
          <div class="delivery-item">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-title">平台交易保障</div>
              <div class="d-desc">成團後才付款</div>
            </div>
          </div>
          <div class="delivery-item">
            <span class="d-icon">👥</span>
            <div>
              <div class="d-title">最少 {{ product.min_group_size }} 件成團</div>
              <div class="d-desc">人多更優惠</div>
            </div>
          </div>
        </div>

        <!-- 規格選擇 -->
        <div v-if="variants.length" class="option-group">
          <div class="option-label">選擇規格</div>
          <div class="option-btns">
            <button
              v-for="v in variants"
              :key="v.id"
              class="option-btn"
              :class="{
                selected: selectedVariant?.id === v.id,
                'sold-out': v.stock === 0
              }"
              @click="v.stock > 0 && (selectedVariant = v)"
            >
              <span class="opt-name">{{ v.name }}</span>
              <span class="opt-extra" v-if="v.extra_price > 0">+NT${{ v.extra_price }}</span>
              <span class="opt-extra neg" v-else-if="v.extra_price < 0">-NT${{ Math.abs(v.extra_price) }}</span>
              <span class="opt-sold" v-if="v.stock === 0">售完</span>
              <span class="opt-stock-low" v-else-if="v.stock <= 5">僅剩{{ v.stock }}</span>
            </button>
          </div>
        </div>

        <!-- 數量選擇 -->
        <div class="option-group">
          <div class="option-label">購買數量</div>
          <div class="qty-row">
            <button class="qty-btn" @click="quantity > 1 && quantity--">−</button>
            <span class="qty-val">{{ quantity }}</span>
            <button class="qty-btn" @click="quantity < maxStock && quantity++">＋</button>
            <span class="qty-hint">（庫存 {{ maxStock }} 件）</span>
          </div>
        </div>

        <!-- 成團進度框 -->
        <div v-if="activeGroupBuy" class="group-box">
          <div class="group-box-header">
            <span class="group-fire">🔥 拼團進行中</span>
            <span class="group-countdown">⏱ {{ timeLeft }}</span>
          </div>
          <div class="group-numbers">
            <span class="group-current">{{ activeGroupBuy.current_count }}</span>
            <span class="group-sep">/</span>
            <span class="group-target">{{ activeGroupBuy.target_count }} 件</span>
            <span class="group-pct-badge" :class="{ full: groupPct >= 100 }">{{ groupPct }}%</span>
          </div>
          <div class="group-bar-wrap">
            <div class="group-bar-fill" :style="{ width: groupPct + '%' }"></div>
          </div>
          <div class="group-hint" v-if="groupPct < 100">
            還差 <b>{{ activeGroupBuy.target_count - activeGroupBuy.current_count }}</b> 件即可成團，快揪人！
          </div>
          <div class="group-hint success" v-else>🎉 已達成團門檻，出貨準備中！</div>
        </div>

        <!-- 操作按鈕 -->
        <div class="action-row">
          <button class="btn-cart" @click="addToCart">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
            </svg>
            加入購物車
          </button>
          <button class="btn-buy" @click="joinGroupBuy" v-if="activeGroupBuy">
            立即參團
          </button>
        </div>

        <!-- 提示文字 -->
        <p class="login-hint" v-if="!authStore.token">
          <router-link to="/login">登入</router-link> 後才能加入購物車
        </p>
      </div>
    </div>

    <!-- ── 商品詳情 Tabs ── -->
    <div class="detail-tabs">
      <div class="tabs-nav">
        <button
          v-for="tab in tabs" :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</button>
      </div>

      <div class="tab-content">
        <!-- 商品介紹 -->
        <div v-if="activeTab === 'desc'">
          <div v-if="product.description" class="desc-text" v-html="formattedDesc"></div>
          <div v-else class="desc-empty">商家尚未填寫商品介紹</div>
        </div>

        <!-- 商品規格 -->
        <div v-if="activeTab === 'spec'" class="spec-table">
          <div class="spec-row">
            <div class="spec-key">商品名稱</div>
            <div class="spec-val">{{ product.name }}</div>
          </div>
          <div class="spec-row">
            <div class="spec-key">分類</div>
            <div class="spec-val">{{ categoryLabel }}</div>
          </div>
          <div class="spec-row">
            <div class="spec-key">最低成團數</div>
            <div class="spec-val">{{ product.min_group_size }} 件</div>
          </div>
          <div class="spec-row">
            <div class="spec-key">現有庫存</div>
            <div class="spec-val">{{ product.stock }} 件</div>
          </div>
          <div class="spec-row" v-if="product.merchant_name">
            <div class="spec-key">供應商家</div>
            <div class="spec-val">{{ product.merchant_name }}</div>
          </div>
          <div class="spec-row" v-if="variants.length">
            <div class="spec-key">可選規格</div>
            <div class="spec-val">{{ variants.map(v=>v.name).join('、') }}</div>
          </div>
        </div>

        <!-- 活動說明 -->
        <div v-if="activeTab === 'group'" class="group-desc">
          <div class="group-desc-item">
            <span class="gd-icon">📋</span>
            <div>
              <div class="gd-title">成團條件</div>
              <div class="gd-body">本團需 <b>{{ product.min_group_size }}</b> 件即可成團。達標後商家將進行備貨與出貨。</div>
            </div>
          </div>
          <div class="group-desc-item">
            <span class="gd-icon">💰</span>
            <div>
              <div class="gd-title">付款方式</div>
              <div class="gd-body">成團後才扣款；未成團全額退款，無任何手續費。</div>
            </div>
          </div>
          <div class="group-desc-item">
            <span class="gd-icon">📍</span>
            <div>
              <div class="gd-title">取貨方式</div>
              <div class="gd-body">新竹在地多點自取，下單時選擇取貨地點與時段。</div>
            </div>
          </div>
          <div class="group-desc-item" v-if="activeGroupBuy">
            <span class="gd-icon">⏰</span>
            <div>
              <div class="gd-title">截止時間</div>
              <div class="gd-body">{{ formatDeadline(activeGroupBuy.deadline) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading">
    <el-skeleton :rows="8" animated />
  </div>

  <div v-else class="not-found">
    <el-result icon="warning" title="找不到此商品">
      <template #extra>
        <el-button @click="$router.push('/products')">返回商品列表</el-button>
      </template>
    </el-result>
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
const displayImg = ref('')
const activeTab = ref('desc')
let timer = null

const tabs = [
  { key: 'desc',  label: '商品介紹' },
  { key: 'spec',  label: '商品規格' },
  { key: 'group', label: '活動說明' },
]

const allImages = computed(() => {
  const imgs = product.value?.images?.length ? [...product.value.images] : []
  if (product.value?.image_url && !imgs.includes(product.value.image_url))
    imgs.unshift(product.value.image_url)
  return imgs.length ? imgs : ['https://placehold.co/600x400/f0f4ff/409eff?text=商品圖']
})

const selectedVariantPrice = computed(() =>
  (product.value?.group_price || 0) + (selectedVariant.value?.extra_price || 0)
)
const maxStock = computed(() => selectedVariant.value?.stock ?? product.value?.stock ?? 99)
const discountPct = computed(() =>
  Math.round((selectedVariantPrice.value / (product.value?.original_price || 1)) * 10)
)
const savingAmt = computed(() =>
  Math.round((product.value?.original_price || 0) - selectedVariantPrice.value)
)
const groupPct = computed(() => {
  if (!activeGroupBuy.value) return 0
  return Math.min(100, Math.round(
    (activeGroupBuy.value.current_count / activeGroupBuy.value.target_count) * 100
  ))
})
const ratingCount = computed(() => Math.floor(Math.random() * 80) + 20)
const soldHint = computed(() => {
  const s = product.value?.stock
  if (!s) return ''
  return s > 100 ? '100+ 件' : `${s} 件`
})
const categoryLabel = computed(() => ({
  food: '🍱 熟食料理', drink: '🧋 飲品茶飲', dessert: '🍰 甜點烘焙',
  fresh: '🥩 生鮮蔬果', snack: '🍿 零食點心', frozen: '🧊 冷凍食品',
  health: '🥗 健康養生', brunch: '🍳 早午餐', international: '🌏 異國料理', gift: '🎁 伴手禮',
  daily: '🛒 生活日用', cleaning: '🧹 清潔衛生', beauty: '💄 美妝保養',
  baby: '👶 母嬰用品', pet: '🐾 寵物用品', electronics: '📱 3C家電',
  home: '🛋️ 居家用品', stationery: '✏️ 文具玩具', fashion: '👕 服飾配件', sports: '🏃 運動戶外',
})[product.value?.category] || product.value?.category)

const formattedDesc = computed(() =>
  (product.value?.description || '').replace(/\n/g, '<br>')
)

function updateCountdown() {
  if (!activeGroupBuy.value) return
  const diff = dayjs(activeGroupBuy.value.deadline).diff(dayjs())
  if (diff <= 0) { timeLeft.value = '已截止'; return }
  const d = dayjs.duration(diff)
  const days = Math.floor(d.asDays())
  if (days > 0) timeLeft.value = `${days}天 ${d.hours()}小時`
  else timeLeft.value = `${d.hours()}h ${d.minutes()}m ${d.seconds()}s`
}

function addToCart() {
  if (!authStore.token) return router.push('/login')
  cartStore.addItem(
    { ...product.value, group_price: selectedVariantPrice.value },
    quantity.value,
    selectedVariant.value?.id,
    selectedVariant.value?.name,
  )
  ElMessage.success(`已加入購物車（x${quantity.value}）`)
}

async function joinGroupBuy() {
  if (!authStore.token) return router.push('/login')
  try {
    await api.post(`/group-buys/${activeGroupBuy.value.id}/join`, {
      user_id: authStore.user?.id,
      quantity: quantity.value,
      pickup_location_id: '新竹火車站前廣場',
    })
    ElMessage.success('已成功參團！等待成團後通知取貨。')
    activeGroupBuy.value.current_count += quantity.value
  } catch {
    ElMessage.error('參團失敗，請稍後再試')
  }
}

function copyLink() {
  navigator.clipboard.writeText(window.location.href)
  ElMessage.success('連結已複製')
}

function formatDeadline(d) {
  return dayjs(d).format('YYYY年MM月DD日 HH:mm')
}

onMounted(async () => {
  const pid = route.params.id
  const [pRes, vRes, gbRes] = await Promise.all([
    api.get(`/products/${pid}`),
    api.get(`/products/${pid}/variants`),
    api.get('/group-buys/').catch(() => ({ data: [] })),
  ])
  product.value = pRes.data
  variants.value = vRes.data.filter(v => v.is_active !== false)
  if (variants.value.length) selectedVariant.value = variants.value[0]
  activeGroupBuy.value = gbRes.data.find(
    (gb) => gb.product_id === pid && gb.status === 'open'
  ) || null
  loading.value = false
  displayImg.value = allImages.value[0]
  if (activeGroupBuy.value) {
    updateCountdown()
    timer = setInterval(updateCountdown, 1000)
  }
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.detail-page { display: flex; flex-direction: column; gap: 28px; max-width: 1100px; margin: 0 auto; }

/* Breadcrumb */
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--text-3);
}
.breadcrumb a { color: var(--text-3); text-decoration: none; }
.breadcrumb a:hover { color: var(--brand); }
.breadcrumb .sep { color: var(--border); }
.breadcrumb .current { color: var(--text-1); font-weight: 500; }

/* Detail body layout */
.detail-body {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 36px; align-items: flex-start;
}

/* Image section */
.img-section { display: flex; flex-direction: column; gap: 12px; }
.main-img-wrap {
  position: relative; border-radius: var(--r-xl); overflow: hidden;
  background: #f0f4ff; border: 1px solid var(--border);
}
.main-img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.img-discount-badge {
  position: absolute; top: 14px; right: 14px;
  background: var(--danger); color: #fff;
  font-size: 13px; font-weight: 700;
  padding: 4px 10px; border-radius: 99px;
}
.img-save-badge {
  position: absolute; top: 48px; right: 14px;
  background: #ff6900; color: #fff;
  font-size: 11px; font-weight: 700;
  padding: 3px 9px; border-radius: 99px;
}
.img-tags {
  position: absolute; top: 14px; left: 14px;
  display: flex; flex-direction: column; gap: 5px;
}
.img-tag {
  background: rgba(15,23,42,.7); backdrop-filter: blur(4px);
  color: #fff; font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 99px;
}

.thumb-strip { display: flex; gap: 8px; flex-wrap: wrap; }
.thumb {
  width: 68px; height: 68px; border-radius: var(--r-md);
  border: 2px solid var(--border); overflow: hidden;
  cursor: pointer; transition: border-color .15s; flex-shrink: 0;
}
.thumb.active { border-color: var(--brand); }
.thumb img { width: 100%; height: 100%; object-fit: cover; }

.share-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-3); }
.share-btn {
  padding: 5px 12px; border-radius: var(--r-md);
  border: 1.5px solid var(--border);
  font-size: 12px; cursor: pointer; background: var(--card);
  color: var(--text-2); transition: all .15s;
}
.share-btn:hover { border-color: var(--brand); color: var(--brand); }

/* Buy section */
.buy-section { display: flex; flex-direction: column; gap: 18px; }
.merchant-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 99px;
  background: var(--brand-light); color: var(--brand);
  font-size: 12px; font-weight: 600; width: fit-content;
}
.product-name { font-size: 22px; font-weight: 700; color: var(--text-1); line-height: 1.4; }

.rating-row { display: flex; align-items: center; gap: 10px; }
.stars { color: #f5a623; font-size: 15px; letter-spacing: 1px; }
.rating-count { font-size: 13px; color: var(--text-3); }
.sold-count { font-size: 12px; color: var(--text-3); border-left: 1px solid var(--border); padding-left: 10px; }

/* Price box */
.price-box {
  background: #fff7f7; border-radius: var(--r-lg);
  padding: 16px 20px; border: 1px solid #ffe0e0;
  display: flex; flex-direction: column; gap: 8px;
}
.price-main-row { display: flex; align-items: baseline; gap: 10px; }
.price-label { font-size: 12px; color: #c0392b; font-weight: 600; }
.group-price { font-size: 18px; font-weight: 700; color: #c0392b; }
.group-price em { font-style: normal; font-size: 32px; }
.price-sub-row { display: flex; align-items: center; gap: 12px; }
.original-price { font-size: 14px; color: var(--text-3); text-decoration: line-through; }
.saving-tag {
  background: #fff3cd; color: #856404;
  font-size: 12px; font-weight: 700;
  padding: 2px 8px; border-radius: 4px;
}

/* Delivery row */
.delivery-row {
  display: flex; gap: 0;
  border: 1px solid var(--border); border-radius: var(--r-md);
  overflow: hidden;
}
.delivery-item {
  flex: 1; display: flex; align-items: center; gap: 8px;
  padding: 12px 14px;
  border-right: 1px solid var(--border);
}
.delivery-item:last-child { border-right: none; }
.d-icon { font-size: 20px; flex-shrink: 0; }
.d-title { font-size: 12px; font-weight: 700; color: var(--text-1); margin-bottom: 2px; }
.d-desc { font-size: 11px; color: var(--text-3); }

/* Option group */
.option-group { display: flex; flex-direction: column; gap: 10px; }
.option-label { font-size: 13px; font-weight: 700; color: var(--text-2); }

.option-btns { display: flex; flex-wrap: wrap; gap: 8px; }
.option-btn {
  position: relative; padding: 8px 16px;
  border-radius: var(--r-md); border: 2px solid var(--border);
  cursor: pointer; background: var(--card);
  font-size: 14px; color: var(--text-1);
  transition: all .18s; display: flex; align-items: center; gap: 5px;
}
.option-btn:hover:not(.sold-out) { border-color: var(--brand); }
.option-btn.selected { border-color: var(--brand); background: var(--brand-light); color: var(--brand); }
.option-btn.sold-out { opacity: .4; cursor: not-allowed; text-decoration: line-through; }
.opt-name { font-weight: 500; }
.opt-extra { font-size: 11px; color: var(--accent); }
.opt-extra.neg { color: #27ae60; }
.opt-sold { font-size: 10px; color: var(--text-3); }
.opt-stock-low { font-size: 10px; color: var(--danger); }

/* Qty row */
.qty-row { display: flex; align-items: center; gap: 10px; }
.qty-btn {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid var(--border);
  background: var(--card); cursor: pointer;
  font-size: 18px; font-weight: 300; color: var(--text-1);
  display: flex; align-items: center; justify-content: center;
  transition: all .15s; line-height: 1;
}
.qty-btn:hover { border-color: var(--brand); color: var(--brand); }
.qty-val { font-size: 18px; font-weight: 700; min-width: 32px; text-align: center; }
.qty-hint { font-size: 12px; color: var(--text-3); }

/* Group box */
.group-box {
  background: linear-gradient(135deg, #fff7e6 0%, #fff3d4 100%);
  border: 1px solid #f5c84c; border-radius: var(--r-lg);
  padding: 16px 18px; display: flex; flex-direction: column; gap: 10px;
}
.group-box-header { display: flex; justify-content: space-between; align-items: center; }
.group-fire { font-size: 14px; font-weight: 700; color: #d97706; }
.group-countdown { font-size: 13px; font-weight: 700; color: #b45309; }
.group-numbers { display: flex; align-items: baseline; gap: 4px; }
.group-current { font-size: 22px; font-weight: 700; color: var(--brand); }
.group-sep { font-size: 15px; color: var(--text-3); }
.group-target { font-size: 15px; color: var(--text-2); }
.group-pct-badge {
  margin-left: 8px; padding: 2px 8px; border-radius: 99px;
  background: var(--brand-light); color: var(--brand);
  font-size: 12px; font-weight: 700;
}
.group-pct-badge.full { background: #d1fae5; color: #059669; }
.group-bar-wrap {
  height: 8px; border-radius: 99px; background: #fde68a; overflow: hidden;
}
.group-bar-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  transition: width .5s ease;
}
.group-hint { font-size: 13px; color: #92400e; }
.group-hint.success { color: #059669; font-weight: 600; }

/* Action row */
.action-row { display: flex; gap: 12px; }
.btn-cart {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px; border-radius: var(--r-md);
  background: var(--card); border: 2px solid var(--brand);
  color: var(--brand); font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all .18s;
}
.btn-cart:hover { background: var(--brand-light); }
.btn-buy {
  flex: 1; padding: 14px; border-radius: var(--r-md);
  background: var(--brand); border: 2px solid var(--brand);
  color: #fff; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all .18s;
}
.btn-buy:hover { background: var(--brand-hover); border-color: var(--brand-hover); }

.login-hint { font-size: 13px; color: var(--text-3); text-align: center; }
.login-hint a { color: var(--brand); font-weight: 600; }

/* Detail tabs */
.detail-tabs {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-xl); overflow: hidden;
}
.tabs-nav {
  display: flex; border-bottom: 1px solid var(--border);
  background: var(--bg);
}
.tab-btn {
  padding: 14px 28px; font-size: 14px; font-weight: 600; cursor: pointer;
  border: none; background: transparent; color: var(--text-3);
  border-bottom: 3px solid transparent;
  transition: all .15s; margin-bottom: -1px;
}
.tab-btn:hover { color: var(--brand); }
.tab-btn.active { color: var(--brand); border-bottom-color: var(--brand); background: var(--card); }

.tab-content { padding: 28px; }

.desc-text { font-size: 15px; color: var(--text-1); line-height: 2; }
.desc-empty { font-size: 14px; color: var(--text-3); text-align: center; padding: 24px; }

.spec-table { display: flex; flex-direction: column; }
.spec-row {
  display: flex; padding: 14px 0; border-bottom: 1px solid var(--border);
}
.spec-row:last-child { border-bottom: none; }
.spec-key { width: 140px; font-size: 14px; font-weight: 600; color: var(--text-3); flex-shrink: 0; }
.spec-val { flex: 1; font-size: 14px; color: var(--text-1); }

.group-desc { display: flex; flex-direction: column; gap: 20px; }
.group-desc-item { display: flex; gap: 14px; align-items: flex-start; }
.gd-icon { font-size: 24px; flex-shrink: 0; margin-top: 2px; }
.gd-title { font-size: 15px; font-weight: 700; color: var(--text-1); margin-bottom: 4px; }
.gd-body { font-size: 14px; color: var(--text-2); line-height: 1.7; }

.loading, .not-found { padding: 60px 40px; }

/* ── Mobile ─────────────────────────────────── */
@media (max-width: 900px) {
  .detail-body { grid-template-columns: 1fr; gap: 24px; }
  .detail-page { gap: 20px; }
}
@media (max-width: 600px) {
  .delivery-row { flex-direction: column; }
  .delivery-item { border-right: none; border-bottom: 1px solid var(--border); }
  .delivery-item:last-child { border-bottom: none; }
  .product-name { font-size: 18px; }
  .group-price em { font-size: 26px; }
  .tab-btn { padding: 12px 16px; font-size: 13px; }
  .tab-content { padding: 20px; }
}
</style>
