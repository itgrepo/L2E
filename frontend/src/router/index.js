import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MonitorView from '../views/MonitorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/catalog',
      name: 'catalog',
      component: () => import('../views/CatalogView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dataset/:id',
      name: 'dataset-detail',
      component: () => import('../views/DatasetDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/api-management',
      name: 'api-management',
      component: () => import('../views/APIManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/api-monitor',
      name: 'api-monitor',
      component: () => import('../views/ApiMonitorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/ContactView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/dataset-config',
      name: 'dataset-config',
      component: () => import('../views/DatasetConfigView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/verify/:token',
      name: 'verify-email',
      component: () => import('../views/VerifyEmailView.vue')
    },
    {
      path: '/user-approval',
      name: 'user-approval',
      component: () => import('../views/UserApprovalView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/user-management',
      name: 'user-management',
      component: () => import('../views/UserManagementView.vue')
    },
    {
      path: '/permission-management',
      name: 'permission-management',
      component: () => import('../views/PermissionManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/group-user-management',
      name: 'group-user-management',
      component: () => import('../views/GroupUserManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dataset-management',
      name: 'dataset-management',
      component: () => import('../views/DatasetManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/group-dataset-management',
      name: 'group-dataset-management',
      component: () => import('../views/GroupDatasetManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dataset-permission-monitor',
      name: 'dataset-permission-monitor',
      component: () => import('../views/DatasetPermissionMonitorView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('../views/FavoritesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/organization-management',
      name: 'organization-management',
      component: () => import('../views/OrganizationManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/category-management',
      name: 'category-management',
      component: () => import('../views/CategoryManagementView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/monitor',
      name: 'monitor',
      component: MonitorView,
      meta: { requiresAuth: true }
    }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  
  if (to.meta.requiresAuth && !user) {
    next({ name: 'login' });
  } else {
    next();
  }
});

export default router
