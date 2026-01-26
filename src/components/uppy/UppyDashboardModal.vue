<script setup lang="ts">
import DashboardModal from "@uppy/vue/dashboard-modal";

import { createTusUppyService } from "@/services/uppy/tus";
import { useUppyModal } from "@/services/uppy/useUppyModal";
import "@uppy/core/css/style.min.css";
import "@uppy/dashboard/css/style.min.css";
import { onUnmounted } from "vue";

const { open, toggleModal } = useUppyModal();

const service = createTusUppyService({}, {}, undefined);

onUnmounted(() => {
  service.destroy();
});
</script>

<template>
  <DashboardModal :uppy="service.uppy" :open="open" @close="toggleModal(false)" />
</template>
