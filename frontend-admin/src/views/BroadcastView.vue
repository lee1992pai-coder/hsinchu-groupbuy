<template>
  <div>
    <el-card class="broadcast-card">
      <template #header>📢 發送全站推播通知</template>

      <el-form :model="form" label-width="100px" label-position="top">
        <el-form-item label="通知標題">
          <el-input v-model="form.title" placeholder="例：本週新團開跑！" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="通知內容">
          <el-input
            v-model="form.body"
            type="textarea" :rows="4"
            placeholder="例：竹科最受歡迎的辣味肉乾團購來了，快來搶！"
            maxlength="200" show-word-limit
          />
        </el-form-item>

        <!-- 預覽 -->
        <el-form-item label="手機通知預覽">
          <div class="phone-preview">
            <div class="notif-bar">
              <span class="app-name">新竹團購</span>
              <span class="notif-time">現在</span>
            </div>
            <div class="notif-title">{{ form.title || '通知標題' }}</div>
            <div class="notif-body">{{ form.body || '通知內容…' }}</div>
          </div>
        </el-form-item>

        <el-button
          type="primary" size="large"
          :loading="sending"
          :disabled="!form.title || !form.body"
          @click="sendBroadcast"
        >
          🚀 發送給全部用戶
        </el-button>
      </el-form>

      <el-divider />

      <div class="history-section">
        <h3>發送記錄</h3>
        <el-table :data="history" empty-text="尚無發送記錄" size="small">
          <el-table-column prop="title" label="標題" />
          <el-table-column prop="sent" label="發送人數" width="100" />
          <el-table-column prop="time" label="發送時間" width="160" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'

const form = reactive({ title: '', body: '' })
const sending = ref(false)
const history = ref([])

async function sendBroadcast() {
  await ElMessageBox.confirm(
    `確定要對所有用戶發送推播「${form.title}」？`,
    '確認發送',
    { type: 'warning', confirmButtonText: '確認發送', cancelButtonText: '取消' }
  )
  sending.value = true
  try {
    const { data } = await api.post('/admin/broadcast', { title: form.title, body: form.body })
    ElMessage.success(`已發送給 ${data.sent} 位用戶`)
    history.value.unshift({
      title: form.title,
      sent: data.sent,
      time: dayjs().format('MM/DD HH:mm'),
    })
    form.title = ''
    form.body = ''
  } catch { ElMessage.error('發送失敗') }
  finally { sending.value = false }
}
</script>

<style scoped>
.broadcast-card { max-width: 640px; }
.phone-preview {
  background: #1c1c1e; color: #fff; border-radius: 16px;
  padding: 14px 16px; width: 300px; font-size: 13px;
}
.notif-bar { display: flex; justify-content: space-between; margin-bottom: 6px; opacity: .6; font-size: 11px; }
.app-name { font-weight: 600; }
.notif-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.notif-body { opacity: .85; line-height: 1.4; }
.history-section h3 { margin-bottom: 12px; }
</style>
