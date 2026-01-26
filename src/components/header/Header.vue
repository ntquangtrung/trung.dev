<script setup lang="ts">
import { useAuth } from "@/auth/useAuth";
import { routes } from "@/router";
import { useUppyModal } from "@/services/uppy/useUppyModal";
import ButtonPrimary from "../button/ButtonPrimary.vue";
import styles from "./styles.module.css";

const { isAuthenticated } = useAuth();
const { toggleModal, open } = useUppyModal();
</script>

<template>
  <header :class="[styles.headerContainer]">
    <div class="flex-1 flex justify-between px-4">
      <RouterLink :to="routes.home.path">
        <strong class="text-gradient text-3xl font-pixeboy leading-[unset] select-none"
          >Your App Dashboard</strong
        >
      </RouterLink>
      <ButtonPrimary
        v-if="isAuthenticated"
        class="capitalize flex-0 whitespace-nowrap"
        @click="toggleModal(!open)"
        type="button"
      />
    </div>
  </header>
</template>
