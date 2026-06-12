<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>登入</h2>
      <el-form :model="form" @submit.prevent="submit" label-position="top">
        <el-form-item label="Email">
          <el-input v-model="form.email" type="email" placeholder="your@email.com" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">
          登入
        </el-button>
      </el-form>
      <div class="auth-link">
        還沒有帳號？<router-link to="/register">立即註冊</router-link>
      </div>
    </el-card>
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
const authStore = useAuthStore()

async function submit() {
  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    router.push('/')
  } catch {
    ElMessage.error('帳號或密碼錯誤')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap { display: flex; justify-content: center; padding: 40px 0; }
.auth-card { width: 400px; padding: 20px; }
.auth-card h2 { margin-bottom: 24px; }
.auth-link { margin-top: 16px; text-align: center; font-size: 14px; }
</style>
