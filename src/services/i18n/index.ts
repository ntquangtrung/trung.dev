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

  private static readonly LOCALE_VERSION = "1.0.0";
  private static readonly STORAGE_KEY = "app_locale";
  private static readonly VERSION_KEY = "app_locale_version";
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

    const locale = this.getInitialLocale();

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
      return this.getStoredLocale() ?? I18nManager.DEFAULT_LOCALE;
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
    this.persistLocale(locale);
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

  private getStoredLocale(): SupportedLocale | null {
    try {
      const storedVersion = localStorage.getItem(I18nManager.VERSION_KEY);

      if (storedVersion !== I18nManager.LOCALE_VERSION) {
        localStorage.removeItem(I18nManager.STORAGE_KEY);
        localStorage.setItem(I18nManager.VERSION_KEY, I18nManager.LOCALE_VERSION);
        return null;
      }

      const storedLocale = localStorage.getItem(I18nManager.STORAGE_KEY);

      if (
        storedLocale !== null &&
        storedLocale.length > 0 &&
        SUPPORTED_LOCALES.includes(storedLocale as SupportedLocale)
      ) {
        return storedLocale as SupportedLocale;
      }
    } catch (error) {
      console.error("Failed to get stored locale:", error);
    }

    return null;
  }

  private persistLocale(locale: SupportedLocale): void {
    try {
      localStorage.setItem(I18nManager.STORAGE_KEY, locale);
      localStorage.setItem(I18nManager.VERSION_KEY, I18nManager.LOCALE_VERSION);
    } catch (error) {
      console.error("Failed to persist locale:", error);
    }
  }

  private getInitialLocale(): SupportedLocale {
    const storedLocale = this.getStoredLocale();

    if (storedLocale !== null) {
      return storedLocale;
    }

    const browserLocale = this.detectBrowserLocale();
    this.persistLocale(browserLocale);

    return browserLocale;
  }
}

export const i18nManager = I18nManager.getInstance();
