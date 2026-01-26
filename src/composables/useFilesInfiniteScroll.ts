import type { FileEntryDto } from "@/api/dto/get-all-files.dto";
import seaweedRepository from "@/api/repositories/seaweed.repository";
import { computed, nextTick, onMounted, ref } from "vue";

export function useFilesInfiniteScroll() {
  const shouldLoadMore = ref(false);
  const datas = ref<ReadonlyArray<FileEntryDto>>([]);
  const limit = ref(5);
  const lastFileName = ref("");

  const onLoadMore = async () => {
    const response = await seaweedRepository.getAllFiles({
      limit: limit.value,
      lastFileName: lastFileName.value,
    });
    datas.value = [...datas.value, ...response.files];
    await nextTick();
    if (response.hasMore) {
      limit.value += 5;
      lastFileName.value = response.lastFileName;
    }
    shouldLoadMore.value = response.hasMore;
  };

  const groupedDatasBasedOnDateCreated = computed(() => {
    return datas.value.reduce(
      (accumulator, current) => {
        const currentDateFormatted = new Date(current.createdTime).toLocaleDateString();
        if (accumulator[currentDateFormatted] === undefined) {
          return { ...accumulator, [currentDateFormatted]: [current] };
        }
        return {
          ...accumulator,
          [currentDateFormatted]: [
            ...(accumulator[currentDateFormatted] as ReadonlyArray<FileEntryDto>),
            current,
          ],
        };
      },
      {} as Record<string, ReadonlyArray<FileEntryDto>>
    );
  });

  onMounted(() => {
    onLoadMore();
  });

  return {
    shouldLoadMore,
    onLoadMore,
    datas: groupedDatasBasedOnDateCreated,
  };
}
