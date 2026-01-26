import type { SupportedLocale } from "@/services/i18n";
import { i18nManager } from "@/services/i18n";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

export function useLocale() {
  const { locale, t } = useI18n();

  const currentLocale = computed<SupportedLocale>(() => locale.value as SupportedLocale);

  const setLocale = (newLocale: SupportedLocale) => {
    i18nManager.setLocale(newLocale);
  };

  return {
    locale: currentLocale,
    setLocale,
    t,
  };
}
