import { createRouter, createWebHistory } from 'vue-router'
import { useAdminAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    component: () => import('../views/AdminLayout.vue'),
    meta: { auth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'merchants', component: () => import('../views/MerchantsView.vue') },
      { path: 'banners', component: () => import('../views/BannersView.vue') },
      { path: 'broadcast', component: () => import('../views/BroadcastView.vue') },
      { path: 'revenue', component: () => import('../views/RevenueView.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const authStore = useAdminAuthStore()
  if (to.meta.auth && !authStore.isLoggedIn) return '/login'
})

export default router
