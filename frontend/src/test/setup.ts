import '@testing-library/jest-dom'
import i18n from '../i18n/config'

// Initialize i18n for tests
i18n.init({
  lng: 'en',
  fallbackLng: 'en',
  ns: ['translation'],
  defaultNS: 'translation',
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false,
  },
}).catch(() => {
  // i18n might already be initialized, which is fine
})

// Disable React act warnings for tests
// These warnings are caused by async state updates in hooks that are not critical for test functionality
const originalError = console.error;
beforeEach(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('An update to') &&
      args[0].includes('inside a test was not wrapped in act')
    ) {
      return;
    }
    // Suppress i18next initialization warning in tests
    if (
      typeof args[0] === 'string' &&
      args[0].includes('i18next') &&
      args[0].includes('initReactI18next')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterEach(() => {
  console.error = originalError;
});
