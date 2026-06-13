<template>
  <div class="merchants-page">
    <div class="page-header">
      <div class="page-title">
        <span class="section-accent" />
        <h1>精選店家</h1>
        <span class="sub">共 {{ merchants.length }} 家認證商家</span>
      </div>
      <el-input
        v-model="searchQ" placeholder="搜尋店家名稱…" clearable
        class="search-input" @input="filtered"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div v-loading="loading">
      <div v-if="filteredMerchants.length" class="merchant-grid">
        <div
          v-for="m in filteredMerchants" :key="m.id"
          class="merchant-card"
          @click="$router.push(`/merchants/${m.id}`)"
        >
          <div class="mc-banner">
            <img v-if="m.logo_url" :src="m.logo_url" :alt="m.name" class="mc-logo" />
            <div v-else class="mc-logo-placeholder">{{ m.name[0] }}</div>
          </div>
          <div class="mc-body">
            <div class="mc-name">{{ m.name }}</div>
            <div class="mc-desc">{{ m.description || '點擊進入店家' }}</div>
            <div class="mc-footer">
              <span class="mc-count">📦 {{ m.product_count }} 件商品</span>
              <span class="mc-enter">進入店鋪 →</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else-if="!loading" description="找不到符合的店家" :image-size="120" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '../api'

const merchants = ref([])
const loading = ref(true)
const searchQ = ref('')

const filteredMerchants = computed(() => {
  if (!searchQ.value.trim()) return merchants.value
  const q = searchQ.value.toLowerCase()
  return merchants.value.filter(m => m.name.toLowerCase().includes(q) || (m.description || '').toLowerCase().includes(q))
})

onMounted(async () => {
  const { data } = await api.get('/public/merchants').catch(() => ({ data: [] }))
  merchants.value = data
  loading.value = false
})
</script>

<style scoped>
.merchants-page { display: flex; flex-direction: column; gap: 24px; }

.page-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.page-title { display: flex; align-items: center; gap: 12px; }
.section-accent { display: block; width: 4px; height: 24px; border-radius: 2px; background: var(--brand); }
.page-title h1 { font-size: 22px; font-weight: 700; color: var(--text-1); margin: 0; }
.sub { font-size: 13px; color: var(--text-3); }
.search-input { max-width: 280px; }

.merchant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.merchant-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-xl); overflow: hidden;
  cursor: pointer; transition: transform .2s, box-shadow .2s;
}
.merchant-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }

.mc-banner {
  height: 100px;
  background: linear-gradient(135deg, #1e3a5f, #2563eb);
  display: flex; align-items: center; justify-content: center;
}
.mc-logo { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 3px solid rgba(255,255,255,.5); }
.mc-logo-placeholder {
  width: 72px; height: 72px; border-radius: 50%;
  background: rgba(255,255,255,.2); border: 3px solid rgba(255,255,255,.4);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 800; color: #fff;
}

.mc-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 6px; }
.mc-name { font-size: 16px; font-weight: 700; color: var(--text-1); }
.mc-desc {
  font-size: 13px; color: var(--text-3); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.mc-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.mc-count { font-size: 12px; color: var(--text-3); }
.mc-enter { font-size: 13px; font-weight: 600; color: var(--brand); }

@media (max-width: 600px) {
  .merchant-grid { grid-template-columns: 1fr 1fr; gap: 12px; }
  .mc-banner { height: 80px; }
  .mc-logo, .mc-logo-placeholder { width: 56px; height: 56px; font-size: 22px; }
}
</style>
