import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/logout',
      name: 'logout',
      beforeEnter: async (to, from, next) => {
        const auth = useAuthStore()
        await auth.logout()
        next({ name: 'login' })
      },
    },
    {
      path: '/',
      name: 'home',
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          component: HomeView,
        },
      ],
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // On first load, restore user info if a token exists in sessionStorage
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      // Token is invalid or expired — clean up and send to login
      await auth.logout()
      return next({ name: 'login' })
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && auth.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
