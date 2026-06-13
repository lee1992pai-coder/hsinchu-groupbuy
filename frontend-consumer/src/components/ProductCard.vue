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
      <!-- 省 X 元 badge -->
      <div class="save-badge" v-if="savingAmt > 0">省 NT${{ savingAmt }}</div>
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
      <div class="merchant-row" v-if="product.merchant_name">
        <span class="merchant-icon">🏪</span>
        <span class="merchant-name">{{ product.merchant_name }}</span>
      </div>
      <p class="card-name">{{ product.name }}</p>

      <!-- 團購門檻 + 庫存 -->
      <div class="card-meta">
        <span class="card-min">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:-1px">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          {{ product.min_group_size }} 件成團
        </span>
        <span class="card-stock urgent" v-if="product.stock <= 10 && product.stock > 0">
          僅剩 {{ product.stock }} 件！
        </span>
        <span class="card-stock" v-else-if="product.stock <= 30 && product.stock > 0">
          剩 {{ product.stock }} 件
        </span>
      </div>

      <div class="price-row">
        <div class="price-main">
          <span class="price-label">團購價</span>
          <span class="price-value">NT$<em>{{ product.group_price }}</em></span>
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
const savingAmt = computed(() =>
  Math.round(props.product.original_price - props.product.group_price)
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
.card-img-wrap { position: relative; overflow: hidden; background: #F1F5F9; }
.card-img {
  width: 100%; height: 200px; object-fit: cover;
  display: block; transition: transform .4s ease;
}
.product-card:hover .card-img { transform: scale(1.04); }

.discount-badge {
  position: absolute; top: 10px; right: 10px;
  background: var(--danger); color: #fff;
  font-size: 11px; font-weight: 700;
  padding: 3px 8px; border-radius: 20px;
}
.save-badge {
  position: absolute; top: 36px; right: 10px;
  background: #ff6900; color: #fff;
  font-size: 10px; font-weight: 700;
  padding: 2px 7px; border-radius: 20px;
}

.tag-list {
  position: absolute; top: 10px; left: 10px;
  display: flex; flex-direction: column; gap: 4px;
}
.tag {
  display: inline-block;
  background: rgba(15,23,42,.65); backdrop-filter: blur(4px);
  color: #fff; font-size: 10px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
}

.add-btn {
  position: absolute; bottom: 0; left: 0; right: 0;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  background: var(--brand); color: #fff;
  font-size: 13px; font-weight: 600; border: none; cursor: pointer;
  padding: 11px;
  opacity: 0; transform: translateY(6px);
  transition: opacity .2s, transform .2s;
}
.add-btn:hover { background: var(--brand-hover); }

/* Body */
.card-body { padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 6px; flex: 1; }

.merchant-row { display: flex; align-items: center; gap: 4px; }
.merchant-icon { font-size: 11px; }
.merchant-name { font-size: 11px; color: var(--text-3); }

.card-name {
  font-size: 14px; font-weight: 600; color: var(--text-1);
  line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta { display: flex; justify-content: space-between; align-items: center; }
.card-min {
  font-size: 11px; color: var(--text-3);
  display: flex; align-items: center; gap: 3px;
}
.card-stock { font-size: 11px; color: var(--accent); font-weight: 500; }
.card-stock.urgent { color: #f56c6c; font-weight: 700; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }

.price-row {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-top: auto;
}
.price-main { display: flex; flex-direction: column; gap: 1px; }
.price-label { font-size: 10px; color: var(--text-3); font-weight: 500; letter-spacing: .4px; }
.price-value { font-size: 15px; font-weight: 700; color: var(--brand); line-height: 1; }
.price-value em { font-style: normal; font-size: 20px; }
.price-original { font-size: 12px; color: var(--text-3); text-decoration: line-through; align-self: flex-end; }

@media (max-width: 480px) {
  .card-img { height: 140px; }
  .add-btn { opacity: 1; transform: translateY(0); }
  .card-body { padding: 10px 12px 12px; }
  .price-value em { font-size: 17px; }
}
</style>
