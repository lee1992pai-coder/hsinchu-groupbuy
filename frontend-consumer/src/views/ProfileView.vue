<template>
  <div class="profile-wrap">
    <el-card class="profile-card">
      <!-- 頭像區 -->
      <div class="avatar-section">
        <el-avatar :size="80" style="background:#409eff;font-size:32px">
          {{ form.display_name?.[0] || '我' }}
        </el-avatar>
        <h2>{{ form.display_name }}</h2>
        <p class="email-text">{{ form.email }}</p>
      </div>

      <el-form :model="form" label-width="90px" label-position="left">
        <el-form-item label="暱稱">
          <el-input v-model="form.display_name" placeholder="請輸入暱稱" />
        </el-form-item>
        <el-form-item label="手機號碼">
          <el-input v-model="form.phone" placeholder="+886912345678" />
        </el-form-item>
        <el-form-item label="常用地址">
          <el-input
            v-model="form.address"
            type="textarea" :rows="2"
            placeholder="新竹市東區○○路○○號（結帳時自動填入）"
          />
          <div class="addr-hint" v-if="form.address">
            <span v-if="isHsinchu">✅ 在配送範圍內</span>
            <span v-else style="color:#e6a23c">⚠️ 超出配送範圍，僅限新竹市/縣</span>
          </div>
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" disabled />
        </el-form-item>
      </el-form>

      <div class="btn-row">
        <el-button type="primary" :loading="saving" @click="save" style="flex:1">
          儲存變更
        </el-button>
        <el-button type="danger" plain @click="logout">登出</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { validate_delivery_address } from '../utils/logistics'

const authStore = useAuthStore()
const router = useRouter()
const saving = ref(false)

const form = reactive({ display_name: '', phone: '', email: '', address: '' })

const isHsinchu = computed(() =>
  !form.address || form.address.startsWith('新竹')
)

onMounted(async () => {
  const userId = authStore.user?.id
  if (!userId) return
  try {
    const { data } = await api.get(`/users/${userId}`)
    Object.assign(form, data)
    authStore.user = data
  } catch {
    // 用本地快取
    Object.assign(form, authStore.user || {})
  }
})

async function save() {
  saving.value = true
  try {
    const userId = authStore.user?.id
    const { data } = await api.patch(`/users/${userId}`, {
      display_name: form.display_name,
      phone: form.phone,
      address: form.address,
    })
    authStore.user = { ...authStore.user, ...data }
    localStorage.setItem('user', JSON.stringify(authStore.user))
    ElMessage.success('已儲存')
  } catch {
    ElMessage.error('儲存失敗')
  } finally {
    saving.value = false
  }
}

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.profile-wrap { display: flex; justify-content: center; padding: 20px; }
.profile-card { width: 480px; padding: 12px; }
.avatar-section { text-align: center; margin-bottom: 28px; }
.avatar-section h2 { margin: 12px 0 4px; }
.email-text { color: #909399; font-size: 14px; }
.addr-hint { font-size: 12px; margin-top: 4px; }
.btn-row { display: flex; gap: 12px; margin-top: 24px; }
</style>
