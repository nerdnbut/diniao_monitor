import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import { createPinia } from 'pinia';

// 设置axios的请求基础路径
axios.defaults.baseURL = 'http://127.0.0.1:8000/api/';
axios.defaults.withCredentials = true;

// 创建 Pinia 实例
const pinia = createPinia();
// 注册应用
createApp(App)
  .use(router)
  .use(pinia)
  .mount('#app');
