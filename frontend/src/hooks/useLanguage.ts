import { useTranslation } from 'react-i18next';

/**
 * Custom hook for language management
 * Provides easy access to translation function and language switching
 * Persists language preference to localStorage
 */
export const useLanguage = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string): void => {
    i18n.changeLanguage(lng);
    // Persist language choice to localStorage
    localStorage.setItem('language', lng);
  };

  const getCurrentLanguage = (): string => {
    return i18n.language;
  };

  const getAvailableLanguages = (): Array<{ code: string; label: string }> => {
    return [
      { code: 'en', label: t('languageSwitcher.english') },
      { code: 'es', label: t('languageSwitcher.spanish') },
      { code: 'fr', label: t('languageSwitcher.french') },
    ];
  };

  return {
    t,
    changeLanguage,
    currentLanguage: getCurrentLanguage(),
    availableLanguages: getAvailableLanguages(),
  };
};
