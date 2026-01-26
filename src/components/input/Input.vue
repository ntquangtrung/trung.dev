<script setup lang="ts">
import { useAttrs, type InputHTMLAttributes } from "vue";
interface Props {
  label?: string;
  modelValue: string | boolean | undefined;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  label: "",
  disabled: false,
});

const emit = defineEmits<{
  "update:modelValue": [event: InputEvent];
}>();
const attrs = useAttrs() as InputHTMLAttributes;
</script>

<template>
  <label v-if="props.label" class="capitalize text-gradient">{{ props.label }}</label>
  <input
    v-bind="attrs"
    class="input"
    :value="props.modelValue"
    :disabled="props.disabled"
    @input="emit('update:modelValue', $event)"
  />
</template>
