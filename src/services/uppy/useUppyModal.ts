import { ref } from "vue";

const open = ref(false);

export const useUppyModal = () => {
  const toggleModal = (toggle: boolean) => {
    open.value = toggle;
  };

  return { open, toggleModal };
};
