<script setup lang="ts">
import { faHeart } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import styles from "./styles.module.css";
</script>

<template>
  <footer :class="[styles.footerContainer]">
    <strong class="text-gradient text-2xl font-pixeboy leading-[unset] select-none"
      >Made by Trung</strong
    >
    <small><FontAwesomeIcon :icon="faHeart" /> trung.dev</small>
  </footer>
</template>
