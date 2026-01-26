import { routes } from "@/router";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import type { User } from "./interface";

export function useAuth() {
  const user = ref<User | null>(JSON.parse(localStorage.getItem("user")!));
  const router = useRouter();

  const isAuthenticated = computed(() => user.value !== null);

  const login = (userData: User) => {
    localStorage.setItem("user", JSON.stringify(userData));
    user.value = userData;
    router.push(routes.home.path);
  };

  return { user, isAuthenticated, login };
}
