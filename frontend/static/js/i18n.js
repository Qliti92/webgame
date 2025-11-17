/**
 * i18n (Internationalization) System
 * Supports: Vietnamese (vi), English (en), Chinese (zh)
 *
 * Usage:
 * - Add data-i18n="key.path" attribute to HTML elements
 * - Call t('key.path') in JavaScript to get translation
 * - Call changeLanguage('en') to switch language
 */

class I18n {
    constructor() {
        this.currentLang = this.getStoredLanguage();
        this.translations = {};
        this.defaultLang = 'vi';
        this.supportedLanguages = ['vi', 'en', 'zh'];
        this.isAdmin = window.location.pathname.startsWith('/admin');
    }

    /**
     * Get stored language from localStorage
     */
    getStoredLanguage() {
        // Admin always uses Vietnamese
        if (window.location.pathname.startsWith('/admin')) {
            return 'vi';
        }

        const stored = localStorage.getItem('language');
        return stored && ['vi', 'en', 'zh'].includes(stored) ? stored : 'vi';
    }

    /**
     * Load translation file for specified language
     */
    async loadLanguage(lang) {
        // Admin always uses Vietnamese
        if (this.isAdmin) {
            lang = 'vi';
        }

        if (!this.supportedLanguages.includes(lang)) {
            console.warn(`Language "${lang}" not supported. Falling back to ${this.defaultLang}`);
            lang = this.defaultLang;
        }

        try {
            const response = await fetch(`/static/locales/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load language file: ${lang}.json`);
            }
            this.translations = await response.json();
            this.currentLang = lang;

            // Don't store language preference for admin pages
            if (!this.isAdmin) {
                localStorage.setItem('language', lang);
            }

            return true;
        } catch (error) {
            console.error('Error loading language file:', error);

            // Try fallback to default language
            if (lang !== this.defaultLang) {
                console.log(`Falling back to ${this.defaultLang}...`);
                return this.loadLanguage(this.defaultLang);
            }

            return false;
        }
    }

    /**
     * Get translation by key path (e.g., "auth.login")
     */
    t(key, defaultValue = '') {
        const keys = key.split('.');
        let value = this.translations;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`Translation key not found: "${key}" for language "${this.currentLang}"`);
                return defaultValue || key;
            }
        }

        return value || defaultValue || key;
    }

    /**
     * Apply translations to all elements with data-i18n attribute
     */
    applyTranslations() {
        const elements = document.querySelectorAll('[data-i18n]');

        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translatedText = this.t(key);

            // Check if element has data-i18n-attr for attribute translation
            const attr = element.getAttribute('data-i18n-attr');
            if (attr) {
                element.setAttribute(attr, translatedText);
            } else {
                // Default: update textContent
                element.textContent = translatedText;
            }
        });
    }

    /**
     * Change language and reload translations
     */
    async changeLanguage(lang) {
        console.log('🔄 changeLanguage called with:', lang);
        console.log('🔄 Current language:', this.currentLang);
        console.log('🔄 Is admin:', this.isAdmin);

        // Prevent language change in admin
        if (this.isAdmin) {
            console.warn('Language cannot be changed in admin panel');
            return false;
        }

        if (lang === this.currentLang) {
            console.log('ℹ️ Already using this language');
            return true; // Already using this language
        }

        console.log('📥 Loading language:', lang);
        const success = await this.loadLanguage(lang);
        console.log('📥 Load result:', success);

        if (success) {
            console.log('✨ Applying translations...');
            this.applyTranslations();
            this.updateLanguageDisplay(lang);

            // Dispatch custom event for other scripts to react
            window.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: lang }
            }));

            console.log('✅ Language change complete!');
            return true;
        }

        console.error('❌ Language change failed');
        return false;
    }

    /**
     * Update language display in UI (flags, labels, etc.)
     */
    updateLanguageDisplay(lang) {
        const langLabels = {
            'vi': 'VI',
            'en': 'EN',
            'zh': '中文'
        };

        const currentLangElement = document.getElementById('currentLanguage');
        if (currentLangElement) {
            currentLangElement.textContent = langLabels[lang] || lang.toUpperCase();
        }

        // Update HTML lang attribute
        document.documentElement.lang = lang;
    }

    /**
     * Initialize i18n system
     */
    async init() {
        const success = await this.loadLanguage(this.currentLang);
        if (success) {
            this.applyTranslations();
            this.updateLanguageDisplay(this.currentLang);
        }
        return success;
    }

    /**
     * Get current language code
     */
    getCurrentLanguage() {
        return this.currentLang;
    }

    /**
     * Get all supported languages
     */
    getSupportedLanguages() {
        return this.supportedLanguages;
    }
}

// Create global instance and expose to window
const i18n = new I18n();
window.i18n = i18n;

// Helper function for easy access
function t(key, defaultValue = '') {
    return i18n.t(key, defaultValue);
}
window.t = t;

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        i18n.init();
    });
} else {
    i18n.init();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { i18n, t };
}
