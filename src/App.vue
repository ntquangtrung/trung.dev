<script setup lang="ts">
import Footer from "@/components/footer/Footer.vue";
import Header from "@/components/header/Header.vue";
import { RouterView } from "vue-router";
</script>

<template>
  <Header />
  <section class="pt-(--header-height) px-4 min-h-screen">
    <RouterView />
  </section>

  <Footer />
</template>
