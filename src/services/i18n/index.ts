import en from "@/locales/en.json";
import viVn from "@/locales/vi-vn.json";
import type { I18n, I18nOptions } from "vue-i18n";
import { createI18n } from "vue-i18n";

// Supported locales
export const SUPPORTED_LOCALES = ["vi-vn", "en"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

// Message schema type inferred from the JSON files
type MessageSchema = typeof en;

// Typed I18n instance
export type TypedI18n = I18n<
  { "vi-vn": MessageSchema; en: MessageSchema },
  Record<string, unknown>,
  Record<string, unknown>,
  SupportedLocale,
  false
>;

/**
 * I18nManager singleton class handles all internationalization logic
 */
class I18nManager {
  private static instance: I18nManager | null = null;
  private static readonly DEFAULT_LOCALE: SupportedLocale = "vi-vn";
  private static readonly FALLBACK_LOCALE: SupportedLocale = "en";

  private i18n: TypedI18n | null = null;

  private constructor() {}

  static getInstance(): I18nManager {
    if (I18nManager.instance === null) {
      I18nManager.instance = new I18nManager();
    }
    return I18nManager.instance;
  }

  /**
   * Initialize and return the i18n instance for Vue app registration
   */
  init(): TypedI18n {
    if (this.i18n !== null) {
      return this.i18n;
    }

    const locale = this.detectBrowserLocale();

    const options = {
      legacy: false,
      locale,
      fallbackLocale: I18nManager.FALLBACK_LOCALE,
      messages: {
        "vi-vn": viVn,
        en,
      },
      globalInjection: true,
      missingWarn: false,
      fallbackWarn: false,
    } satisfies I18nOptions;

    this.i18n = createI18n(options);
    document.documentElement.setAttribute("lang", locale);

    return this.i18n;
  }

  /**
   * Get the current locale
   */
  get locale(): SupportedLocale {
    if (this.i18n === null) {
      return this.detectBrowserLocale();
    }
    return this.i18n.global.locale.value as SupportedLocale;
  }

  /**
   * Set the locale
   */
  set locale(newLocale: SupportedLocale) {
    this.setLocale(newLocale);
  }

  /**
   * Change the current locale
   */
  setLocale(locale: SupportedLocale): void {
    if (this.i18n === null) {
      console.warn("I18nManager not initialized. Call init() first.");
      return;
    }

    if (this.i18n.global.locale.value === locale) {
      return;
    }

    this.i18n.global.locale.value = locale;
    document.documentElement.setAttribute("lang", locale);
  }

  /**
   * Get the i18n instance (must call init() first)
   */
  getI18n(): TypedI18n {
    if (this.i18n === null) {
      throw new Error("I18nManager not initialized. Call init() first.");
    }
    return this.i18n;
  }

  private detectBrowserLocale(): SupportedLocale {
    const browserLang = navigator.language.toLowerCase();

    if (browserLang.startsWith("vi")) {
      return "vi-vn";
    }

    if (browserLang.startsWith("en")) {
      return "en";
    }

    return I18nManager.DEFAULT_LOCALE;
  }
}

export const i18nManager = I18nManager.getInstance();
