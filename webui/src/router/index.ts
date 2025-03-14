import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue';
import DashboradView from '@/views/DashboradView.vue';
import FilesViews from '@/views/FilesViews.vue';
import StoragerView from '@/views/StoragersView.vue';
import UsersView from '@/views/UsersView.vue';
import { useCookies } from 'vue3-cookies';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'dashborad',
      alias: '/dashborad',
      component: DashboradView
    },
    {
      path: '/files',
      name: 'files',
      component: FilesViews
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView
    },
    {
      path: '/storagers',
      name: 'storage',
      component: StoragerView
    }
  ],
})

const { cookies } = useCookies();

router.beforeEach((to, from) => {
  if (to.path === '/login') {
    return true;
  } else {
    let token = cookies.isKey('token');
    if (token) {
      return true;
    } else {
      return '/login';
    }
  }
})

export default router
