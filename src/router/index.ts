import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

export enum RoutePaths {
  HOME = "/",
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: RoutePaths.HOME,
      name: "home",
      component: HomeView,
    },
  ],
});

export default router;
