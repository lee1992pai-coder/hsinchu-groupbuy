<template>
  <div class="layout">

    <!-- 側邊欄 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="7" fill="#fff" fill-opacity=".12"/>
            <path d="M7 10h14M7 14h10M7 18h12" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="21" cy="18" r="3" fill="#F59E0B"/>
          </svg>
        </div>
        <div>
          <div class="brand-name">商家後台</div>
          <div class="brand-sub">{{ auth.merchant?.name || '管理介面' }}</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          <span class="nav-icon" v-html="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <div class="sidebar-bottom">
        <div class="sidebar-user">
          <div class="user-avatar">{{ (auth.merchant?.name || '商')[0] }}</div>
          <div class="user-info">
            <div class="user-name">{{ auth.merchant?.name || '商家帳號' }}</div>
            <div class="user-email">{{ auth.merchant?.email || '' }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="logout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
          </svg>
          登出
        </button>
      </div>
    </aside>

    <!-- 主區 -->
    <div class="main-wrap">
      <header class="topbar">
        <div class="topbar-title">{{ pageTitle }}</div>
        <div class="topbar-right">
          <span class="topbar-time">{{ currentTime }}</span>
        </div>
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const navItems = [
  {
    path: '/products', label: '商品管理',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
  },
  {
    path: '/orders', label: '訂單管理',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  },
  {
    path: '/pick-list', label: '揀貨單',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
  },
  {
    path: '/revenue', label: '分潤報表',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  },
]

const titleMap = { '/products': '商品管理', '/orders': '訂單管理', '/pick-list': '揀貨單', '/revenue': '分潤報表' }
const pageTitle = computed(() => titleMap[route.path] || '商家後台')

const currentTime = ref('')
let timerId = null
function updateTime() {
  currentTime.value = new Date().toLocaleString('zh-TW', { hour: '2-digit', minute: '2-digit', weekday: 'short' })
}
onMounted(() => { updateTime(); timerId = setInterval(updateTime, 60000) })
onUnmounted(() => clearInterval(timerId))

function logout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');

:root {
  --s-bg:     #0F172A;
  --s-hover:  #1E293B;
  --s-active: #2563EB;
  --s-border: rgba(255,255,255,.08);
  --s-text:   #94A3B8;
  --s-text2:  #CBD5E1;
}

.layout {
  display: flex; height: 100vh;
  font-family: 'Inter', 'Noto Sans TC', system-ui, sans-serif;
  background: #F8FAFC;
}

/* ── Sidebar ──────────────────────────────────────────────── */
.sidebar {
  width: 240px; flex-shrink: 0;
  background: var(--s-bg);
  display: flex; flex-direction: column;
  border-right: 1px solid var(--s-border);
}

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 22px 20px;
  border-bottom: 1px solid var(--s-border);
}
.brand-icon {
  width: 38px; height: 38px; border-radius: 10px;
  background: #2563EB;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.brand-name { font-size: 14px; font-weight: 700; color: #fff; line-height: 1; }
.brand-sub { font-size: 11px; color: var(--s-text); margin-top: 3px; }

/* Nav */
.sidebar-nav {
  flex: 1; padding: 12px 10px;
  display: flex; flex-direction: column; gap: 3px;
  overflow-y: auto;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  text-decoration: none; color: var(--s-text);
  font-size: 14px; font-weight: 500;
  transition: background .15s, color .15s;
  position: relative;
}
.nav-item:hover { background: var(--s-hover); color: var(--s-text2); }
.nav-item.router-link-active {
  background: rgba(37,99,235,.2);
  color: #60A5FA;
}
.nav-item.router-link-active .nav-icon { color: #60A5FA; }
.nav-icon { flex-shrink: 0; display: flex; }
.nav-icon :deep(svg) { stroke: currentColor; }
.nav-badge {
  margin-left: auto;
  background: #DC2626; color: #fff;
  font-size: 10px; font-weight: 700;
  padding: 1px 6px; border-radius: 99px;
}

/* Bottom */
.sidebar-bottom {
  border-top: 1px solid var(--s-border);
  padding: 14px 16px;
  display: flex; flex-direction: column; gap: 12px;
}
.sidebar-user { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: #2563EB;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #fff;
  flex-shrink: 0;
}
.user-name { font-size: 13px; font-weight: 600; color: #E2E8F0; }
.user-email { font-size: 11px; color: var(--s-text); margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 150px; }
.logout-btn {
  display: flex; align-items: center; gap: 7px;
  background: none; border: 1px solid var(--s-border);
  border-radius: 7px; padding: 7px 12px;
  color: var(--s-text); font-size: 13px; cursor: pointer;
  transition: all .15s; width: 100%;
}
.logout-btn:hover { background: var(--s-hover); color: var(--s-text2); border-color: transparent; }

/* ── Main ──────────────────────────────────────────────────── */
.main-wrap { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.topbar {
  height: 58px; background: #fff;
  border-bottom: 1px solid #E2E8F0;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
  flex-shrink: 0;
}
.topbar-title { font-size: 17px; font-weight: 700; color: #0F172A; }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.topbar-time { font-size: 13px; color: #94A3B8; }
.main-content {
  flex: 1; overflow-y: auto;
  background: #F8FAFC;
  padding: 28px;
}
</style>
