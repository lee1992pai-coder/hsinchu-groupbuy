<template>
  <div class="home">

    <!-- Hero Banner -->
    <section class="hero-banner" v-if="banners.length">
      <el-carousel height="320px" arrow="hover" :interval="5000">
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
        @click="activeCategory = c.key; filterProducts()"
      >
        <span class="cat-icon">{{ c.icon }}</span>
        {{ c.label }}
      </button>
    </div>

    <!-- 限時拼團 -->
    <section class="section" v-if="groupBuys.length || loading">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>限時拼團</h2>
          <span class="section-sub">{{ groupBuys.length }} 個活動進行中</span>
        </div>
        <router-link to="/group-buys" class="see-all">查看全部 <span>→</span></router-link>
      </div>
      <div class="product-grid">
        <GroupBuyCard
          v-for="gb in groupBuys"
          :key="gb.id"
          :group-buy="gb"
          @click="$router.push(`/group-buys/${gb.id}`)"
        />
      </div>
      <div v-if="!groupBuys.length && !loading" class="empty-hint">暫無進行中拼團</div>
    </section>

    <!-- 商品 -->
    <section class="section">
      <div class="section-header">
        <div class="section-title">
          <span class="section-accent" />
          <h2>{{ categoryLabel }}商品</h2>
        </div>
        <router-link to="/products" class="see-all">更多商品 <span>→</span></router-link>
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

    <!-- 取貨地點 -->
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
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import GroupBuyCard from '../components/GroupBuyCard.vue'
import ProductCard from '../components/ProductCard.vue'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const banners = ref([])
const groupBuys = ref([])
const products = ref([])
const pickupLocations = ref([])
const loading = ref(false)
const activeCategory = ref('all')

const categories = [
  { key: 'all',     label: '全部',   icon: '🏪' },
  { key: 'food',    label: '美食',   icon: '🍱' },
  { key: 'drink',   label: '飲品',   icon: '🧋' },
  { key: 'dessert', label: '甜點',   icon: '🍰' },
  { key: 'fresh',   label: '生鮮',   icon: '🥩' },
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

async function filterProducts() {
  loading.value = true
  try {
    const params = activeCategory.value !== 'all' ? { category: activeCategory.value } : {}
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
  const [bannersRes, gbRes, locRes] = await Promise.all([
    api.get('/banners').catch(() => ({ data: [] })),
    api.get('/group-buys/').catch(() => ({ data: [] })),
    api.get('/pickup/locations').catch(() => ({ data: [] })),
  ])
  banners.value = bannersRes.data
  groupBuys.value = gbRes.data.slice(0, 4)
  pickupLocations.value = locRes.data
  await filterProducts()
})
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 40px; }

/* Hero */
.hero-banner { border-radius: var(--r-xl); overflow: hidden; box-shadow: var(--shadow-md); }
.hero-slide { position: relative; height: 320px; }
.hero-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(15,23,42,.65) 0%, rgba(15,23,42,.1) 60%);
  display: flex; flex-direction: column; justify-content: flex-end;
  padding: 40px 48px;
  gap: 12px;
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
  cursor: pointer; white-space: nowrap;
  transition: all .18s;
}
.cat-pill:hover { border-color: var(--brand); color: var(--brand); background: var(--brand-light); }
.cat-pill.active { border-color: var(--brand); color: var(--brand); background: var(--brand-light); font-weight: 600; }
.cat-icon { font-size: 18px; }

/* Sections */
.section { display: flex; flex-direction: column; gap: 20px; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-title { display: flex; align-items: center; gap: 12px; }
.section-accent {
  display: block; width: 4px; height: 24px; border-radius: 2px;
  background: var(--brand);
}
.section-title h2 { font-size: 20px; font-weight: 700; color: var(--text-1); }
.section-sub { font-size: 13px; color: var(--text-3); }

.see-all {
  font-size: 14px; font-weight: 500; color: var(--brand);
  text-decoration: none; display: flex; align-items: center; gap: 4px;
}
.see-all span { transition: transform .15s; }
.see-all:hover span { transform: translateX(3px); }

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
}
.empty-hint {
  grid-column: 1/-1;
  text-align: center; padding: 40px; color: var(--text-3); font-size: 14px;
}

/* Pickup */
.pickup-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.pickup-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 18px;
  display: flex; flex-direction: column; gap: 10px;
  box-shadow: var(--shadow-xs);
  transition: box-shadow .18s;
}
.pickup-card:hover { box-shadow: var(--shadow-sm); }
.pickup-icon { font-size: 24px; }
.pickup-name { font-size: 15px; font-weight: 600; color: var(--text-1); margin-bottom: 3px; }
.pickup-addr { font-size: 13px; color: var(--text-3); }
.pickup-slots { display: flex; flex-wrap: wrap; gap: 6px; }
.slot-pill {
  display: inline-block;
  background: var(--brand-light); color: var(--brand);
  font-size: 12px; font-weight: 500;
  padding: 3px 10px; border-radius: 99px;
}

/* Features */
.features-bar {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}
.feature {
  display: flex; align-items: center; gap: 14px;
  padding: 22px 24px;
  border-right: 1px solid var(--border);
}
.feature:last-child { border-right: none; }
.feature-icon { font-size: 28px; flex-shrink: 0; }
.feature-title { font-size: 14px; font-weight: 700; color: var(--text-1); margin-bottom: 3px; }
.feature-desc { font-size: 12px; color: var(--text-3); }

/* ── Mobile ─────────────────────────────────────────────── */
@media (max-width: 768px) {
  .home { gap: 28px; }

  .hero-slide { height: 220px; }
  .hero-overlay { padding: 20px 20px; gap: 8px; }
  .hero-title { font-size: 18px; max-width: 100%; }
  .hero-cta { font-size: 13px; padding: 6px 14px; }

  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .pickup-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .features-bar {
    grid-template-columns: 1fr 1fr;
  }
  .feature {
    padding: 16px;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
  .feature:nth-child(odd) { border-right: 1px solid var(--border); }
  .feature:nth-last-child(-n+2) { border-bottom: none; }
}

@media (max-width: 480px) {
  .product-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .features-bar { grid-template-columns: 1fr; }
  .feature { border-right: none !important; }
  .feature:not(:last-child) { border-bottom: 1px solid var(--border); }
}
</style>
