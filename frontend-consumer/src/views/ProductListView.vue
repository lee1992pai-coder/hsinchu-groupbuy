<template>
  <div class="list-page">

    <!-- 頂部搜尋列 -->
    <div class="search-header">
      <el-input
        v-model="searchQ"
        placeholder="搜尋商品名稱、關鍵字…"
        clearable
        @keyup.enter="doFetch"
        @clear="doFetch"
        class="search-input"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
        <template #append>
          <el-button type="primary" @click="doFetch">搜尋</el-button>
        </template>
      </el-input>
    </div>

    <!-- 熱門標籤橫排 -->
    <div class="tag-strip">
      <span class="tag-strip-label">熱門篩選：</span>
      <button
        v-for="t in hotTags" :key="t"
        class="tag-chip"
        :class="{ active: activeTag === t }"
        @click="toggleTag(t)"
      >{{ t }}</button>
    </div>

    <div class="layout">
      <!-- 左側篩選 -->
      <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
        <div class="sidebar-title">
          <span>篩選條件</span>
          <button class="sidebar-close" @click="sidebarOpen = false">✕</button>
        </div>

        <!-- 分類（分組） -->
        <div class="filter-group">
          <button
            class="filter-btn"
            :class="{ active: category === '' }"
            @click="category = ''; doFetch()"
          >🏪 全部商品</button>
        </div>
        <div class="filter-group" v-for="grp in categoryGroups" :key="grp.label">
          <div class="filter-label">{{ grp.label }}</div>
          <div class="filter-options">
            <button
              v-for="c in grp.items" :key="c.key"
              class="filter-btn"
              :class="{ active: category === c.key }"
              @click="category = c.key; doFetch()"
            >
              <span>{{ c.icon }}</span> {{ c.label }}
            </button>
          </div>
        </div>

        <!-- 價格區間 -->
        <div class="filter-group">
          <div class="filter-label">價格區間</div>
          <div class="price-range">
            <input v-model.number="priceMin" type="number" placeholder="最低" class="price-input" @change="doFetch" />
            <span class="price-sep">—</span>
            <input v-model.number="priceMax" type="number" placeholder="最高" class="price-input" @change="doFetch" />
          </div>
          <div class="price-presets">
            <button v-for="p in pricePresets" :key="p.label"
              class="preset-btn"
              @click="priceMin=p.min; priceMax=p.max; doFetch()">
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- 快速成團 -->
        <div class="filter-group">
          <div class="filter-label">成團門檻</div>
          <div class="filter-options">
            <button class="filter-btn" :class="{ active: minGroup==='small' }" @click="minGroup=minGroup==='small'?'':'small'; doFetch()">5 件以下</button>
            <button class="filter-btn" :class="{ active: minGroup==='mid' }" @click="minGroup=minGroup==='mid'?'':'mid'; doFetch()">6–15 件</button>
            <button class="filter-btn" :class="{ active: minGroup==='big' }" @click="minGroup=minGroup==='big'?'':'big'; doFetch()">15 件以上</button>
          </div>
        </div>

        <button class="reset-btn" @click="resetFilters">重設篩選</button>
      </aside>

      <!-- 右側主內容 -->
      <div class="main-content">

        <!-- 工具列 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="9" y2="18"/>
              </svg>
              篩選
            </button>
            <span class="result-count" v-if="!loading">共 <b>{{ products.length }}</b> 件商品</span>
          </div>
          <div class="toolbar-right">
            <select v-model="sortBy" class="sort-select" @change="doFetch">
              <option value="">預設排序</option>
              <option value="price_asc">價格低→高</option>
              <option value="price_desc">價格高→低</option>
              <option value="newest">最新上架</option>
            </select>
            <!-- 格式切換 -->
            <div class="view-toggle">
              <button :class="{ active: viewMode==='grid' }" @click="viewMode='grid'" title="格狀">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
                </svg>
              </button>
              <button :class="{ active: viewMode==='list' }" @click="viewMode='list'" title="列表">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                  <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 商品格狀 -->
        <div v-loading="loading">
          <div v-if="filteredProducts.length">
            <!-- 格狀模式 -->
            <div v-if="viewMode==='grid'" class="product-grid">
              <ProductCard
                v-for="p in filteredProducts" :key="p.id"
                :product="p"
                @click="$router.push(`/products/${p.id}`)"
                @add-to-cart="addToCart(p)"
              />
            </div>
            <!-- 列表模式 -->
            <div v-else class="product-list">
              <div
                v-for="p in filteredProducts" :key="p.id"
                class="list-item"
                @click="$router.push(`/products/${p.id}`)"
              >
                <img
                  :src="p.image_url || 'https://placehold.co/120x120/EFF6FF/2563EB?text=商品'"
                  :alt="p.name" class="list-img"
                />
                <div class="list-info">
                  <div class="list-merchant" v-if="p.merchant_name">🏪 {{ p.merchant_name }}</div>
                  <div class="list-name">{{ p.name }}</div>
                  <div class="list-tags">
                    <span v-for="tag in p.tags?.slice(0,3)" :key="tag" class="list-tag">{{ tag }}</span>
                  </div>
                  <div class="list-meta">最低 {{ p.min_group_size }} 件成團</div>
                </div>
                <div class="list-price-col">
                  <div class="list-price">NT${{ p.group_price }}</div>
                  <div class="list-original">NT${{ p.original_price }}</div>
                  <div class="list-save">省 NT${{ Math.round(p.original_price - p.group_price) }}</div>
                  <button class="list-cart-btn" @click.stop="addToCart(p)">加入購物車</button>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else-if="!loading" description="找不到符合條件的商品" :image-size="120" />
        </div>

        <!-- 載入更多 -->
        <div class="load-more" v-if="hasMore">
          <el-button @click="loadMore" :loading="loadingMore" round>載入更多商品</el-button>
        </div>
      </div>
    </div>

    <!-- 側欄遮罩 (mobile) -->
    <div class="sidebar-overlay" v-if="sidebarOpen" @click="sidebarOpen=false" />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const products = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const searchQ = ref('')
const category = ref('')
const activeTag = ref('')
const sortBy = ref('')
const viewMode = ref('grid')
const sidebarOpen = ref(false)
const priceMin = ref(null)
const priceMax = ref(null)
const minGroup = ref('')
const page = ref(0)
const PAGE_SIZE = 24
const hasMore = ref(false)

const categoryGroups = [
  {
    label: '食品飲料', items: [
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
    ],
  },
  {
    label: '生活百貨', items: [
      { key: 'daily',       label: '生活日用', icon: '🛒' },
      { key: 'cleaning',    label: '清潔衛生', icon: '🧹' },
      { key: 'beauty',      label: '美妝保養', icon: '💄' },
      { key: 'baby',        label: '母嬰用品', icon: '👶' },
      { key: 'pet',         label: '寵物用品', icon: '🐾' },
      { key: 'electronics', label: '3C家電',   icon: '📱' },
      { key: 'home',        label: '居家用品', icon: '🛋️' },
      { key: 'stationery',  label: '文具玩具', icon: '✏️' },
      { key: 'fashion',     label: '服飾配件', icon: '👕' },
      { key: 'sports',      label: '運動戶外', icon: '🏃' },
    ],
  },
]
const categories = [{ key: '', label: '全部', icon: '🏪' }, ...categoryGroups.flatMap(g => g.items)]

const hotTags = ['今日熱門', '園區下午茶', '限時特惠', '新品上架', '人氣必買']

const pricePresets = [
  { label: '100以下', min: 0, max: 100 },
  { label: '100–300', min: 100, max: 300 },
  { label: '300–500', min: 300, max: 500 },
  { label: '500以上', min: 500, max: null },
]

// client-side price + group filter after server fetch
const filteredProducts = computed(() => {
  let list = products.value
  if (priceMin.value != null) list = list.filter(p => p.group_price >= priceMin.value)
  if (priceMax.value != null) list = list.filter(p => p.group_price <= priceMax.value)
  if (minGroup.value === 'small') list = list.filter(p => p.min_group_size <= 5)
  if (minGroup.value === 'mid')   list = list.filter(p => p.min_group_size > 5 && p.min_group_size <= 15)
  if (minGroup.value === 'big')   list = list.filter(p => p.min_group_size > 15)
  return list
})

function toggleTag(t) {
  activeTag.value = activeTag.value === t ? '' : t
  doFetch()
}

function buildParams(skip) {
  const p = { skip, limit: PAGE_SIZE }
  if (category.value) p.category = category.value
  if (activeTag.value) p.tag = activeTag.value
  if (searchQ.value.trim()) p.q = searchQ.value.trim()
  if (sortBy.value) p.sort = sortBy.value
  return p
}

async function doFetch() {
  page.value = 0
  loading.value = true
  const { data } = await api.get('/products/', { params: buildParams(0) }).catch(() => ({ data: [] }))
  products.value = data
  hasMore.value = data.length === PAGE_SIZE
  loading.value = false
}

async function loadMore() {
  page.value++
  loadingMore.value = true
  const { data } = await api.get('/products/', { params: buildParams(page.value * PAGE_SIZE) })
  products.value.push(...data)
  hasMore.value = data.length === PAGE_SIZE
  loadingMore.value = false
}

function addToCart(product) {
  cartStore.addItem(product)
  ElMessage({ message: `「${product.name}」已加入購物車`, type: 'success', duration: 1500 })
}

function resetFilters() {
  category.value = ''
  activeTag.value = ''
  sortBy.value = ''
  searchQ.value = ''
  priceMin.value = null
  priceMax.value = null
  minGroup.value = ''
  doFetch()
}

onMounted(doFetch)
</script>

<style scoped>
.list-page { display: flex; flex-direction: column; gap: 16px; }

/* Search header */
.search-header { display: flex; justify-content: center; }
.search-input { max-width: 600px; width: 100%; }

/* Tag strip */
.tag-strip {
  display: flex; align-items: center; gap: 8px;
  flex-wrap: wrap; padding: 2px 0;
}
.tag-strip-label { font-size: 13px; color: var(--text-3); white-space: nowrap; }
.tag-chip {
  padding: 5px 14px; border-radius: 99px;
  border: 1.5px solid var(--border);
  font-size: 13px; font-weight: 500; color: var(--text-2);
  cursor: pointer; background: var(--card);
  transition: all .15s;
}
.tag-chip:hover { border-color: var(--brand); color: var(--brand); }
.tag-chip.active { border-color: var(--brand); color: var(--brand); background: var(--brand-light); font-weight: 600; }

/* Layout */
.layout { display: flex; gap: 24px; align-items: flex-start; }

/* Sidebar */
.sidebar {
  width: 220px; flex-shrink: 0;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 20px;
  display: flex; flex-direction: column; gap: 20px;
  position: sticky; top: 80px;
}
.sidebar-title {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 15px; font-weight: 700; color: var(--text-1);
}
.sidebar-close { display: none; background: none; border: none; cursor: pointer; font-size: 16px; color: var(--text-3); }

.filter-group { display: flex; flex-direction: column; gap: 10px; }
.filter-label { font-size: 12px; font-weight: 700; color: var(--text-3); text-transform: uppercase; letter-spacing: .5px; }
.filter-options { display: flex; flex-direction: column; gap: 6px; }
.filter-btn {
  text-align: left; padding: 7px 12px; border-radius: var(--r-md);
  border: 1.5px solid transparent;
  font-size: 13px; color: var(--text-2); cursor: pointer;
  background: transparent; transition: all .15s;
}
.filter-btn:hover { background: var(--brand-light); color: var(--brand); }
.filter-btn.active { background: var(--brand-light); color: var(--brand); border-color: var(--brand); font-weight: 600; }

.price-range { display: flex; align-items: center; gap: 6px; }
.price-input {
  flex: 1; min-width: 0; padding: 6px 8px; border-radius: var(--r-md);
  border: 1.5px solid var(--border); font-size: 13px; color: var(--text-1);
  background: var(--bg); outline: none;
}
.price-input:focus { border-color: var(--brand); }
.price-sep { font-size: 12px; color: var(--text-3); flex-shrink: 0; }

.price-presets { display: flex; flex-wrap: wrap; gap: 5px; }
.preset-btn {
  padding: 4px 8px; border-radius: 99px;
  border: 1px solid var(--border);
  font-size: 11px; color: var(--text-3); cursor: pointer;
  background: transparent; transition: all .15s;
}
.preset-btn:hover { border-color: var(--brand); color: var(--brand); }

.reset-btn {
  padding: 8px; border-radius: var(--r-md);
  border: 1.5px solid var(--border);
  font-size: 13px; color: var(--text-3); cursor: pointer;
  background: transparent; transition: all .15s;
  margin-top: 4px;
}
.reset-btn:hover { border-color: var(--danger); color: var(--danger); }

/* Main content */
.main-content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 16px; }

/* Toolbar */
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 10px 16px;
}
.toolbar-left { display: flex; align-items: center; gap: 12px; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }
.sidebar-toggle {
  display: none;
  align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: var(--r-md);
  border: 1.5px solid var(--border);
  font-size: 13px; color: var(--text-2); cursor: pointer;
  background: transparent;
}

.result-count { font-size: 13px; color: var(--text-3); }
.result-count b { color: var(--text-1); }

.sort-select {
  padding: 6px 10px; border-radius: var(--r-md);
  border: 1.5px solid var(--border);
  font-size: 13px; color: var(--text-2);
  background: var(--card); cursor: pointer; outline: none;
}
.sort-select:focus { border-color: var(--brand); }

.view-toggle { display: flex; border: 1.5px solid var(--border); border-radius: var(--r-md); overflow: hidden; }
.view-toggle button {
  padding: 6px 10px; background: transparent; border: none;
  cursor: pointer; color: var(--text-3); display: flex; align-items: center;
  transition: all .15s;
}
.view-toggle button.active { background: var(--brand-light); color: var(--brand); }
.view-toggle button:first-child { border-right: 1.5px solid var(--border); }

/* Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 16px;
}

/* List mode */
.product-list { display: flex; flex-direction: column; gap: 12px; }
.list-item {
  display: flex; gap: 16px; align-items: center;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 14px;
  cursor: pointer; transition: box-shadow .18s;
}
.list-item:hover { box-shadow: var(--shadow-sm); }
.list-img { width: 100px; height: 100px; object-fit: cover; border-radius: var(--r-md); flex-shrink: 0; }
.list-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 5px; }
.list-merchant { font-size: 11px; color: var(--text-3); }
.list-name { font-size: 15px; font-weight: 600; color: var(--text-1); }
.list-tags { display: flex; gap: 5px; flex-wrap: wrap; }
.list-tag {
  padding: 2px 8px; border-radius: 99px;
  background: var(--brand-light); color: var(--brand);
  font-size: 11px; font-weight: 500;
}
.list-meta { font-size: 12px; color: var(--text-3); }
.list-price-col {
  display: flex; flex-direction: column; align-items: flex-end; gap: 4px;
  flex-shrink: 0; min-width: 120px;
}
.list-price { font-size: 20px; font-weight: 700; color: var(--brand); }
.list-original { font-size: 13px; color: var(--text-3); text-decoration: line-through; }
.list-save { font-size: 12px; color: #ff6900; font-weight: 600; }
.list-cart-btn {
  margin-top: 4px; padding: 6px 14px;
  background: var(--brand); color: #fff;
  border: none; border-radius: var(--r-md);
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background .15s;
}
.list-cart-btn:hover { background: var(--brand-hover); }

.load-more { text-align: center; padding: 20px 0; }

/* Sidebar overlay for mobile */
.sidebar-overlay {
  display: none;
  position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 99;
}

/* ── Mobile ─────────────────────────────────── */
@media (max-width: 900px) {
  .sidebar {
    display: none;
    position: fixed; top: 0; left: 0; bottom: 0;
    width: 280px; z-index: 100;
    border-radius: 0; overflow-y: auto;
    transform: translateX(-100%); transition: transform .25s ease;
  }
  .sidebar.sidebar-open {
    display: flex; transform: translateX(0);
  }
  .sidebar-close { display: block; }
  .sidebar-toggle { display: flex; }
  .sidebar-overlay { display: block; }
  .product-grid { grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); }
}

@media (max-width: 480px) {
  .product-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .list-img { width: 80px; height: 80px; }
  .list-price { font-size: 17px; }
  .list-cart-btn { display: none; }
}
</style>
