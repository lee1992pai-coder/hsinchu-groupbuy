<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>建立帳號</h2>

      <!-- 社群登入 -->
      <div class="social-btns">
        <el-button class="social-btn line" @click="loginLine">
          <img src="https://upload.wikimedia.org/wikipedia/commons/4/41/LINE_logo.svg" width="18" /> LINE 登入
        </el-button>
        <el-button class="social-btn google" @click="loginGoogle">
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18" /> Google 登入
        </el-button>
      </div>

      <el-divider>或使用手機簡訊</el-divider>

      <!-- SMS OTP 流程 -->
      <template v-if="!otpSent">
        <el-form label-position="top">
          <el-form-item label="手機號碼">
            <el-input v-model="phone" placeholder="+886912345678" />
          </el-form-item>
          <el-button type="primary" style="width:100%" @click="sendOtp" :loading="sending">
            發送驗證碼
          </el-button>
        </el-form>
      </template>

      <template v-else>
        <el-form label-position="top">
          <el-form-item :label="`驗證碼（已發送至 ${phone}）`">
            <el-input v-model="otp" placeholder="6 位數字" maxlength="6" />
          </el-form-item>
          <el-button type="primary" style="width:100%" @click="verifyOtp" :loading="verifying">
            驗證並登入
          </el-button>
          <el-button text @click="otpSent = false; otp = ''" style="width:100%;margin-top:8px">
            重新發送
          </el-button>
        </el-form>
      </template>

      <el-divider>或用 Email 註冊</el-divider>

      <el-form :model="form" label-position="top">
        <el-form-item label="Email">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        <el-form-item label="暱稱">
          <el-input v-model="form.display_name" />
        </el-form-item>
        <el-form-item label="手機">
          <el-input v-model="form.phone" placeholder="+886912345678" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" style="width:100%" @click="register" :loading="loading">
          完成註冊
        </el-button>
      </el-form>

      <div class="auth-link">已有帳號？<router-link to="/login">立即登入</router-link></div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const form = reactive({ email: '', display_name: '', phone: '', password: '' })
const phone = ref('')
const otp = ref('')
const otpSent = ref(false)
const sending = ref(false)
const verifying = ref(false)
const loading = ref(false)
const router = useRouter()
const authStore = useAuthStore()

async function sendOtp() {
  if (!phone.value) return ElMessage.warning('請輸入手機號碼')
  sending.value = true
  try {
    await api.post('/auth/sms/send', { phone: phone.value })
    otpSent.value = true
    ElMessage.success('驗證碼已發送')
  } catch { ElMessage.error('發送失敗') }
  finally { sending.value = false }
}

async function verifyOtp() {
  verifying.value = true
  try {
    const { data } = await api.post('/auth/sms/verify', { phone: phone.value, code: otp.value })
    localStorage.setItem('token', data.access_token)
    router.push('/')
  } catch { ElMessage.error('驗證碼錯誤') }
  finally { verifying.value = false }
}

async function register() {
  loading.value = true
  try {
    await authStore.register(form)
    router.push('/')
  } catch { ElMessage.error('註冊失敗，Email 可能已被使用') }
  finally { loading.value = false }
}

// LINE/Google 為前端 OAuth redirect，實際需配置 OAuth client
function loginLine() {
  window.location.href = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${import.meta.env.VITE_LINE_CLIENT_ID}&redirect_uri=${encodeURIComponent(window.location.origin + '/auth/line/callback')}&state=csrf&scope=profile`
}
function loginGoogle() {
  ElMessage.info('Google 登入需配置 Google OAuth Client ID')
}
</script>

<style scoped>
.auth-wrap { display: flex; justify-content: center; padding: 40px 20px; }
.auth-card { width: 420px; padding: 24px; }
.auth-card h2 { margin-bottom: 20px; }
.social-btns { display: flex; flex-direction: column; gap: 10px; margin-bottom: 8px; }
.social-btn { display: flex; align-items: center; gap: 8px; justify-content: center; width: 100%; height: 44px; }
.social-btn.line { background: #00b900; color: #fff; border: none; }
.social-btn.google { background: #fff; border: 1px solid #e4e7ed; }
.auth-link { margin-top: 16px; text-align: center; font-size: 14px; }
</style>
