<script setup lang="ts">
import InfiniteScroll from "@/components/infinite-scroll/InfiniteScroll.vue";
import UppyDashboardModal from "@/components/uppy/UppyDashboardModal.vue";
import { useFilesInfiniteScroll } from "@/composables/useFilesInfiniteScroll";
import { isImage } from "@/utils/mime";
import mediumZoom, { type Zoom } from "medium-zoom";
import { nextTick, onMounted, watch } from "vue";

const { shouldLoadMore, onLoadMore, datas } = useFilesInfiniteScroll();

let zoom: Zoom | null = null;

onMounted(() => {
  zoom = mediumZoom(".zoomable", {
    margin: 24,
    background: "rgba(0, 0, 0, 0.8)",
    scrollOffset: 40,
  });
});

watch(datas, async () => {
  console.log("datas: ", datas);
  await nextTick(); // wait for DOM update
  zoom?.attach(".zoomable");
});
</script>

<template>
  <section class="py-6">
    <InfiniteScroll
      :should-load-more="shouldLoadMore"
      @load-more="onLoadMore"
      class="flex flex-col gap-6"
    >
      <li v-for="([date, files], index) in datas" :key="index">
        <strong class="text-orange block border-b">{{ date }}</strong>
        <ul class="grid grid-cols-3 gap-4 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 py-6">
          <li v-for="(file, fileIndex) in files" :key="fileIndex" class="h-40 md:h-48">
            <img
              v-if="isImage(file.type)"
              :src="file.fullPath"
              class="zoomable w-full h-full object-contain rounded-xl"
            />
            <video
              v-else
              controls
              preload="metadata"
              playsinline
              class="w-full h-full object-cover rounded-xl"
            >
              <source :src="file.fullPath" :type="file.type" />
              Your browser does not support the video tag.
            </video>
          </li>
        </ul>
      </li>
    </InfiniteScroll>
    <UppyDashboardModal />
  </section>
</template>
