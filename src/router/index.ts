import type { User } from "@/auth/interface";
import HomeView from "@/views/HomeView.vue";
import Login from "@/views/Login.vue";
import { createRouter, createWebHistory } from "vue-router";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    requiresGuest?: boolean; // Only for non-authenticated users
    roles?: ("admin" | "editor" | "user")[];
    permissions?: string[];
  }
}

export const routes = {
  home: { path: "/", name: "home" },
  login: { path: "/login", name: "login" },
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: routes.home.path,
      name: routes.home.name,
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: routes.login.path,
      name: routes.login.name,
      component: Login,
      meta: { guestOnly: true },
    },
  ],
});

router.beforeEach((to, _, next) => {
  const user: User | null = JSON.parse(localStorage.getItem("user")!);
  // Check if route requires authentication
  if (to.meta.requiresAuth === true && user === null) {
    next({ name: routes.login.name, query: { redirect: to.fullPath } });
  }
  // // Check if route is for guests only (like login page)
  else if (to.meta.guestOnly === true && user !== null) {
    next({ name: routes.home.name });
  } else {
    next();
  }
});

export default router;
