import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import ChatLayout from '../views/ChatLayout.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      name: 'home',
      component: ChatLayout,
      meta: { requiresAuth: true }
    }
  ]
});

router.beforeEach((to, from, next) => {
    const token = sessionStorage.getItem('auth_token');
    if (to.meta.requiresAuth && !token) {
        next('/login');
    } else {
        next();
    }
});

export default router;
