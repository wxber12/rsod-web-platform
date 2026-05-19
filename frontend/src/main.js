import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js' // 引⼊路由

// ======= 🎯 核心：补上 Element Plus 的 JS 和 CSS 样式 =======
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

// 启⽤路由
app.use(router)

// ======= 🎯 核心：注册启用 Element Plus =======
app.use(ElementPlus)

app.mount('#app')