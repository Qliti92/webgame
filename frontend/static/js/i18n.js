/**
 * Simplified i18n stub - English only
 * All user-facing text is now in English
 * Django Admin remains in Vietnamese
 */

// Simple stub that returns the default value (English text)
function t(key, defaultValue = '') {
    return defaultValue || key;
}

// Expose to window
window.t = t;

// No-op functions for compatibility
window.i18n = {
    t: t,
    changeLanguage: function() { return false; },
    getCurrentLanguage: function() { return 'en'; },
    getSupportedLanguages: function() { return ['en']; },
    init: function() { return Promise.resolve(true); }
};

// No initialization needed
console.log('✅ i18n disabled - English only mode');
