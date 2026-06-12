<template>
  <div class="layout">

    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">⚙</div>
        <div>
          <div class="brand-name">Platform Admin</div>
          <div class="brand-sub">新竹團購平台</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          <span class="nav-icon" v-html="item.icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-bottom">
        <div class="admin-info">
          <div class="admin-dot" />
          <span>{{ authStore.admin?.display_name || '管理員' }}</span>
        </div>
        <button class="logout-btn" @click="logout">登出</button>
      </div>
    </aside>

    <div class="main-wrap">
      <header class="topbar">
        <div class="topbar-left">
          <div class="breadcrumb">管理後台</div>
          <h1 class="topbar-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-badge">Admin Console</div>
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAdminAuthStore()

const navItems = [
  {
    path: '/dashboard', label: '平台總覽',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  },
  {
    path: '/merchants', label: '商家管理',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
  },
  {
    path: '/banners', label: 'Banner 管理',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
  },
  {
    path: '/broadcast', label: '全站推播',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>',
  },
  {
    path: '/revenue', label: '帳務報表',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
  },
]

const titleMap = {
  '/dashboard': '平台總覽', '/merchants': '商家管理',
  '/banners': 'Banner 管理', '/broadcast': '全站推播', '/revenue': '帳務報表',
}
const pageTitle = computed(() => titleMap[route.path] || '管理後台')

function logout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');

.layout {
  display: flex; height: 100vh;
  font-family: 'Inter', 'Noto Sans TC', system-ui, sans-serif;
}

/* ── Sidebar ──────────────────────────────────────────────── */
.sidebar {
  width: 240px; flex-shrink: 0;
  background: #020817;
  display: flex; flex-direction: column;
  border-right: 1px solid rgba(255,255,255,.06);
}

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 22px 18px;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.brand-mark {
  width: 36px; height: 36px; border-radius: 9px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.brand-name { font-size: 14px; font-weight: 700; color: #fff; }
.brand-sub { font-size: 11px; color: #475569; margin-top: 2px; }

.sidebar-nav {
  flex: 1; padding: 14px 10px;
  display: flex; flex-direction: column; gap: 2px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  text-decoration: none; color: #64748B;
  font-size: 14px; font-weight: 500;
  transition: all .15s;
}
.nav-item:hover { background: #0F172A; color: #CBD5E1; }
.nav-item.router-link-active { background: rgba(59,130,246,.15); color: #60A5FA; }
.nav-icon { display: flex; flex-shrink: 0; }
.nav-icon :deep(svg) { stroke: currentColor; }

.sidebar-bottom {
  border-top: 1px solid rgba(255,255,255,.06);
  padding: 14px 18px;
  display: flex; justify-content: space-between; align-items: center;
}
.admin-info {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #94A3B8;
}
.admin-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 0 3px rgba(16,185,129,.2);
}
.logout-btn {
  background: none; border: 1px solid rgba(255,255,255,.1);
  border-radius: 6px; padding: 5px 12px;
  color: #64748B; font-size: 12px; cursor: pointer;
  transition: all .15s;
}
.logout-btn:hover { background: #0F172A; color: #CBD5E1; border-color: rgba(255,255,255,.2); }

/* ── Main ──────────────────────────────────────────────────── */
.main-wrap { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #F8FAFC; }
.topbar {
  height: 62px; background: #fff;
  border-bottom: 1px solid #E2E8F0;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px; flex-shrink: 0;
}
.topbar-left { display: flex; flex-direction: column; gap: 2px; }
.breadcrumb { font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: .8px; font-weight: 600; }
.topbar-title { font-size: 18px; font-weight: 700; color: #0F172A; line-height: 1; }
.topbar-badge {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  color: #fff; font-size: 11px; font-weight: 700;
  padding: 4px 12px; border-radius: 99px;
  letter-spacing: .5px;
}
.main-content {
  flex: 1; overflow-y: auto;
  padding: 28px 32px;
}
</style>
