<script setup lang="ts">
import { useAuth } from "@/auth/useAuth";
import ButtonSecondary from "@/components/button/ButtonSecondary.vue";
import Input from "@/components/input/Input.vue";
import { useLocale } from "@/composables/useLocale";
import { ref } from "vue";

const phoneNumer = ref<string>("");
const name = ref<string>("");
const loading = ref<boolean>(false);

const { t } = useLocale();
const auth = useAuth();

// Phone number validation and transformation handler
const handlePhoneInput = (event: InputEvent) => {
  const value = (event.target as HTMLInputElement).value;
  if (value === undefined || value === "") {
    phoneNumer.value = value;
    return;
  }

  let cleaned = value;

  // Convert +84 to 0
  if (cleaned.startsWith("+84")) {
    cleaned = "0" + cleaned.substring(3);
  }

  // Remove all non-numeric characters
  cleaned = cleaned.replace(/\D/g, "");

  // Limit to 10 characters
  cleaned = cleaned.substring(0, 10);

  phoneNumer.value = cleaned;
};

const handleNameInput = (event: InputEvent) => {
  const value = (event.target as HTMLInputElement).value;
  name.value = value;
};

const handleLogin = async () => {
  try {
    await auth.login({ name: name.value, phoneNumber: phoneNumer.value });
  } catch (error) {
    console.error("error: ", error);
  }
};
</script>

<template>
  <div class="flex flex-col justify-center items-center py-8 gap-10">
    <strong class="text-gradient text-2xl">{{ t("auth.login") }}</strong>
    <div class="flex flex-col gap-4 w-full max-w-sm">
      <div>
        <Input
          type="text"
          :label="t('auth.name')"
          :placeholder="t('auth.fullName')"
          :model-value="name"
          @update:model-value="handleNameInput"
          :disabled="loading"
        />
      </div>
      <div>
        <Input
          type="text"
          :label="t('auth.phoneNumber')"
          :placeholder="t('auth.yourPhoneNumber')"
          :model-value="phoneNumer"
          @update:model-value="handlePhoneInput"
          :disabled="loading"
        />
      </div>
    </div>
    <ButtonSecondary
      type="button"
      class="uppercase w-full max-w-sm"
      @click="handleLogin"
      :disabled="loading"
    />
  </div>
</template>
