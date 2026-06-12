<template>
  <article class="gb-card" @click="$emit('click')" :class="{ urgent: isUrgent }">
    <!-- 商品圖 -->
    <div class="gb-img-wrap" v-if="groupBuy.product?.image_url">
      <img :src="groupBuy.product.image_url" :alt="groupBuy.product?.name" class="gb-img" loading="lazy" />
    </div>

    <div class="gb-body">
      <!-- 狀態 + 倒計時 -->
      <div class="gb-top">
        <span class="gb-status-badge" :class="statusClass">{{ statusLabel }}</span>
        <span class="gb-countdown" v-if="timeLeft">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          {{ timeLeft }}
        </span>
      </div>

      <!-- 商品名稱 -->
      <p class="gb-name" v-if="groupBuy.product?.name">{{ groupBuy.product.name }}</p>

      <!-- 進度 -->
      <div class="progress-section">
        <div class="progress-meta">
          <span class="progress-count">
            <strong>{{ groupBuy.current_count }}</strong> / {{ groupBuy.target_count }} 人
          </span>
          <span class="progress-pct" :class="{ full: progressPct >= 100 }">{{ progressPct }}%</span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :style="{ width: progressPct + '%' }"
            :class="{ full: progressPct >= 100 }"
          />
        </div>
        <p class="progress-hint" v-if="progressPct < 100">
          還差 <strong>{{ groupBuy.target_count - groupBuy.current_count }}</strong> 件即成團
        </p>
        <p class="progress-hint success" v-else>🎉 已成團！出貨準備中</p>
      </div>

      <!-- 價格（若有） -->
      <div class="gb-price" v-if="groupBuy.product?.group_price">
        NT$ <strong>{{ groupBuy.product.group_price }}</strong>
        <span class="gb-orig" v-if="groupBuy.product.original_price">
          NT$ {{ groupBuy.product.original_price }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

const props = defineProps({ groupBuy: Object })
defineEmits(['click'])

const timeLeft = ref('')
let timer = null

function updateCountdown() {
  const diff = dayjs(props.groupBuy.deadline).diff(dayjs())
  if (diff <= 0) { timeLeft.value = '已截止'; clearInterval(timer); return }
  const d = dayjs.duration(diff)
  if (d.days() > 0) {
    timeLeft.value = `${d.days()}天 ${String(d.hours()).padStart(2,'0')}:${String(d.minutes()).padStart(2,'0')}`
  } else {
    timeLeft.value = `${String(d.hours()).padStart(2,'0')}:${String(d.minutes()).padStart(2,'0')}:${String(d.seconds()).padStart(2,'0')}`
  }
}

onMounted(() => { updateCountdown(); timer = setInterval(updateCountdown, 1000) })
onUnmounted(() => clearInterval(timer))

const progressPct = computed(() =>
  Math.min(100, Math.round((props.groupBuy.current_count / props.groupBuy.target_count) * 100))
)
const isUrgent = computed(() => {
  const diff = dayjs(props.groupBuy.deadline).diff(dayjs(), 'hour')
  return diff <= 6 && diff > 0
})
const statusClass = computed(() => ({
  open: 'status-open',
  success: 'status-success',
  failed: 'status-failed',
  done: 'status-done',
}[props.groupBuy.status] || 'status-open'))
const statusLabel = computed(() => ({
  open: '拼團中', success: '已成團', failed: '未成團', done: '已完成', shipping: '出貨中',
}[props.groupBuy.status] || props.groupBuy.status))
</script>

<style scoped>
.gb-card {
  background: var(--card);
  border-radius: var(--r-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  overflow: hidden;
  display: flex; flex-direction: column;
  transition: transform .22s cubic-bezier(.34,1.56,.64,1), box-shadow .22s;
}
.gb-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.gb-card.urgent { border-color: #FCA5A5; box-shadow: 0 0 0 2px rgba(220,38,38,.12), var(--shadow-sm); }

.gb-img-wrap { overflow: hidden; background: #F1F5F9; }
.gb-img { width: 100%; height: 160px; object-fit: cover; display: block; transition: transform .4s; }
.gb-card:hover .gb-img { transform: scale(1.04); }

.gb-body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 10px; }

.gb-top { display: flex; justify-content: space-between; align-items: center; }

.gb-status-badge {
  font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 20px; letter-spacing: .3px;
}
.status-open    { background: #DBEAFE; color: #1D4ED8; }
.status-success { background: #D1FAE5; color: #065F46; }
.status-failed  { background: #FEE2E2; color: #991B1B; }
.status-done    { background: #F1F5F9; color: #475569; }

.gb-countdown {
  display: flex; align-items: center; gap: 4px;
  font-size: 12px; font-weight: 600;
  color: var(--danger);
}
.gb-card.urgent .gb-countdown { animation: pulse 1s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.5 } }

.gb-name {
  font-size: 14px; font-weight: 600; color: var(--text-1); line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

.progress-section { display: flex; flex-direction: column; gap: 6px; }
.progress-meta { display: flex; justify-content: space-between; align-items: center; }
.progress-count { font-size: 13px; color: var(--text-2); }
.progress-count strong { color: var(--text-1); }
.progress-pct { font-size: 13px; font-weight: 700; color: var(--accent); }
.progress-pct.full { color: var(--success); }

.progress-track {
  height: 8px; background: #E2E8F0; border-radius: 99px; overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--brand), #60A5FA);
  transition: width .4s ease;
}
.progress-fill.full { background: linear-gradient(90deg, var(--success), #34D399); }

.progress-hint { font-size: 12px; color: var(--text-3); }
.progress-hint strong { color: var(--text-2); }
.progress-hint.success { color: var(--success); font-weight: 600; }

.gb-price {
  font-size: 16px; color: var(--brand); margin-top: 2px;
}
.gb-price strong { font-size: 20px; font-weight: 700; }
.gb-orig { font-size: 12px; color: var(--text-3); text-decoration: line-through; margin-left: 6px; }
</style>
