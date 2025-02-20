// import { createRouter, createWebHistory } from 'vue-router';
import { createRouter, createWebHistory, NavigationGuardNext, RouteLocationNormalized, Router, RouteRecordRaw } from 'vue-router'
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import Diniao from '../components/Diniao.vue';
import userinfo from '../components/userinfo.vue';
function getCookie(name: string): string | null {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/diniao', component: Diniao},
  { path: '/userinfo', component: userinfo},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});
export const defaultBeforeEach = (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (['/login','/register', '/404', '/403', '/500'].includes(to.path)) {
    next()
    return
  }
  if (getCookie('token')) {
    next()
  } else {
    next({ path: '/login' })
  }
  }
// 每次路由跳转前执行 defaultBeforeEach 中的逻辑。
router.beforeEach(defaultBeforeEach)
export default router;
