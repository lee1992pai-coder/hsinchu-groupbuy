<template>
  <div class="result-wrap">
    <el-result icon="success" title="訂單建立成功！">
      <template #sub-title>
        <p class="sub">訂單編號：<b>{{ paymentId }}</b></p>
        <p class="sub">總金額：<b style="color:#f56c6c">NT$ {{ Number(total).toLocaleString() }}</b></p>
      </template>
      <template #extra>
        <el-card class="cash-card">
          <div class="cash-icon">💵</div>
          <div class="cash-title">付款方式：現場付款</div>
          <div class="cash-desc">請於取貨 / 收貨時，以現金支付給商家或配送人員。</div>
          <el-steps direction="vertical" :active="1" class="steps">
            <el-step title="訂單已確認" description="商家收到您的訂單，開始備貨" status="finish" />
            <el-step title="備貨中" description="商家正在準備您的商品" />
            <el-step title="可取貨 / 配送中" description="系統會推播通知您" />
            <el-step title="現場付款完成" description="完成取貨並支付款項" />
          </el-steps>
        </el-card>

        <div class="btn-row">
          <el-button type="primary" @click="$router.push('/orders')">查看訂單狀態</el-button>
          <el-button @click="$router.push('/')">繼續購物</el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
const paymentId = route.query.payment_id?.slice(0, 8).toUpperCase() || '--------'
const total = route.query.total || 0
</script>

<style scoped>
.result-wrap { max-width: 520px; margin: 40px auto; }
.sub { color: #606266; margin: 4px 0; }
.cash-card { text-align: center; padding: 8px; margin-bottom: 20px; }
.cash-icon { font-size: 48px; margin-bottom: 8px; }
.cash-title { font-size: 18px; font-weight: bold; margin-bottom: 6px; color: #e6a23c; }
.cash-desc { font-size: 14px; color: #606266; margin-bottom: 20px; }
.steps { text-align: left; }
.btn-row { display: flex; gap: 12px; justify-content: center; }
</style>
