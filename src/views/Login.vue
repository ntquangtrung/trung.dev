<script setup lang="ts">
import ButtonSecondary from "@/components/button/ButtonSecondary.vue";
import Input from "@/components/input/Input.vue";
import { useLocale } from "@/composables/useLocale";
import { ref } from "vue";

const phoneNumer = ref<string>("");
const name = ref<string>("");
const { t } = useLocale();
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
          v-model="name"
        />
      </div>
      <div>
        <Input
          type="number"
          :label="t('auth.phoneNumber')"
          :placeholder="t('auth.yourPhoneNumber')"
          v-model="phoneNumer"
        />
      </div>
    </div>
    <ButtonSecondary class="uppercase w-full max-w-sm" />
  </div>
</template>
