// This is a simple client-side helper for displaying translated content
// The actual translation happens on the server

class LanguageUtils {
    constructor() {
        this.languageNames = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ko': 'Korean',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ar': 'Arabic'
        };
    }
    
    getLanguageName(code) {
        return this.languageNames[code] || code;
    }
}

const languageUtils = new LanguageUtils(); 