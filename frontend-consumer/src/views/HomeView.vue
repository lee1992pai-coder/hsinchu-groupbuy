<template>
  <div class="home">

    <!-- Hero Banner -->
    <section class="hero-banner" v-if="banners.length">
      <el-carousel height="340px" arrow="hover" :interval="5000">
        <el-carousel-item v-for="b in banners" :key="b.id">
          <div class="hero-slide" @click="b.link_url && $router.push(b.link_url)" :style="{ cursor: b.link_url ? 'pointer' : 'default' }">
            <img :src="b.image_url" :alt="b.title" class="hero-img" />
            <div class="hero-overlay">
              <h2 class="hero-title">{{ b.title }}</h2>
              <span class="hero-cta" v-if="b.link_url">立即搶購 →</span>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <!-- 分類快捷列 -->
    <div class="category-bar">
      <button
        v-for="c in categories" :key="c.key"
        class="cat-pill"
        :class="{ active: activeCategory === c.key }"
        @click="setCategory(c.key)"
      >
        <span class="cat-icon">{{ c.icon }}</span>
        {{ c.label }}
      </button>
    </div>

    <!-- ── 閃購區 ── -->
    <section class="section flash-section" v-if="flashProducts.length">
      <div class="section-header">
        <div class="section-title">
          <span class="flash-badge">⚡ 限時特惠</span>
          <div class="flash-timer">
            <span class="timer-label">距離結束</span>
            <span class="timer-block">{{ flashTimer.h }}</span>
            <span class="timer-sep">:</span>
            <span class="timer-block">{{ flashTimer.m }}</span>
            <span class="timer-sep">:</span>
            <span class="timer-block">{{ flashTimer.s }}</span>
          </div>
        </div>
        <router-link to="/products?tag=限時特惠" class="see-all">查看全部 →</router-link>
      </div>
      <div class="h-scroll">
        <div
          v-for="p in flashProducts" :key="p.id"
          class="flash-card"
          @click="$router.push(`/products/${p.id}`)"
        >
          <div class="flash-img-wrap">
            <img :src="p.image_url || 'https://placehold.co/200x180/EFF6FF/2563EB?text=商品'" :alt="p.name" class="flash-img" />
            <div class="flash-discount">{{ Math.round((p.group_price/p.original_price)*10) }}折</div>
          </div>
          <div class="flash-body">
            <div class="flash-name">{{ p.name }}</div>
            <div class="flash-prices">
              <span class="flash-price">NT${{ p.group_price }}</span>
              <span class="flash-orig">NT${{ p.original_price }}</span>
            </div>
            <div class="flash-save">省 NT${{ Math.round(p.original_price - p.group_price) }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 限時拼團 ── -->
    <section class="section" v-if="groupBuys.length">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>限時拼團</h2>
          <span class="section-sub">{{ groupBuys.length }} 個活動進行中</span>
        </div>
        <router-link to="/group-buys" class="see-all">查看全部 →</router-link>
      </div>
      <div class="product-grid">
        <GroupBuyCard
          v-for="gb in groupBuys"
          :key="gb.id"
          :group-buy="gb"
          @click="$router.push(`/group-buys/${gb.id}`)"
        />
      </div>
    </section>

    <!-- ── 商品區 ── -->
    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>{{ categoryLabel }}商品</h2>
        </div>
        <div class="section-right">
          <select class="home-sort" v-model="sortBy" @change="filterProducts">
            <option value="">預設</option>
            <option value="price_asc">價格低→高</option>
            <option value="price_desc">價格高→低</option>
          </select>
          <router-link to="/products" class="see-all">更多商品 →</router-link>
        </div>
      </div>
      <div class="product-grid" v-loading="loading">
        <ProductCard
          v-for="p in products"
          :key="p.id"
          :product="p"
          @add-to-cart="addToCart(p)"
          @click="$router.push(`/products/${p.id}`)"
        />
        <div v-if="!products.length && !loading" class="empty-hint">此分類暫無商品</div>
      </div>
    </section>

    <!-- ── 熱門標籤快捷 ── -->
    <section class="section tag-section">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>熱門分類</h2>
        </div>
      </div>
      <div class="hot-tags">
        <button
          v-for="t in hotTags" :key="t"
          class="hot-tag-btn"
          @click="$router.push(`/products?tag=${t}`)"
        >
          <span class="hot-tag-icon">{{ t.icon }}</span>
          {{ t.label }}
        </button>
      </div>
    </section>

    <!-- ── 取貨地點 ── -->
    <section class="section pickup-section">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>新竹自取地點</h2>
          <span class="section-sub">共 {{ pickupLocations.length }} 處取貨點</span>
        </div>
      </div>
      <div class="pickup-grid">
        <div v-for="loc in pickupLocations" :key="loc.id" class="pickup-card">
          <div class="pickup-icon">📍</div>
          <div class="pickup-info">
            <div class="pickup-name">{{ loc.name }}</div>
            <div class="pickup-addr">{{ loc.address }}</div>
          </div>
          <div class="pickup-slots">
            <span v-for="slot in loc.time_slots" :key="slot" class="slot-pill">{{ slot }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 品牌特色條 -->
    <section class="features-bar">
      <div class="feature" v-for="f in features" :key="f.icon">
        <span class="feature-icon">{{ f.icon }}</span>
        <div>
          <div class="feature-title">{{ f.title }}</div>
          <div class="feature-desc">{{ f.desc }}</div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import GroupBuyCard from '../components/GroupBuyCard.vue'
import ProductCard from '../components/ProductCard.vue'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const banners = ref([])
const groupBuys = ref([])
const products = ref([])
const flashProducts = ref([])
const pickupLocations = ref([])
const loading = ref(false)
const activeCategory = ref('all')
const sortBy = ref('')
let flashTimerHandle = null

const flashTimer = ref({ h: '02', m: '00', s: '00' })
let flashEndTime = null

const categories = [
  { key: 'all',           label: '全部',     icon: '🏪' },
  { key: 'food',          label: '熟食料理', icon: '🍱' },
  { key: 'drink',         label: '飲品茶飲', icon: '🧋' },
  { key: 'dessert',       label: '甜點烘焙', icon: '🍰' },
  { key: 'fresh',         label: '生鮮蔬果', icon: '🥩' },
  { key: 'snack',         label: '零食點心', icon: '🍿' },
  { key: 'frozen',        label: '冷凍食品', icon: '🧊' },
  { key: 'health',        label: '健康養生', icon: '🥗' },
  { key: 'brunch',        label: '早午餐',   icon: '🍳' },
  { key: 'international', label: '異國料理', icon: '🌏' },
  { key: 'gift',          label: '伴手禮',   icon: '🎁' },
]

const hotTags = [
  { label: '今日熱門', icon: '🔥' },
  { label: '園區下午茶', icon: '☕' },
  { label: '限時特惠', icon: '⚡' },
  { label: '新品上架', icon: '✨' },
  { label: '人氣必買', icon: '⭐' },
]

const features = [
  { icon: '🔒', title: '安全購物', desc: '每筆交易受平台保障' },
  { icon: '🚚', title: '新竹在地配送', desc: '限定服務範圍，快速到貨' },
  { icon: '🤝', title: '拼團優惠', desc: '人越多，折扣越大' },
  { icon: '💵', title: '取貨付款', desc: '到場驗貨再付款' },
]

const categoryLabel = computed(() => {
  const c = categories.find((c) => c.key === activeCategory.value)
  return c?.key === 'all' ? '' : `${c?.label} `
})

function updateFlashTimer() {
  if (!flashEndTime) return
  const diff = flashEndTime - Date.now()
  if (diff <= 0) {
    flashTimer.value = { h: '00', m: '00', s: '00' }
    return
  }
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  const s = Math.floor((diff % 60000) / 1000)
  flashTimer.value = {
    h: String(h).padStart(2, '0'),
    m: String(m).padStart(2, '0'),
    s: String(s).padStart(2, '0'),
  }
}

function setCategory(key) {
  activeCategory.value = key
  filterProducts()
}

async function filterProducts() {
  loading.value = true
  try {
    const params = {}
    if (activeCategory.value !== 'all') params.category = activeCategory.value
    if (sortBy.value) params.sort = sortBy.value
    params.limit = 12
    const { data } = await api.get('/products/', { params })
    products.value = data
  } finally {
    loading.value = false
  }
}

function addToCart(product) {
  cartStore.addItem(product)
  ElMessage({ message: `「${product.name}」已加入購物車`, type: 'success', duration: 1800, grouping: true })
}

onMounted(async () => {
  loading.value = true
  const [bannersRes, gbRes, locRes, flashRes] = await Promise.all([
    api.get('/banners').catch(() => ({ data: [] })),
    api.get('/group-buys/').catch(() => ({ data: [] })),
    api.get('/pickup/locations').catch(() => ({ data: [] })),
    api.get('/products/', { params: { tag: '限時特惠', limit: 8 } }).catch(() => ({ data: [] })),
  ])
  banners.value = bannersRes.data
  groupBuys.value = gbRes.data.slice(0, 4)
  pickupLocations.value = locRes.data
  flashProducts.value = flashRes.data

  // flash timer: end at next midnight
  const now = new Date()
  flashEndTime = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0).getTime()
  updateFlashTimer()
  flashTimerHandle = setInterval(updateFlashTimer, 1000)

  await filterProducts()
})

onUnmounted(() => clearInterval(flashTimerHandle))
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 40px; }

/* Hero */
.hero-banner { border-radius: var(--r-xl); overflow: hidden; box-shadow: var(--shadow-md); }
.hero-slide { position: relative; height: 340px; }
.hero-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(15,23,42,.65) 0%, rgba(15,23,42,.1) 60%);
  display: flex; flex-direction: column; justify-content: flex-end;
  padding: 40px 48px; gap: 12px;
}
.hero-title { font-size: 28px; font-weight: 700; color: #fff; line-height: 1.3; max-width: 420px; }
.hero-cta {
  display: inline-block;
  background: var(--accent); color: #fff;
  font-size: 14px; font-weight: 700;
  padding: 8px 20px; border-radius: var(--r-md);
  width: fit-content;
}

/* Category bar */
.category-bar { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 2px; }
.category-bar::-webkit-scrollbar { display: none; }
.cat-pill {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 18px; border-radius: 99px;
  background: var(--card); border: 1.5px solid var(--border);
  font-size: 14px; font-weight: 500; color: var(--text-2);
  cursor: pointer; white-space: nowrap; transition: all .18s;
}
.cat-pill:hover, .cat-pill.active { border-color: var(--brand); color: var(--brand); background: var(--brand-light); font-weight: 600; }
.cat-icon { font-size: 18px; }

/* Sections */
.section { display: flex; flex-direction: column; gap: 20px; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-title { display: flex; align-items: center; gap: 12px; }
.section-accent { display: block; width: 4px; height: 24px; border-radius: 2px; background: var(--brand); }
.section-title h2 { font-size: 20px; font-weight: 700; color: var(--text-1); }
.section-sub { font-size: 13px; color: var(--text-3); }
.section-right { display: flex; align-items: center; gap: 12px; }
.see-all { font-size: 14px; font-weight: 500; color: var(--brand); text-decoration: none; }
.see-all:hover { opacity: .8; }

/* Home sort */
.home-sort {
  padding: 5px 10px; border-radius: var(--r-md);
  border: 1.5px solid var(--border);
  font-size: 13px; color: var(--text-2);
  background: var(--card); cursor: pointer; outline: none;
}

/* Flash section */
.flash-section { }
.flash-badge {
  display: inline-flex; align-items: center;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: #fff; font-size: 15px; font-weight: 800;
  padding: 6px 16px; border-radius: var(--r-md);
}
.flash-timer { display: flex; align-items: center; gap: 4px; margin-left: 12px; }
.timer-label { font-size: 12px; color: var(--text-3); margin-right: 4px; }
.timer-block {
  background: var(--text-1); color: var(--card);
  font-size: 16px; font-weight: 700; font-family: monospace;
  padding: 4px 8px; border-radius: 4px; min-width: 32px; text-align: center;
}
.timer-sep { font-size: 16px; font-weight: 700; color: var(--text-2); }

/* Horizontal scroll */
.h-scroll {
  display: flex; gap: 14px;
  overflow-x: auto; padding-bottom: 8px;
}
.h-scroll::-webkit-scrollbar { height: 4px; }
.h-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

.flash-card {
  min-width: 160px; max-width: 160px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); overflow: hidden;
  cursor: pointer; transition: transform .18s, box-shadow .18s; flex-shrink: 0;
}
.flash-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.flash-img-wrap { position: relative; }
.flash-img { width: 100%; height: 130px; object-fit: cover; display: block; }
.flash-discount {
  position: absolute; top: 8px; right: 8px;
  background: var(--danger); color: #fff;
  font-size: 11px; font-weight: 700;
  padding: 2px 7px; border-radius: 99px;
}
.flash-body { padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; }
.flash-name {
  font-size: 13px; font-weight: 600; color: var(--text-1);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.flash-prices { display: flex; align-items: baseline; gap: 6px; }
.flash-price { font-size: 16px; font-weight: 700; color: var(--brand); }
.flash-orig { font-size: 11px; color: var(--text-3); text-decoration: line-through; }
.flash-save { font-size: 11px; color: #ff6900; font-weight: 600; }

/* Product grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}
.empty-hint { grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-3); font-size: 14px; }

/* Hot tags */
.hot-tags { display: flex; gap: 12px; flex-wrap: wrap; }
.hot-tag-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 12px 20px; border-radius: var(--r-lg);
  background: var(--card); border: 1.5px solid var(--border);
  font-size: 14px; font-weight: 500; color: var(--text-1);
  cursor: pointer; transition: all .18s;
}
.hot-tag-btn:hover { border-color: var(--brand); color: var(--brand); background: var(--brand-light); }
.hot-tag-icon { font-size: 18px; }

/* Pickup */
.pickup-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.pickup-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 18px;
  display: flex; flex-direction: column; gap: 10px;
  box-shadow: var(--shadow-xs); transition: box-shadow .18s;
}
.pickup-card:hover { box-shadow: var(--shadow-sm); }
.pickup-icon { font-size: 24px; }
.pickup-name { font-size: 15px; font-weight: 600; color: var(--text-1); margin-bottom: 3px; }
.pickup-addr { font-size: 13px; color: var(--text-3); }
.pickup-slots { display: flex; flex-wrap: wrap; gap: 6px; }
.slot-pill {
  display: inline-block; background: var(--brand-light); color: var(--brand);
  font-size: 12px; font-weight: 500; padding: 3px 10px; border-radius: 99px;
}

/* Features */
.features-bar {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); overflow: hidden; box-shadow: var(--shadow-xs);
}
.feature {
  display: flex; align-items: center; gap: 14px;
  padding: 22px 24px; border-right: 1px solid var(--border);
}
.feature:last-child { border-right: none; }
.feature-icon { font-size: 28px; flex-shrink: 0; }
.feature-title { font-size: 14px; font-weight: 700; color: var(--text-1); margin-bottom: 3px; }
.feature-desc { font-size: 12px; color: var(--text-3); }

/* ── Mobile ─────────────────────────────────────────── */
@media (max-width: 768px) {
  .home { gap: 28px; }
  .hero-slide { height: 220px; }
  .hero-overlay { padding: 20px; gap: 8px; }
  .hero-title { font-size: 18px; }
  .product-grid { grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 12px; }
  .pickup-grid { grid-template-columns: 1fr; }
  .features-bar { grid-template-columns: 1fr 1fr; }
  .feature { padding: 16px; border-right: none; border-bottom: 1px solid var(--border); }
  .feature:nth-child(odd) { border-right: 1px solid var(--border); }
  .feature:nth-last-child(-n+2) { border-bottom: none; }
  .flash-timer { display: none; }
}
@media (max-width: 480px) {
  .product-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .features-bar { grid-template-columns: 1fr; }
  .feature { border-right: none !important; }
  .feature:not(:last-child) { border-bottom: 1px solid var(--border); }
}
</style>
