<script setup lang="ts">
import styles from "./styles.module.css";

interface Props {
  size?: "sm" | "md" | "lg";
}

withDefaults(defineProps<Props>(), {
  size: "md",
});
</script>

<template>
  <div :class="[styles.spinnerContainer, styles[size]]">
    <div :class="[styles.spinner]"></div>
  </div>
</template>
