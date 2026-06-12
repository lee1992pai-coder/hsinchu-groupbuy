import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/register', component: () => import('../views/RegisterView.vue') },
  { path: '/products', component: () => import('../views/ProductListView.vue') },
  { path: '/products/:id', component: () => import('../views/ProductDetailView.vue') },
  { path: '/group-buys', component: () => import('../views/GroupBuyListView.vue') },
  { path: '/group-buys/:id', component: () => import('../views/GroupBuyDetailView.vue') },
  { path: '/cart', component: () => import('../views/CartView.vue'), meta: { auth: true } },
  { path: '/orders', component: () => import('../views/OrderListView.vue'), meta: { auth: true } },
  { path: '/checkout/result', component: () => import('../views/CheckoutResultView.vue') },
  { path: '/profile', component: () => import('../views/ProfileView.vue'), meta: { auth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.token) return '/login'
})

export default router
