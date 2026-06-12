<template>
  <div class="login-page">
    <div class="glow glow-1" />
    <div class="glow glow-2" />

    <div class="login-card">
      <div class="card-top">
        <div class="logo-mark">⚙</div>
        <div class="card-title">Platform Admin</div>
        <p class="card-sub">新竹團購平台 · 管理後台</p>
      </div>

      <el-form :model="form" @submit.prevent="submit" label-position="top" class="login-form">
        <el-form-item>
          <template #label><span class="field-label">管理員帳號</span></template>
          <el-input v-model="form.email" type="email" placeholder="admin@example.com" size="large" />
        </el-form-item>
        <el-form-item>
          <template #label><span class="field-label">密碼</span></template>
          <el-input v-model="form.password" type="password" show-password placeholder="••••••••" size="large" />
        </el-form-item>
        <el-button
          type="primary" native-type="submit" size="large"
          style="width:100%;height:48px;font-size:15px;font-weight:700;border-radius:10px;margin-top:4px"
          :loading="loading"
        >
          進入管理後台
        </el-button>
      </el-form>

      <div class="security-note">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        此頁面僅供授權管理員存取
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAdminAuthStore } from '../stores/auth'

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const router = useRouter()
const authStore = useAdminAuthStore()

async function submit() {
  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    router.push('/')
  } catch {
    ElMessage.error('帳號密碼錯誤，或非管理員帳號')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700&display=swap');

.login-page {
  min-height: 100vh;
  background: #020817;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Inter', 'Noto Sans TC', system-ui, sans-serif;
  position: relative; overflow: hidden;
  padding: 24px;
}
.glow {
  position: absolute; border-radius: 50%;
  filter: blur(80px); pointer-events: none; opacity: .35;
}
.glow-1 { width: 500px; height: 500px; background: #3B82F6; top: -150px; left: -100px; }
.glow-2 { width: 400px; height: 400px; background: #8B5CF6; bottom: -100px; right: -80px; }

.login-card {
  position: relative; z-index: 1;
  width: 100%; max-width: 420px;
  background: rgba(15,23,42,.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 20px;
  padding: 48px 44px;
  box-shadow: 0 32px 80px rgba(0,0,0,.6);
}

.card-top { text-align: center; margin-bottom: 36px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.logo-mark {
  width: 54px; height: 54px; border-radius: 16px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; box-shadow: 0 8px 24px rgba(59,130,246,.4);
}
.card-title { font-size: 22px; font-weight: 800; color: #fff; letter-spacing: -.5px; }
.card-sub { font-size: 13px; color: #475569; }

.login-form { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 13px; font-weight: 600; color: #94A3B8; }

/* Override Element dark bg */
:deep(.el-input__wrapper) {
  background: rgba(255,255,255,.05) !important;
  border-color: rgba(255,255,255,.1) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
}
:deep(.el-input__inner) { color: #E2E8F0 !important; }
:deep(.el-input__inner::placeholder) { color: #475569 !important; }
:deep(.el-form-item__label) { color: #94A3B8 !important; }

.security-note {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  margin-top: 24px;
  font-size: 12px; color: #334155;
}
</style>
