import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    component: () => import('../views/DashboardLayout.vue'),
    meta: { auth: true },
    children: [
      { path: '', redirect: '/products' },
      { path: 'products', component: () => import('../views/ProductsView.vue') },
      { path: 'orders', component: () => import('../views/OrdersView.vue') },
      { path: 'pick-list', component: () => import('../views/PickListView.vue') },
      { path: 'revenue', component: () => import('../views/RevenueView.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.token) return '/login'
})

export default router
