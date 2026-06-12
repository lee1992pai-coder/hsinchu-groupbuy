<template>
  <div>
    <div class="page-header">
      <h2>🔥 限時拼團</h2>
      <el-radio-group v-model="statusFilter" @change="fetch">
        <el-radio-button value="open">拼團中</el-radio-button>
        <el-radio-button value="success">已成團</el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading">
      <div v-if="groupBuys.length" class="gb-grid">
        <div
          v-for="gb in groupBuys" :key="gb.id"
          class="gb-item"
          @click="$router.push(`/group-buys/${gb.id}`)"
        >
          <img
            :src="productMap[gb.product_id]?.image_url || 'https://placehold.co/400x200/f0f4ff/409eff?text=拼團'"
            class="gb-img"
          />
          <div class="gb-body">
            <div class="gb-name">{{ productMap[gb.product_id]?.name || '載入中…' }}</div>
            <div class="gb-price" v-if="productMap[gb.product_id]">
              <span class="group-price">NT$ {{ productMap[gb.product_id].group_price }}</span>
              <span class="original">NT$ {{ productMap[gb.product_id].original_price }}</span>
            </div>
            <GroupBuyCard :group-buy="gb" />
          </div>
        </div>
      </div>
      <el-empty v-else-if="!loading" description="目前沒有進行中的拼團" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'
import GroupBuyCard from '../components/GroupBuyCard.vue'

const groupBuys = ref([])
const productMap = ref({})
const loading = ref(false)
const statusFilter = ref('open')

async function fetch() {
  loading.value = true
  const { data } = await api.get('/group-buys/').catch(() => ({ data: [] }))
  groupBuys.value = data.filter((gb) => gb.status === statusFilter.value)

  // 批次載入商品資訊
  const ids = [...new Set(groupBuys.value.map((gb) => gb.product_id))]
  await Promise.all(
    ids.map(async (id) => {
      if (!productMap.value[id]) {
        const { data: p } = await api.get(`/products/${id}`).catch(() => ({ data: null }))
        if (p) productMap.value[id] = p
      }
    })
  )
  loading.value = false
}

onMounted(fetch)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h2 { font-size: 22px; }
.gb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.gb-item {
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.08); cursor: pointer; transition: transform .2s;
}
.gb-item:hover { transform: translateY(-3px); }
.gb-img { width: 100%; height: 160px; object-fit: cover; display: block; }
.gb-body { padding: 14px; }
.gb-name { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.gb-price { display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px; }
.group-price { font-size: 18px; font-weight: bold; color: #f56c6c; }
.original { font-size: 12px; color: #c0c4cc; text-decoration: line-through; }
</style>
