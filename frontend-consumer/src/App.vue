<template>
  <el-config-provider :locale="zhTw">
    <div class="app">

      <header class="navbar">
        <div class="navbar-inner">
          <!-- Logo -->
          <router-link to="/" class="logo">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="#2563EB"/>
              <path d="M7 10h14M7 14h10M7 18h12" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="21" cy="18" r="3" fill="#F59E0B"/>
            </svg>
            <span class="logo-text">新竹<em>團購</em></span>
          </router-link>

          <!-- Nav Links -->
          <nav class="nav-links">
            <router-link to="/products">商品瀏覽</router-link>
            <router-link to="/group-buys">
              <span class="link-badge">🔥</span> 拼團中
            </router-link>
            <router-link to="/cart" class="cart-link">
              <el-badge :value="cartStore.count || 0" :hidden="!cartStore.count" type="danger">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <path d="M16 10a4 4 0 01-8 0"/>
                </svg>
              </el-badge>
              購物車
            </router-link>

            <template v-if="authStore.token">
              <router-link to="/orders">我的訂單</router-link>
              <router-link to="/profile" class="avatar-link">
                <div class="avatar">{{ authStore.user?.display_name?.[0] || '我' }}</div>
              </router-link>
            </template>
            <template v-else>
              <router-link to="/login" class="btn-login">登入 / 註冊</router-link>
            </template>
          </nav>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>

      <footer class="footer">
        <div class="footer-inner">
          <div class="footer-brand">
            <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="#2563EB"/>
              <path d="M7 10h14M7 14h10M7 18h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="21" cy="18" r="3" fill="#F59E0B"/>
            </svg>
            <span>新竹團購平台</span>
          </div>
          <p class="footer-desc">在地好物・拼出優惠・服務範圍：新竹市、新竹縣</p>
          <p class="footer-copy">© 2025 新竹團購平台. All rights reserved.</p>
        </div>
      </footer>

    </div>
  </el-config-provider>
</template>

<script setup>
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import { useAuthStore } from './stores/auth'
import { useCartStore } from './stores/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');

:root {
  --brand:        #2563EB;
  --brand-hover:  #1D4ED8;
  --brand-light:  #EFF6FF;
  --accent:       #F59E0B;
  --accent-light: #FFFBEB;
  --success:      #059669;
  --danger:       #DC2626;
  --text-1:       #0F172A;
  --text-2:       #475569;
  --text-3:       #94A3B8;
  --bg:           #F8FAFC;
  --card:         #FFFFFF;
  --border:       #E2E8F0;
  --shadow-xs:    0 1px 2px rgba(15,23,42,.06);
  --shadow-sm:    0 1px 3px rgba(15,23,42,.08), 0 4px 12px rgba(15,23,42,.04);
  --shadow-md:    0 4px 16px rgba(15,23,42,.10), 0 1px 4px rgba(15,23,42,.06);
  --shadow-lg:    0 12px 40px rgba(15,23,42,.14), 0 4px 12px rgba(15,23,42,.06);
  --r-sm:  6px;
  --r-md:  12px;
  --r-lg:  18px;
  --r-xl:  24px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', 'Noto Sans TC', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text-1);
  -webkit-font-smoothing: antialiased;
}

/* Element Plus overrides */
.el-button--primary {
  --el-button-bg-color: var(--brand) !important;
  --el-button-border-color: var(--brand) !important;
  --el-button-hover-bg-color: var(--brand-hover) !important;
}
.el-tag--warning { background: var(--accent-light); border-color: #FDE68A; color: #92400E; }

.app { min-height: 100vh; display: flex; flex-direction: column; }

/* ── Navbar ──────────────────────────────────────────────── */
.navbar {
  position: sticky; top: 0; z-index: 200;
  background: rgba(255,255,255,.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  height: 64px;
}
.navbar-inner {
  max-width: 1280px; margin: 0 auto;
  height: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
}
.logo {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none;
}
.logo-text {
  font-size: 18px; font-weight: 700; color: var(--text-1); letter-spacing: -.5px;
}
.logo-text em { font-style: normal; color: var(--brand); }

.nav-links {
  display: flex; align-items: center; gap: 4px;
}
.nav-links a {
  display: flex; align-items: center; gap: 5px;
  text-decoration: none;
  font-size: 14px; font-weight: 500;
  color: var(--text-2);
  padding: 6px 12px; border-radius: var(--r-md);
  transition: color .15s, background .15s;
}
.nav-links a:hover { color: var(--text-1); background: var(--bg); }
.nav-links a.router-link-active { color: var(--brand); background: var(--brand-light); }
.nav-links .link-badge { font-size: 13px; }

.cart-link { position: relative; }

.avatar-link { padding: 4px !important; }
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--brand); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
}

.btn-login {
  margin-left: 8px;
  background: var(--brand) !important;
  color: #fff !important;
  padding: 7px 16px !important;
  border-radius: var(--r-md) !important;
  font-weight: 600 !important;
}
.btn-login:hover { background: var(--brand-hover) !important; color: #fff !important; }

/* ── Main ─────────────────────────────────────────────────── */
.main-content {
  max-width: 1280px; margin: 0 auto; width: 100%;
  padding: 32px 24px;
  flex: 1;
}

/* ── Footer ───────────────────────────────────────────────── */
.footer {
  background: #0F172A;
  border-top: 1px solid #1E293B;
  padding: 40px 24px;
  margin-top: auto;
}
.footer-inner {
  max-width: 1280px; margin: 0 auto;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.footer-brand {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 700; color: #fff;
}
.footer-desc { font-size: 13px; color: #64748B; }
.footer-copy { font-size: 12px; color: #475569; }
</style>
