<script setup lang="ts">
import { useLocale } from "@/composables/useLocale";
import { useAttrs, type ButtonHTMLAttributes } from "vue";

interface Props {
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

const attrs = useAttrs() as ButtonHTMLAttributes;
const { t } = useLocale();
</script>

<template>
  <button v-bind="attrs" class="btn btn-secondary" :disabled="props.disabled">
    <slot>{{ t("common.submit") }}</slot>
  </button>
</template>
