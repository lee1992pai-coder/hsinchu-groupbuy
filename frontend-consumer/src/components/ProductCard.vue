<template>
  <article class="product-card" @click="$emit('click')">
    <div class="card-img-wrap">
      <img
        :src="product.image_url || 'https://placehold.co/400x280/EFF6FF/2563EB?text=商品'"
        :alt="product.name"
        class="card-img"
        loading="lazy"
      />
      <!-- 折扣角標 -->
      <div class="discount-badge">{{ discountPct }}折</div>
      <!-- 標籤 -->
      <div v-if="product.tags?.length" class="tag-list">
        <span v-for="tag in product.tags.slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <!-- hover 加入按鈕 -->
      <button class="add-btn" @click.stop="$emit('add-to-cart')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        加入購物車
      </button>
    </div>

    <div class="card-body">
      <p class="card-name">{{ product.name }}</p>
      <div class="card-meta">
        <span class="card-min">最低 {{ product.min_group_size }} 件成團</span>
        <span class="card-stock" v-if="product.stock <= 20 && product.stock > 0">
          僅剩 {{ product.stock }} 件
        </span>
      </div>
      <div class="price-row">
        <div class="price-main">
          <span class="price-label">團購價</span>
          <span class="price-value">NT$ {{ product.group_price }}</span>
        </div>
        <span class="price-original">NT$ {{ product.original_price }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ product: Object })
defineEmits(['click', 'add-to-cart'])
const discountPct = computed(() =>
  Math.round((props.product.group_price / props.product.original_price) * 10)
)
</script>

<style scoped>
.product-card {
  background: var(--card);
  border-radius: var(--r-lg);
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: transform .22s cubic-bezier(.34,1.56,.64,1), box-shadow .22s;
  display: flex; flex-direction: column;
}
.product-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}
.product-card:hover .add-btn { opacity: 1; transform: translateY(0); }

/* Image area */
.card-img-wrap {
  position: relative; overflow: hidden;
  background: #F1F5F9;
}
.card-img {
  width: 100%; height: 200px; object-fit: cover;
  display: block;
  transition: transform .4s ease;
}
.product-card:hover .card-img { transform: scale(1.04); }

.discount-badge {
  position: absolute; top: 12px; right: 12px;
  background: var(--danger);
  color: #fff;
  font-size: 11px; font-weight: 700;
  padding: 3px 8px; border-radius: 20px;
  letter-spacing: .3px;
}

.tag-list {
  position: absolute; top: 12px; left: 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.tag {
  display: inline-block;
  background: rgba(15,23,42,.65);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 10px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
  letter-spacing: .3px;
}

.add-btn {
  position: absolute; bottom: 0; left: 0; right: 0;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  background: var(--brand);
  color: #fff; font-size: 13px; font-weight: 600;
  border: none; cursor: pointer;
  padding: 11px;
  opacity: 0; transform: translateY(6px);
  transition: opacity .2s, transform .2s;
}
.add-btn:hover { background: var(--brand-hover); }

/* Body */
.card-body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 8px; flex: 1; }

.card-name {
  font-size: 14px; font-weight: 600; color: var(--text-1);
  line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex; justify-content: space-between; align-items: center;
}
.card-min { font-size: 12px; color: var(--text-3); }
.card-stock { font-size: 12px; color: var(--accent); font-weight: 600; }

.price-row {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-top: auto;
}
.price-main { display: flex; flex-direction: column; gap: 1px; }
.price-label { font-size: 10px; color: var(--text-3); font-weight: 500; text-transform: uppercase; letter-spacing: .5px; }
.price-value { font-size: 20px; font-weight: 700; color: var(--brand); line-height: 1; }
.price-original { font-size: 12px; color: var(--text-3); text-decoration: line-through; align-self: flex-end; margin-bottom: 2px; }
</style>
