<script setup lang="ts">
import { useLocale } from "@/composables/useLocale";
import { useAttrs, type ButtonHTMLAttributes } from "vue";

const attrs = useAttrs() as ButtonHTMLAttributes;
const { t } = useLocale();
</script>

<template>
  <button v-bind="attrs" class="btn btn-secondary">
    <slot>{{ t("common.submit") }}</slot>
  </button>
</template>
