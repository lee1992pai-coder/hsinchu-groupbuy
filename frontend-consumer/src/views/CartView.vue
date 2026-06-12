<template>
  <div>
    <h2 class="page-title">🛒 購物車</h2>

    <el-empty v-if="!cartStore.items.length" description="購物車是空的">
      <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
    </el-empty>

    <template v-else>
      <el-row :gutter="24">
        <!-- 左：品項列表 -->
        <el-col :span="15">
          <el-card v-for="item in cartStore.items" :key="item.product.id" class="cart-item">
            <div class="item-row">
              <img :src="item.product.image_url || 'https://placehold.co/80x80/f0f4ff/409eff?text=商品'" class="item-img" />
              <div class="item-info">
                <div class="item-name">{{ item.product.name }}</div>
                <div v-if="item.variantName" class="item-variant">規格：{{ item.variantName }}</div>
                <div class="item-price">NT$ {{ item.product.group_price }}</div>
              </div>
              <el-input-number
                v-model="item.quantity" :min="1" size="small"
                @change="(v) => cartStore.updateQty(item.key, v)"
              />
              <el-button text type="danger" @click="cartStore.removeItem(item.key)">刪除</el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 右：結帳資訊 -->
        <el-col :span="9">
          <el-card class="checkout-card">
            <h3>物流選擇</h3>
            <el-radio-group v-model="deliveryType" class="delivery-group">
              <el-radio value="pickup">📍 指定據點自取</el-radio>
              <el-radio value="delivery">🚚 區域配送（限新竹/竹北）</el-radio>
            </el-radio-group>

            <!-- 自取 -->
            <template v-if="deliveryType === 'pickup'">
              <el-select v-model="pickupLocationId" placeholder="選擇取貨地點" style="width:100%;margin-top:10px">
                <el-option
                  v-for="loc in pickupLocations"
                  :key="loc.id"
                  :label="loc.name"
                  :value="loc.id"
                />
              </el-select>
              <el-select
                v-if="selectedLocation?.time_slots?.length"
                v-model="pickupTimeSlot"
                placeholder="選擇取貨時段"
                style="width:100%;margin-top:8px"
              >
                <el-option v-for="s in selectedLocation.time_slots" :key="s" :label="s" :value="s" />
              </el-select>
            </template>

            <!-- 配送 -->
            <template v-else>
              <el-input
                v-model="deliveryAddress"
                placeholder="新竹市東區○○路○○號"
                type="textarea" :rows="2"
                style="margin-top:10px"
                @blur="validateAddress"
              />
              <div v-if="addressError" class="addr-error">⚠️ {{ addressError }}</div>
              <div v-if="addressOk" class="addr-ok">✅ 地址在配送範圍內</div>
            </template>

            <el-divider />

            <div class="summary-row">
              <span>商品 {{ cartStore.count }} 件</span>
              <span class="total">NT$ {{ cartStore.total.toFixed(0) }}</span>
            </div>

            <el-alert type="warning" :closable="false" style="margin:12px 0 8px">
              💵 現場付款：請於取貨或收貨時付款
            </el-alert>

            <el-button
              type="primary" size="large" style="width:100%"
              :loading="submitting"
              :disabled="!canCheckout"
              @click="checkout"
            >
              確認下單
            </el-button>

            <div class="hint">下單後商家即開始備貨</div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()

const deliveryType = ref('pickup')
const pickupLocations = ref([])
const pickupLocationId = ref('')
const pickupTimeSlot = ref('')
const deliveryAddress = ref('')
const addressError = ref('')
const addressOk = ref(false)
const submitting = ref(false)

const selectedLocation = computed(
  () => pickupLocations.value.find((l) => l.id === pickupLocationId.value)
)

const canCheckout = computed(() => {
  if (deliveryType.value === 'pickup') return !!pickupLocationId.value
  return !!deliveryAddress.value && addressOk.value
})

async function validateAddress() {
  addressError.value = ''
  addressOk.value = false
  if (!deliveryAddress.value) return
  try {
    await api.post('/pickup/validate-address', { address: deliveryAddress.value })
    addressOk.value = true
  } catch (e) {
    addressError.value = e.response?.data?.detail || '地址超出配送範圍'
  }
}

async function checkout() {
  submitting.value = true
  try {
    const payload = {
      user_id: authStore.user?.id || '00000000-0000-0000-0000-000000000001',
      items: cartStore.items.map((i) => ({
        product_id: i.product.id,
        variant_id: i.variantId || null,
        quantity: i.quantity,
      })),
      delivery_type: deliveryType.value,
      pickup_location_id: deliveryType.value === 'pickup' ? pickupLocationId.value : null,
      pickup_time_slot: deliveryType.value === 'pickup' ? pickupTimeSlot.value : null,
      delivery_address: deliveryType.value === 'delivery' ? deliveryAddress.value : null,
    }
    const { data } = await api.post('/orders/checkout', payload)
    cartStore.clear()
    router.push(`/checkout/result?payment_id=${data.payment_id}&total=${data.total_amount}`)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '下單失敗，請稍後再試')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/pickup/locations').catch(() => ({ data: [] }))
  pickupLocations.value = data
})
</script>

<style scoped>
.page-title { margin-bottom: 28px; font-size: 24px; font-weight: 700; color: var(--text-1); }

/* Cart items */
.cart-item {
  margin-bottom: 12px;
  border-radius: var(--r-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-xs) !important;
}
.item-row { display: flex; align-items: center; gap: 16px; }
.item-img { width: 88px; height: 88px; object-fit: cover; border-radius: var(--r-sm); flex-shrink: 0; }
.item-info { flex: 1; min-width: 0; }
.item-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; color: var(--text-1); }
.item-variant {
  display: inline-block;
  font-size: 11px; color: var(--brand);
  background: var(--brand-light);
  padding: 2px 8px; border-radius: 99px;
  margin-bottom: 6px;
}
.item-price { font-size: 17px; color: var(--brand); font-weight: 700; }

/* Checkout card */
.checkout-card {
  position: sticky; top: 80px;
  border-radius: var(--r-lg) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
.checkout-card h3 { font-size: 15px; font-weight: 700; margin-bottom: 14px; color: var(--text-1); }
.delivery-group { display: flex; flex-direction: column; gap: 10px; }
.addr-error { font-size: 12px; color: var(--danger); margin-top: 6px; }
.addr-ok { font-size: 12px; color: var(--success); font-weight: 600; margin-top: 6px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.summary-row span:first-child { font-size: 14px; color: var(--text-2); }
.total { font-size: 24px; font-weight: 800; color: var(--brand); }
.hint { text-align: center; font-size: 12px; color: var(--text-3); margin-top: 10px; }
</style>
