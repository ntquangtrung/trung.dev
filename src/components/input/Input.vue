<script setup lang="ts">
import { useAttrs, type InputHTMLAttributes } from "vue";
interface Props {
  label: string;
}

const props = withDefaults(defineProps<Props>(), {
  label: "",
});
const attrs = useAttrs() as InputHTMLAttributes;
const model = defineModel<string>({ required: true });
</script>

<template>
  <label class="capitalize text-gradient">{{ props.label }}</label>
  <input v-bind="attrs" class="input" v-model="model" />
</template>
