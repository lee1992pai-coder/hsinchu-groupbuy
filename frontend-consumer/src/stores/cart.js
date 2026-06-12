import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

  function persist() {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }

  function addItem(product, quantity = 1, variantId = null, variantName = null) {
    const key = `${product.id}_${variantId || 'default'}`
    const existing = items.value.find((i) => i.key === key)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({ key, product, quantity, variantId, variantName })
    }
    persist()
  }

  function removeItem(key) {
    items.value = items.value.filter((i) => i.key !== key)
    persist()
  }

  function updateQty(key, quantity) {
    const item = items.value.find((i) => i.key === key)
    if (item) { item.quantity = quantity; persist() }
  }

  function clear() {
    items.value = []
    persist()
  }

  const total = computed(() =>
    items.value.reduce((sum, i) => sum + i.product.group_price * i.quantity, 0)
  )

  const count = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))

  return { items, total, count, addItem, removeItem, updateQty, clear }
})
