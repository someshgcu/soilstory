/**
 * SoilStory LocalStorage Management
 * Handles all data persistence operations in the browser
 */

class SoilStorage {
    constructor() {
        this.storageKey = 'soilstory_data';
        this.analysesKey = 'soilstory_analyses';
        this.settingsKey = 'soilstory_settings';
        this.maxStorageSize = 50; // Maximum number of analyses to store
    }

    /**
     * Check if localStorage is available and has space
     */
    isStorageAvailable() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }

    /**
     * Get storage usage information
     */
    getStorageInfo() {
        if (!this.isStorageAvailable()) {
            return { available: false, usage: 0, limit: 0 };
        }

        let totalSize = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                totalSize += localStorage[key].length + key.length;
            }
        }

        return {
            available: true,
            usage: totalSize,
            limit: 5 * 1024 * 1024, // 5MB typical limit
            percentage: (totalSize / (5 * 1024 * 1024)) * 100
        };
    }

    /**
     * Save a new soil analysis
     */
    saveAnalysis(analysis) {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            // Generate unique ID if not provided
            if (!analysis.id) {
                analysis.id = this.generateId();
            }

            // Add timestamp if not provided
            if (!analysis.timestamp) {
                analysis.timestamp = new Date().toISOString();
            }

            // Get existing analyses
            const analyses = this.getAnalyses();
            
            // Add new analysis to the beginning
            analyses.unshift(analysis);

            // Limit storage size
            if (analyses.length > this.maxStorageSize) {
                analyses.splice(this.maxStorageSize);
            }

            // Save back to localStorage
            localStorage.setItem(this.analysesKey, JSON.stringify(analyses));

            // Update storage info
            this.updateStorageInfo();

            return analysis.id;
        } catch (error) {
            console.error('Error saving analysis:', error);
            throw new Error('Failed to save analysis');
        }
    }

    /**
     * Get all analyses
     */
    getAnalyses() {
        if (!this.isStorageAvailable()) {
            return [];
        }

        try {
            const data = localStorage.getItem(this.analysesKey);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('Error reading analyses:', error);
            return [];
        }
    }

    /**
     * Get analysis by ID
     */
    getAnalysis(id) {
        const analyses = this.getAnalyses();
        return analyses.find(analysis => analysis.id === id);
    }

    /**
     * Update an existing analysis
     */
    updateAnalysis(id, updates) {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            const analyses = this.getAnalyses();
            const index = analyses.findIndex(analysis => analysis.id === id);
            
            if (index === -1) {
                throw new Error('Analysis not found');
            }

            // Update the analysis
            analyses[index] = { ...analyses[index], ...updates };
            
            // Save back to localStorage
            localStorage.setItem(this.analysesKey, JSON.stringify(analyses));

            return true;
        } catch (error) {
            console.error('Error updating analysis:', error);
            throw new Error('Failed to update analysis');
        }
    }

    /**
     * Delete an analysis
     */
    deleteAnalysis(id) {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            const analyses = this.getAnalyses();
            const filtered = analyses.filter(analysis => analysis.id !== id);
            
            localStorage.setItem(this.analysesKey, JSON.stringify(filtered));
            
            return true;
        } catch (error) {
            console.error('Error deleting analysis:', error);
            throw new Error('Failed to delete analysis');
        }
    }

    /**
     * Clear all analyses
     */
    clearAnalyses() {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            localStorage.removeItem(this.analysesKey);
            return true;
        } catch (error) {
            console.error('Error clearing analyses:', error);
            throw new Error('Failed to clear analyses');
        }
    }

    /**
     * Search analyses by text
     */
    searchAnalyses(query) {
        const analyses = this.getAnalyses();
        if (!query || query.trim() === '') {
            return analyses;
        }

        const searchTerm = query.toLowerCase().trim();
        return analyses.filter(analysis => {
            // Search in story text
            if (analysis.story && analysis.story.toLowerCase().includes(searchTerm)) {
                return true;
            }
            
            // Search in location
            if (analysis.location && 
                (analysis.location.lat?.toString().includes(searchTerm) || 
                 analysis.location.lon?.toString().includes(searchTerm))) {
                return true;
            }
            
            // Search in timestamp
            if (analysis.timestamp && analysis.timestamp.toLowerCase().includes(searchTerm)) {
                return true;
            }
            
            return false;
        });
    }

    /**
     * Get analyses with pagination
     */
    getAnalysesPaginated(page = 1, pageSize = 12) {
        const analyses = this.getAnalyses();
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        
        return {
            data: analyses.slice(startIndex, endIndex),
            total: analyses.length,
            page: page,
            pageSize: pageSize,
            totalPages: Math.ceil(analyses.length / pageSize)
        };
    }

    /**
     * Save user settings
     */
    saveSettings(settings) {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            localStorage.setItem(this.settingsKey, JSON.stringify(settings));
            return true;
        } catch (error) {
            console.error('Error saving settings:', error);
            throw new Error('Failed to save settings');
        }
    }

    /**
     * Get user settings
     */
    getSettings() {
        if (!this.isStorageAvailable()) {
            return this.getDefaultSettings();
        }

        try {
            const data = localStorage.getItem(this.settingsKey);
            const saved = data ? JSON.parse(data) : {};
            return { ...this.getDefaultSettings(), ...saved };
        } catch (error) {
            console.error('Error reading settings:', error);
            return this.getDefaultSettings();
        }
    }

    /**
     * Get default settings
     */
    getDefaultSettings() {
        return {
            useLocation: true,
            autoSave: true,
            theme: 'light',
            language: 'en',
            notifications: true
        };
    }

    /**
     * Export all data as JSON
     */
    exportData() {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            const data = {
                analyses: this.getAnalyses(),
                settings: this.getSettings(),
                exportDate: new Date().toISOString(),
                version: '1.0.0'
            };

            return JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('Error exporting data:', error);
            throw new Error('Failed to export data');
        }
    }

    /**
     * Import data from JSON
     */
    importData(jsonData) {
        if (!this.isStorageAvailable()) {
            throw new Error('LocalStorage is not available');
        }

        try {
            const data = JSON.parse(jsonData);
            
            if (data.analyses && Array.isArray(data.analyses)) {
                localStorage.setItem(this.analysesKey, JSON.stringify(data.analyses));
            }
            
            if (data.settings && typeof data.settings === 'object') {
                localStorage.setItem(this.settingsKey, JSON.stringify(data.settings));
            }
            
            return true;
        } catch (error) {
            console.error('Error importing data:', error);
            throw new Error('Failed to import data');
        }
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'analysis_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Update storage info
     */
    updateStorageInfo() {
        const info = this.getStorageInfo();
        
        // Show warning if storage is getting full
        if (info.percentage > 80) {
            console.warn('LocalStorage is getting full:', info.percentage.toFixed(1) + '%');
        }
        
        return info;
    }

    /**
     * Get storage statistics
     */
    getStorageStats() {
        const analyses = this.getAnalyses();
        const info = this.getStorageInfo();
        
        return {
            totalAnalyses: analyses.length,
            storageUsage: info.usage,
            storageLimit: info.limit,
            storagePercentage: info.percentage,
            oldestAnalysis: analyses.length > 0 ? analyses[analyses.length - 1].timestamp : null,
            newestAnalysis: analyses.length > 0 ? analyses[0].timestamp : null
        };
    }
}

// Create global instance
window.soilStorage = new SoilStorage();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SoilStorage;
}
