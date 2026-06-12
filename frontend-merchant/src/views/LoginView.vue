<template>
  <div class="login-page">
    <div class="login-bg-pattern" />

    <div class="login-box">
      <!-- Left panel -->
      <div class="login-left">
        <div class="left-brand">
          <div class="left-icon">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="rgba(255,255,255,.15)"/>
              <path d="M7 10h14M7 14h10M7 18h12" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="21" cy="18" r="3" fill="#F59E0B"/>
            </svg>
          </div>
          <span class="left-title">新竹團購平台</span>
        </div>
        <h1 class="left-heading">商家後台</h1>
        <p class="left-desc">管理商品、追蹤訂單、匯出揀貨單，一站搞定所有業務</p>
        <ul class="left-features">
          <li>🛍️ 商品與規格管理</li>
          <li>🔔 即時訂單推播通知</li>
          <li>📊 營業額與分潤報表</li>
          <li>📋 一鍵匯出揀貨單</li>
        </ul>
      </div>

      <!-- Right: Form -->
      <div class="login-right">
        <div class="form-header">
          <h2>歡迎回來</h2>
          <p>請輸入您的商家帳號</p>
        </div>

        <el-form :model="form" @submit.prevent="submit" label-position="top" class="login-form">
          <el-form-item label="電子郵件">
            <el-input v-model="form.email" type="email" placeholder="merchant@example.com" size="large" />
          </el-form-item>
          <el-form-item label="密碼">
            <el-input v-model="form.password" type="password" show-password placeholder="••••••••" size="large" />
          </el-form-item>
          <el-button
            type="primary" native-type="submit" size="large"
            style="width:100%;height:48px;font-size:15px;font-weight:700;border-radius:10px"
            :loading="loading"
          >
            登入後台
          </el-button>
        </el-form>

        <p class="form-note">帳號須通過平台審核後方可登入</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function submit() {
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push('/')
  } catch {
    ElMessage.error('帳號或密碼錯誤，或帳號尚未通過審核')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');

.login-page {
  min-height: 100vh;
  background: #0F172A;
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
  font-family: 'Inter', 'Noto Sans TC', system-ui, sans-serif;
  position: relative;
  overflow: hidden;
}
.login-bg-pattern {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(37,99,235,.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139,92,246,.10) 0%, transparent 40%);
}

.login-box {
  position: relative;
  display: flex;
  width: 100%; max-width: 880px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 32px 80px rgba(0,0,0,.5);
}

/* Left */
.login-left {
  flex: 1;
  background: linear-gradient(160deg, #1E40AF 0%, #1D4ED8 50%, #2563EB 100%);
  padding: 52px 44px;
  display: flex; flex-direction: column; gap: 20px;
  color: #fff;
}
.left-brand { display: flex; align-items: center; gap: 10px; }
.left-icon {
  width: 42px; height: 42px; border-radius: 10px;
  background: rgba(255,255,255,.15);
  display: flex; align-items: center; justify-content: center;
}
.left-title { font-size: 15px; font-weight: 700; opacity: .9; }

.left-heading { font-size: 36px; font-weight: 800; line-height: 1.2; letter-spacing: -1px; }
.left-desc { font-size: 14px; opacity: .7; line-height: 1.6; max-width: 280px; }
.left-features {
  list-style: none; display: flex; flex-direction: column; gap: 10px;
  margin-top: 8px;
}
.left-features li { font-size: 14px; opacity: .85; font-weight: 500; }

/* Right */
.login-right {
  width: 380px; flex-shrink: 0;
  background: #fff;
  padding: 52px 44px;
  display: flex; flex-direction: column; justify-content: center; gap: 28px;
}
.form-header h2 { font-size: 26px; font-weight: 800; color: #0F172A; letter-spacing: -.5px; }
.form-header p { font-size: 14px; color: #94A3B8; margin-top: 6px; }
.login-form { display: flex; flex-direction: column; gap: 4px; }
.form-note { font-size: 12px; color: #CBD5E1; text-align: center; }
</style>
