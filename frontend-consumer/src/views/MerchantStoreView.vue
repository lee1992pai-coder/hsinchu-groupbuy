<template>
  <div v-if="merchant" class="store-page">

    <!-- 店頭橫幅 -->
    <div class="store-hero">
      <div class="store-hero-bg" :style="heroBg"></div>
      <div class="store-hero-content">
        <div class="store-logo-wrap">
          <img v-if="merchant.logo_url" :src="merchant.logo_url" :alt="merchant.name" class="store-logo" />
          <div v-else class="store-logo-placeholder">{{ merchant.name[0] }}</div>
        </div>
        <div class="store-info">
          <h1 class="store-name">{{ merchant.name }}</h1>
          <p class="store-desc">{{ merchant.description || '歡迎光臨！' }}</p>
          <div class="store-badges">
            <span class="store-badge">✅ 已認證商家</span>
            <span class="store-badge">📦 {{ products.length }} 件商品</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分類篩選 -->
    <div class="store-toolbar">
      <div class="store-cat-pills">
        <button
          class="cat-pill" :class="{ active: filterCat === '' }"
          @click="filterCat = ''; fetchProducts()"
        >全部商品</button>
        <button
          v-for="c in availableCats" :key="c.key"
          class="cat-pill" :class="{ active: filterCat === c.key }"
          @click="filterCat = c.key; fetchProducts()"
        >{{ c.icon }} {{ c.label }}</button>
      </div>
      <select class="sort-select" v-model="sortBy" @change="fetchProducts">
        <option value="">預設排序</option>
        <option value="price_asc">價格低→高</option>
        <option value="price_desc">價格高→低</option>
        <option value="newest">最新上架</option>
      </select>
    </div>

    <!-- 商品格 -->
    <div v-loading="loading">
      <div v-if="products.length" class="product-grid">
        <ProductCard
          v-for="p in products" :key="p.id"
          :product="p"
          @click="$router.push(`/products/${p.id}`)"
          @add-to-cart="addToCart(p)"
        />
      </div>
      <el-empty v-else-if="!loading" description="此商家目前尚無商品" :image-size="120" />
    </div>

    <div class="load-more" v-if="hasMore">
      <el-button @click="loadMore" :loading="loadingMore" round>載入更多</el-button>
    </div>
  </div>

  <div v-else-if="loading" class="page-loading">
    <el-skeleton :rows="6" animated />
  </div>

  <el-result v-else icon="warning" title="找不到此商家">
    <template #extra>
      <el-button @click="$router.push('/merchants')">返回商家列表</el-button>
    </template>
  </el-result>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const merchant = ref(null)
const products = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const filterCat = ref('')
const sortBy = ref('')
const hasMore = ref(false)
const PAGE = 20

const ALL_CATS = [
  { key: 'food', label: '熟食料理', icon: '🍱' }, { key: 'drink', label: '飲品茶飲', icon: '🧋' },
  { key: 'dessert', label: '甜點烘焙', icon: '🍰' }, { key: 'fresh', label: '生鮮蔬果', icon: '🥩' },
  { key: 'snack', label: '零食點心', icon: '🍿' }, { key: 'frozen', label: '冷凍食品', icon: '🧊' },
  { key: 'health', label: '健康養生', icon: '🥗' }, { key: 'brunch', label: '早午餐', icon: '🍳' },
  { key: 'international', label: '異國料理', icon: '🌏' }, { key: 'gift', label: '伴手禮', icon: '🎁' },
  { key: 'daily', label: '生活日用', icon: '🛒' }, { key: 'cleaning', label: '清潔衛生', icon: '🧹' },
  { key: 'beauty', label: '美妝保養', icon: '💄' }, { key: 'baby', label: '母嬰用品', icon: '👶' },
  { key: 'pet', label: '寵物用品', icon: '🐾' }, { key: 'electronics', label: '3C家電', icon: '📱' },
  { key: 'home', label: '居家用品', icon: '🛋️' }, { key: 'stationery', label: '文具玩具', icon: '✏️' },
  { key: 'fashion', label: '服飾配件', icon: '👕' }, { key: 'sports', label: '運動戶外', icon: '🏃' },
]

const availableCats = computed(() => {
  const keys = new Set(products.value.map(p => p.category))
  return ALL_CATS.filter(c => keys.has(c.key))
})

const heroBg = computed(() => {
  if (merchant.value?.logo_url) return { backgroundImage: `url(${merchant.value.logo_url})` }
  return {}
})

function buildParams(skip = 0) {
  const p = { merchant_id: route.params.id, skip, limit: PAGE }
  if (filterCat.value) p.category = filterCat.value
  if (sortBy.value) p.sort = sortBy.value
  return p
}

async function fetchProducts() {
  loading.value = true
  const { data } = await api.get('/products/', { params: buildParams(0) }).catch(() => ({ data: [] }))
  products.value = data
  hasMore.value = data.length === PAGE
  loading.value = false
}

async function loadMore() {
  loadingMore.value = true
  const { data } = await api.get('/products/', { params: buildParams(products.value.length) })
  products.value.push(...data)
  hasMore.value = data.length === PAGE
  loadingMore.value = false
}

function addToCart(product) {
  cartStore.addItem(product)
  ElMessage({ message: `「${product.name}」已加入購物車`, type: 'success', duration: 1500 })
}

onMounted(async () => {
  const mid = route.params.id
  const [mRes] = await Promise.all([
    api.get(`/public/merchants/${mid}`).catch(() => ({ data: null })),
  ])
  merchant.value = mRes.data
  if (merchant.value) await fetchProducts()
  else loading.value = false
})
</script>

<style scoped>
.store-page { display: flex; flex-direction: column; gap: 24px; }

/* Hero */
.store-hero {
  position: relative; border-radius: var(--r-xl); overflow: hidden;
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
  min-height: 180px;
}
.store-hero-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: blur(20px) brightness(.4); opacity: .6;
}
.store-hero-content {
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 24px;
  padding: 32px 36px;
}
.store-logo-wrap { flex-shrink: 0; }
.store-logo {
  width: 90px; height: 90px; border-radius: 50%;
  object-fit: cover; border: 3px solid rgba(255,255,255,.6);
}
.store-logo-placeholder {
  width: 90px; height: 90px; border-radius: 50%;
  background: rgba(255,255,255,.2); border: 3px solid rgba(255,255,255,.5);
  display: flex; align-items: center; justify-content: center;
  font-size: 36px; font-weight: 700; color: #fff;
}
.store-info { display: flex; flex-direction: column; gap: 8px; }
.store-name { font-size: 26px; font-weight: 800; color: #fff; margin: 0; }
.store-desc { font-size: 14px; color: rgba(255,255,255,.8); margin: 0; max-width: 500px; }
.store-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.store-badge {
  background: rgba(255,255,255,.18); backdrop-filter: blur(4px);
  color: #fff; font-size: 12px; font-weight: 600;
  padding: 4px 12px; border-radius: 99px; border: 1px solid rgba(255,255,255,.3);
}

/* Toolbar */
.store-toolbar {
  display: flex; justify-content: space-between; align-items: center; gap: 12px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 12px 16px; flex-wrap: wrap;
}
.store-cat-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.cat-pill {
  padding: 5px 14px; border-radius: 99px;
  border: 1.5px solid var(--border); background: transparent;
  font-size: 13px; font-weight: 500; color: var(--text-2); cursor: pointer;
  transition: all .15s;
}
.cat-pill:hover { border-color: var(--brand); color: var(--brand); }
.cat-pill.active { border-color: var(--brand); color: var(--brand); background: var(--brand-light); font-weight: 600; }
.sort-select {
  padding: 6px 10px; border-radius: var(--r-md); border: 1.5px solid var(--border);
  font-size: 13px; color: var(--text-2); background: var(--card); cursor: pointer; outline: none;
}

/* Grid */
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 16px; }
.load-more { text-align: center; padding: 20px 0; }
.page-loading { padding: 60px; }

@media (max-width: 768px) {
  .store-hero-content { flex-direction: column; align-items: flex-start; padding: 24px 20px; gap: 16px; }
  .store-name { font-size: 20px; }
  .product-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
}
</style>
