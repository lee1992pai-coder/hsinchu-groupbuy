<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openProductDialog()">+ 新增商品</el-button>
    </div>

    <el-table :data="products" v-loading="loading" stripe @row-click="openVariants">
      <el-table-column prop="name" label="商品名稱" min-width="160" />
      <el-table-column prop="original_price" label="原價" width="100">
        <template #default="{ row }">NT$ {{ row.original_price }}</template>
      </el-table-column>
      <el-table-column prop="group_price" label="團購價" width="100">
        <template #default="{ row }">
          <span style="color:#f56c6c;font-weight:bold">NT$ {{ row.group_price }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="總庫存" width="90" />
      <el-table-column prop="min_group_size" label="成團數" width="90" />
      <el-table-column label="分類" width="100">
        <template #default="{ row }">{{ categoryLabel(row.category) }}</template>
      </el-table-column>
      <el-table-column label="狀態" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '上架' : '下架' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button text size="small" @click.stop="openProductDialog(row)">編輯</el-button>
          <el-button text size="small" type="primary" @click.stop="openVariants(row)">
            規格 ({{ row.variantCount || 0 }})
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 商品新增/編輯 Dialog -->
    <el-dialog v-model="productDialog" :title="editProduct ? '編輯商品' : '新增商品'" width="560px">
      <el-form :model="pForm" label-width="100px">
        <el-form-item label="商品名稱"><el-input v-model="pForm.name" /></el-form-item>
        <el-form-item label="商品描述">
          <el-input v-model="pForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="商品圖片">
          <div class="img-upload-row">
            <el-input v-model="pForm.image_url" placeholder="https://… 或點右側上傳" style="flex:1" />
            <el-upload
              :show-file-list="false"
              :before-upload="beforeUpload"
              :http-request="uploadImage"
              accept="image/*"
            >
              <el-button :loading="imgUploading" size="small">上傳</el-button>
            </el-upload>
          </div>
          <img v-if="pForm.image_url" :src="pForm.image_url" class="preview-img" />
        </el-form-item>
        <el-form-item label="標籤">
          <el-select v-model="pForm.tags" multiple allow-create filterable placeholder="輸入後按 Enter">
            <el-option label="今日熱門" value="今日熱門" />
            <el-option label="園區下午茶" value="園區下午茶" />
            <el-option label="限時特惠" value="限時特惠" />
            <el-option label="新品上架" value="新品上架" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="原價">
              <el-input-number v-model="pForm.original_price" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="團購價">
              <el-input-number v-model="pForm.group_price" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="庫存">
              <el-input-number v-model="pForm.stock" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成團數量">
              <el-input-number v-model="pForm.min_group_size" :min="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="分類">
          <el-select v-model="pForm.category" style="width:100%">
            <el-option label="🍱 熟食料理" value="food" />
            <el-option label="🧋 飲品茶飲" value="drink" />
            <el-option label="🍰 甜點烘焙" value="dessert" />
            <el-option label="🥩 生鮮蔬果" value="fresh" />
            <el-option label="🍿 零食點心" value="snack" />
            <el-option label="🧊 冷凍食品" value="frozen" />
            <el-option label="🥗 健康養生" value="health" />
            <el-option label="🍳 早午餐" value="brunch" />
            <el-option label="🌏 異國料理" value="international" />
            <el-option label="🎁 伴手禮" value="gift" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProduct">儲存</el-button>
      </template>
    </el-dialog>

    <!-- 規格管理 Drawer -->
    <el-drawer v-model="variantDrawer" :title="`規格管理 — ${activeProduct?.name}`" size="500px">
      <div class="variant-toolbar">
        <el-button type="primary" size="small" @click="openVariantForm()">+ 新增規格</el-button>
      </div>
      <el-table :data="variants" stripe size="small">
        <el-table-column prop="name" label="規格名稱" />
        <el-table-column prop="extra_price" label="加價" width="90">
          <template #default="{ row }">
            <span :style="{ color: row.extra_price > 0 ? '#e6a23c' : '#999' }">
              {{ row.extra_price > 0 ? `+NT$${row.extra_price}` : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="庫存" width="80" />
        <el-table-column label="操作" width="110">
          <template #default="{ row }">
            <el-button text size="small" @click="openVariantForm(row)">編輯</el-button>
            <el-button text size="small" type="danger" @click="deleteVariant(row.id)">刪除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!variants.length" description="尚未設定規格（設定後消費者可選擇）" :image-size="60" />

      <!-- 規格表單 -->
      <el-card v-if="vFormVisible" class="variant-form-card">
        <template #header>{{ editVariant ? '編輯規格' : '新增規格' }}</template>
        <el-form :model="vForm" label-width="80px" size="small">
          <el-form-item label="規格名稱">
            <el-input v-model="vForm.name" placeholder="例：原味 / 大箱 / 冷凍" />
          </el-form-item>
          <el-form-item label="SKU">
            <el-input v-model="vForm.sku" placeholder="可留空" />
          </el-form-item>
          <el-form-item label="加減價">
            <el-input-number v-model="vForm.extra_price" placeholder="0 = 同售價" />
          </el-form-item>
          <el-form-item label="庫存">
            <el-input-number v-model="vForm.stock" :min="0" />
          </el-form-item>
          <div style="display:flex;gap:8px">
            <el-button type="primary" size="small" :loading="vSaving" @click="saveVariant">儲存</el-button>
            <el-button size="small" @click="vFormVisible = false">取消</el-button>
          </div>
        </el-form>
      </el-card>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const CATEGORY_MAP = {
  food: '🍱 熟食料理', drink: '🧋 飲品茶飲', dessert: '🍰 甜點烘焙',
  fresh: '🥩 生鮮蔬果', snack: '🍿 零食點心', frozen: '🧊 冷凍食品',
  health: '🥗 健康養生', brunch: '🍳 早午餐', international: '🌏 異國料理', gift: '🎁 伴手禮',
}
function categoryLabel(key) { return CATEGORY_MAP[key] || key }

const products = ref([])
const variants = ref([])
const loading = ref(false)
const saving = ref(false)
const vSaving = ref(false)
const imgUploading = ref(false)

function beforeUpload(file) {
  if (!file.type.startsWith('image/')) { ElMessage.error('請上傳圖片檔案'); return false }
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('圖片不可超過 5 MB'); return false }
  return true
}

async function uploadImage({ file }) {
  imgUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    pForm.image_url = data.url
    ElMessage.success('圖片已上傳')
  } catch { ElMessage.error('圖片上傳失敗') }
  finally { imgUploading.value = false }
}

// 商品 dialog
const productDialog = ref(false)
const editProduct = ref(null)
const pForm = reactive({
  name: '', description: '', image_url: '', tags: [],
  original_price: 100, group_price: 80, stock: 50,
  min_group_size: 5, category: 'food',
})

// 規格 drawer
const variantDrawer = ref(false)
const activeProduct = ref(null)
const vFormVisible = ref(false)
const editVariant = ref(null)
const vForm = reactive({ name: '', sku: '', extra_price: 0, stock: 0 })

async function fetchProducts() {
  loading.value = true
  const { data } = await api.get(`/merchant/${auth.merchantId}/products`)
  products.value = data
  loading.value = false
}

function openProductDialog(p = null) {
  editProduct.value = p
  Object.assign(pForm, p
    ? { ...p, tags: p.tags || [] }
    : { name: '', description: '', image_url: '', tags: [], original_price: 100, group_price: 80, stock: 50, min_group_size: 5, category: 'food' }
  )
  productDialog.value = true
}

async function saveProduct() {
  saving.value = true
  try {
    if (editProduct.value) {
      await api.put(`/merchant/${auth.merchantId}/products/${editProduct.value.id}`, pForm)
    } else {
      await api.post(`/merchant/${auth.merchantId}/products`, pForm)
    }
    ElMessage.success('已儲存')
    productDialog.value = false
    await fetchProducts()
  } catch { ElMessage.error('儲存失敗') }
  finally { saving.value = false }
}

async function openVariants(row) {
  activeProduct.value = row
  vFormVisible.value = false
  variantDrawer.value = true
  const { data } = await api.get(`/products/${row.id}/variants`)
  variants.value = data
}

function openVariantForm(v = null) {
  editVariant.value = v
  Object.assign(vForm, v
    ? { name: v.name, sku: v.sku || '', extra_price: v.extra_price, stock: v.stock }
    : { name: '', sku: '', extra_price: 0, stock: 0 }
  )
  vFormVisible.value = true
}

async function saveVariant() {
  vSaving.value = true
  try {
    if (editVariant.value) {
      await api.put(`/products/${activeProduct.value.id}/variants/${editVariant.value.id}`, vForm)
    } else {
      await api.post(`/products/${activeProduct.value.id}/variants`, vForm)
    }
    ElMessage.success('已儲存')
    vFormVisible.value = false
    const { data } = await api.get(`/products/${activeProduct.value.id}/variants`)
    variants.value = data
  } catch { ElMessage.error('儲存失敗') }
  finally { vSaving.value = false }
}

async function deleteVariant(id) {
  await api.delete(`/products/${activeProduct.value.id}/variants/${id}`)
  variants.value = variants.value.filter((v) => v.id !== id)
  ElMessage.success('已刪除')
}

onMounted(fetchProducts)
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.variant-toolbar { margin-bottom: 12px; }
.variant-form-card { margin-top: 16px; }
.img-upload-row { display: flex; gap: 8px; align-items: center; width: 100%; }
.preview-img { width: 120px; height: 90px; object-fit: cover; border-radius: 6px; margin-top: 8px; }
</style>
