import userRepository from "@/api/repositories/user.repository";
import type { User } from "@/auth/interface";
import { routes } from "@/router";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

type LoginData = Omit<User, "id">;

export function useAuth() {
  const user = ref<LoginData | null>(JSON.parse(localStorage.getItem("user")!));
  const router = useRouter();

  const isAuthenticated = computed(() => user.value !== null);

  const login = async (userData: LoginData) => {
    await loginUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    user.value = userData;
    router.push(routes.home.path);
  };

  const loginUser = async (userData: LoginData) => {
    const user = await userRepository.userLogin({
      firstName: userData.name,
      phoneNumber: userData.phoneNumber,
    });
    return user;
  };

  return { user, isAuthenticated, login };
}
