<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openDialog()">+ 新增 Banner</el-button>
    </div>

    <!-- 預覽區 -->
    <el-card class="preview-card">
      <template #header>📱 消費者端首頁預覽</template>
      <el-carousel height="160px" v-if="activeBanners.length">
        <el-carousel-item v-for="b in activeBanners" :key="b.id">
          <img :src="b.image_url" class="preview-img" :alt="b.title" />
        </el-carousel-item>
      </el-carousel>
      <el-empty v-else description="目前無啟用的 Banner" :image-size="60" />
    </el-card>

    <!-- 列表 -->
    <el-table :data="banners" stripe class="banner-table">
      <el-table-column label="預覽圖" width="120">
        <template #default="{ row }">
          <img :src="row.image_url" class="thumb" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="標題" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="狀態" width="100">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" @change="toggleBanner(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">編輯</el-button>
          <el-button size="small" type="danger" @click="deleteBanner(row.id)">刪除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="editTarget ? '編輯 Banner' : '新增 Banner'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="標題"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="圖片 URL">
          <el-input v-model="form.image_url" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="連結 URL">
          <el-input v-model="form.link_url" placeholder="可留空" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="啟用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">儲存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const banners = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const editTarget = ref(null)

const form = reactive({ title: '', image_url: '', link_url: '', sort_order: 0, is_active: true })
const activeBanners = computed(() => banners.value.filter((b) => b.is_active))

async function fetchBanners() {
  const { data } = await api.get('/admin/banners')
  banners.value = data
}

function openDialog(banner = null) {
  editTarget.value = banner
  Object.assign(form, banner
    ? { ...banner }
    : { title: '', image_url: '', link_url: '', sort_order: 0, is_active: true }
  )
  dialogVisible.value = true
}

async function save() {
  saving.value = true
  try {
    if (editTarget.value) {
      await api.put(`/admin/banners/${editTarget.value.id}`, form)
    } else {
      await api.post('/admin/banners', form)
    }
    ElMessage.success('已儲存')
    dialogVisible.value = false
    await fetchBanners()
  } catch { ElMessage.error('儲存失敗') }
  finally { saving.value = false }
}

async function toggleBanner(banner) {
  await api.put(`/admin/banners/${banner.id}`, { ...banner })
}

async function deleteBanner(id) {
  await ElMessageBox.confirm('確定要刪除此 Banner？', '確認', { type: 'warning' })
  await api.delete(`/admin/banners/${id}`)
  ElMessage.success('已刪除')
  await fetchBanners()
}

onMounted(fetchBanners)
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.preview-card { margin-bottom: 20px; }
.preview-img { width: 100%; height: 160px; object-fit: cover; }
.banner-table { margin-top: 16px; }
.thumb { width: 100px; height: 56px; object-fit: cover; border-radius: 6px; }
</style>
