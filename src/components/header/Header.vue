<script setup lang="ts">
import { RoutePaths } from "@/router";
import styles from "./styles.module.css";
</script>

<template>
  <header :class="[styles.headerContainer]">
    <div class="flex-1 flex justify-between px-4">
      <RouterLink :to="RoutePaths.HOME">
        <strong class="text-gradient text-3xl font-pixeboy leading-[unset] select-none"
          >Your App Dashboard</strong
        >
      </RouterLink>
      <button class="btn btn-primary capitalize flex-0">upload</button>
    </div>
  </header>
</template>
