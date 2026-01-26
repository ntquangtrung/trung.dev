import type { FileEntryDto } from "@/api/dto/get-all-files.dto";
import seaweedRepository from "@/api/repositories/seaweed.repository";
import { compareDesc } from "date-fns";
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
        const currentDateFormatted = current.createdTime.formattedDate;
        if (accumulator[currentDateFormatted] === undefined) {
          return { ...accumulator, [currentDateFormatted]: [current] };
        }
        return {
          ...accumulator,
          [currentDateFormatted]: [
            ...(accumulator[currentDateFormatted] as ReadonlyArray<FileEntryDto>),
            current,
          ].sort((a, b) => sortDateDescending(a.createdTime.date, b.createdTime.date)),
        };
      },
      {} as Record<string, ReadonlyArray<FileEntryDto>>
    );
  });

  const sortDateDescending = (a: Date, b: Date) => compareDesc(a, b);

  const sortedDescDatas = computed(() =>
    Object.entries(groupedDatasBasedOnDateCreated.value).sort(([a], [b]) =>
      sortDateDescending(new Date(a), new Date(b))
    )
  );

  onMounted(() => {
    onLoadMore();
  });

  return {
    shouldLoadMore,
    onLoadMore,
    datas: sortedDescDatas,
  };
}
