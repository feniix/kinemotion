import { useLanguage } from '../hooks/useLanguage';
import './LanguageSwitcher.css';

/**
 * Language Switcher Component
 * Allows users to switch between available languages (English, Spanish, French)
 * Persists language preference to localStorage for persistence across sessions
 */
export const LanguageSwitcher = () => {
  const { currentLanguage, availableLanguages, changeLanguage } = useLanguage();

  return (
    <div className="language-switcher">
      <select
        value={currentLanguage}
        onChange={(e) => changeLanguage(e.target.value)}
        className="language-select"
        aria-label="Select language"
        title="Change application language"
      >
        {availableLanguages.map(({ code, label }) => (
          <option key={code} value={code}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSwitcher;
