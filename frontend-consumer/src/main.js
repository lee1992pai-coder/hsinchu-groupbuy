import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import App from './App.vue'
import router from './router'

createApp(App)
  .use(createPinia())
  .use(router)
  .use(ElementPlus, { locale: zhTw })
  .mount('#app')
