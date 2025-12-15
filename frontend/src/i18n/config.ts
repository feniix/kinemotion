import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslation from './locales/en/translation.json';
import esTranslation from './locales/es/translation.json';
import frTranslation from './locales/fr/translation.json';

// Define resource structure for TypeScript type safety
const resources = {
  en: { translation: enTranslation },
  es: { translation: esTranslation },
  fr: { translation: frTranslation },
} as const;

// Initialize i18next
i18n
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    resources,

    // Default language - check localStorage first, then default to 'en'
    lng: localStorage.getItem('language') || 'en',

    // Fallback language
    fallbackLng: 'en',

    // Namespace (default is 'translation')
    ns: ['translation'],
    defaultNS: 'translation',

    // Interpolation settings
    interpolation: {
      escapeValue: false, // React already escapes XSS vulnerabilities
    },

    // Debug mode (only in development)
    debug: import.meta.env.MODE === 'development',

    // React options
    react: {
      useSuspense: false, // Avoid Suspense boundaries during initialization
    },
  });

export default i18n;
