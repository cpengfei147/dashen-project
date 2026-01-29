import { createApp } from 'vue'
import App from './App.vue'

// Vant触摸模拟（PC端调试用）
import '@vant/touch-emulator'

// Vant样式
import 'vant/lib/index.css'

// 全局样式
import './styles/main.css'

const app = createApp(App)
app.mount('#app')
