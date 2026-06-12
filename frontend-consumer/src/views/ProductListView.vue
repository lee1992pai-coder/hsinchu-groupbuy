<template>
  <div>
    <!-- 搜尋列 -->
    <div class="search-bar">
      <el-input
        v-model="searchQ"
        placeholder="搜尋商品名稱…"
        clearable
        @keyup.enter="fetch"
        @clear="fetch"
        style="max-width:400px"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="category" placeholder="分類" clearable @change="fetch" style="width:130px">
        <el-option label="美食" value="food" />
        <el-option label="飲品" value="drink" />
        <el-option label="甜點" value="dessert" />
        <el-option label="生鮮" value="fresh" />
      </el-select>
    </div>

    <!-- 熱門標籤 -->
    <div class="tag-bar">
      <el-tag
        v-for="t in hotTags" :key="t"
        :type="activeTag === t ? 'primary' : 'info'"
        class="tag-chip"
        @click="toggleTag(t)"
      >{{ t }}</el-tag>
    </div>

    <div v-loading="loading">
      <div v-if="products.length" class="product-grid">
        <ProductCard
          v-for="p in products" :key="p.id"
          :product="p"
          @click="$router.push(`/products/${p.id}`)"
          @add-to-cart="addToCart(p)"
        />
      </div>
      <el-empty v-else-if="!loading" description="找不到符合條件的商品" />
    </div>

    <!-- 載入更多 -->
    <div class="load-more" v-if="hasMore">
      <el-button @click="loadMore" :loading="loadingMore">載入更多</el-button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
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
const page = ref(0)
const PAGE_SIZE = 20
const hasMore = ref(false)

const hotTags = ['今日熱門', '園區下午茶', '限時特惠', '新品上架', '人氣必買']

function toggleTag(t) {
  activeTag.value = activeTag.value === t ? '' : t
  fetch()
}

async function fetch() {
  page.value = 0
  loading.value = true
  const params = buildParams(0)
  const { data } = await api.get('/products/', { params }).catch(() => ({ data: [] }))
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

function buildParams(skip) {
  const p = { skip, limit: PAGE_SIZE }
  if (category.value) p.category = category.value
  if (activeTag.value) p.tag = activeTag.value
  if (searchQ.value) p.q = searchQ.value
  return p
}

function addToCart(product) {
  cartStore.addItem(product)
  ElMessage({ message: '已加入購物車', type: 'success', duration: 1200 })
}

onMounted(fetch)
</script>

<style scoped>
.search-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.tag-bar { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.tag-chip { cursor: pointer; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.load-more { text-align: center; margin-top: 28px; }
</style>
