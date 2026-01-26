<script setup lang="ts">
import { useAttrs, type ButtonHTMLAttributes } from "vue";

const attrs = useAttrs() as ButtonHTMLAttributes;
</script>

<template>
  <button v-bind="attrs" class="btn btn-secondary">
    <slot>submit</slot>
  </button>
</template>
