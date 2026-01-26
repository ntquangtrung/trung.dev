<script setup lang="ts" generic="TData">
import Spinner from "@/components/spinner/Spinner.vue";
import { useInfiniteScroll, useScroll } from "@vueuse/core";
import { type UnwrapNestedRefs } from "vue";

interface Props {
  data?: Array<TData>;
  loadMore: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  loadMore: [state: UnwrapNestedRefs<ReturnType<typeof useScroll>>];
}>();

const handleLoadMore = (state: UnwrapNestedRefs<ReturnType<typeof useScroll>>) => {
  emit("loadMore", state);
};

const { isLoading } = useInfiniteScroll(window, handleLoadMore, {
  distance: 100,
  canLoadMore: () => props.loadMore,
});
</script>

<template>
  <ul>
    <slot>
      <li v-for="(item, index) in props.data" :key="index">
        {{ item }}
      </li>
    </slot>

    <li v-if="isLoading">
      <Spinner />
    </li>
  </ul>
</template>
