/**
 * SoilStory API Client
 * Handles all communication with the backend Flask server
 */

class SoilAPI {
    constructor() {
        this.baseURL = window.location.origin; // Automatically detect the current domain
        this.endpoints = {
            analyze: '/api/analyze',
            video: '/api/video',
            history: '/api/history',
            health: '/health'
        };
        this.timeout = 30000; // 30 seconds timeout
    }

    /**
     * Make HTTP request with error handling
     */
    async makeRequest(url, options = {}) {
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        try {
            // Add authentication header if available
            const token = this.getAuthToken();
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(url, config);
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Try to parse JSON response
            try {
                const data = await response.json();
                return { success: true, data, status: response.status };
            } catch (parseError) {
                // If not JSON, return text
                const text = await response.text();
                return { success: true, data: text, status: response.status };
            }

        } catch (error) {
            console.error('API request failed:', error);
            return {
                success: false,
                error: error.message,
                status: 0
            };
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        // For local storage version, return a simple token
        return 'local-auth';
    }

    /**
     * Check if backend is available
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.health}`);
            return response.ok;
        } catch (error) {
            console.warn('Backend health check failed:', error);
            return false;
        }
    }

    /**
     * Analyze soil image
     */
    async analyzeSoil(imageFile, location = null) {
        try {
            // Check if backend is available
            const isHealthy = await this.checkHealth();
            if (!isHealthy) {
                // Fallback to demo mode
                return this.getDemoAnalysis(imageFile, location);
            }

            // Prepare form data
            const formData = new FormData();
            formData.append('photo', imageFile);
            
            if (location && location.lat && location.lon) {
                formData.append('lat', location.lat);
                formData.append('lon', location.lon);
            }

            // Make request
            const response = await fetch(`${this.baseURL}${this.endpoints.analyze}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            return { success: true, data: result };

        } catch (error) {
            console.error('Soil analysis failed:', error);
            
            // Fallback to demo mode
            return this.getDemoAnalysis(imageFile, location);
        }
    }

    /**
     * Generate video from story
     */
    async generateVideo(analysisId, storyText, imagePath) {
        try {
            // Check if backend is available
            const isHealthy = await this.checkHealth();
            if (!isHealthy) {
                // Fallback to demo mode
                return this.getDemoVideo(analysisId, storyText);
            }

            const response = await this.makeRequest(`${this.baseURL}${this.endpoints.video}`, {
                method: 'POST',
                body: JSON.stringify({
                    analysisId: analysisId
                })
            });

            if (!response.success) {
                throw new Error(response.error || 'Video generation failed');
            }

            return response;

        } catch (error) {
            console.error('Video generation failed:', error);
            
            // Fallback to demo mode
            return this.getDemoVideo(analysisId, storyText);
        }
    }

    /**
     * Get analysis history
     */
    async getHistory() {
        try {
            // Check if backend is available
            const isHealthy = await this.checkHealth();
            if (!isHealthy) {
                // Return empty history for demo mode
                return { success: true, data: { items: [] } };
            }

            const response = await this.makeRequest(`${this.baseURL}${this.endpoints.history}`);
            return response;

        } catch (error) {
            console.error('Failed to fetch history:', error);
            return { success: true, data: { items: [] } };
        }
    }

    /**
     * Demo analysis for offline/demo mode
     */
    getDemoAnalysis(imageFile, location) {
        // Simulate processing delay
        return new Promise((resolve) => {
            setTimeout(() => {
                const demoData = {
                    id: 'demo_' + Date.now(),
                    imagePath: URL.createObjectURL(imageFile),
                    analysis: {
                        pH: this.getRandomValue(5.5, 8.0, 1),
                        OM: this.getRandomValue(1.0, 5.0, 1),
                        P: this.getRandomValue(10, 50, 0),
                        EC: this.getRandomValue(0.5, 2.5, 1),
                        moisture: this.getRandomValue(15, 35, 0)
                    },
                    weather: location ? {
                        tempC: this.getRandomValue(15, 30, 0),
                        humidity: this.getRandomValue(40, 80, 0),
                        weather: this.getRandomWeather(),
                        windSpeed: this.getRandomValue(5, 20, 1)
                    } : null,
                    story: this.generateDemoStory(location),
                    timestamp: new Date().toISOString(),
                    isDemo: true
                };

                resolve({ success: true, data: demoData });
            }, 2000); // 2 second delay to simulate processing
        });
    }

    /**
     * Demo video generation
     */
    getDemoVideo(analysisId, storyText) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const demoVideo = {
                    videoPath: '/static/demo-video.mp4', // Placeholder
                    videoUrl: '/static/demo-video.mp4',
                    isDemo: true
                };

                resolve({ success: true, data: demoVideo });
            }, 3000); // 3 second delay to simulate video generation
        });
    }

    /**
     * Generate random value within range
     */
    getRandomValue(min, max, decimals = 0) {
        const value = Math.random() * (max - min) + min;
        return decimals === 0 ? Math.round(value) : parseFloat(value.toFixed(decimals));
    }

    /**
     * Get random weather condition
     */
    getRandomWeather() {
        const conditions = [
            'Partly cloudy', 'Sunny', 'Overcast', 'Light rain',
            'Clear skies', 'Misty', 'Light breeze', 'Calm'
        ];
        return conditions[Math.floor(Math.random() * conditions.length)];
    }

    /**
     * Generate demo story based on analysis
     */
    generateDemoStory(location) {
        const stories = [
            "Your soil shows excellent structure with balanced pH levels. The organic matter content suggests good fertility, making it ideal for most garden vegetables. Consider adding compost in the spring to maintain soil health.",
            "This soil sample indicates moderate fertility with room for improvement. The pH is slightly acidic, which is perfect for blueberries and rhododendrons. Adding lime can help balance the pH for other crops.",
            "Your soil demonstrates good drainage and moderate nutrient levels. The electrical conductivity suggests appropriate salt levels for healthy plant growth. Regular mulching will help maintain moisture retention.",
            "This soil has excellent potential for organic gardening. The organic matter content is promising, and the pH range supports a wide variety of plants. Consider crop rotation to optimize soil health."
        ];

        let story = stories[Math.floor(Math.random() * stories.length)];
        
        if (location) {
            story += ` Based on your location coordinates (${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}), this soil type is typical for your region and should support local native plants well.`;
        }

        return story;
    }

    /**
     * Upload image to backend (if available)
     */
    async uploadImage(imageFile) {
        try {
            const formData = new FormData();
            formData.append('photo', imageFile);

            const response = await fetch(`${this.baseURL}/api/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Image upload failed');
            }

            const result = await response.json();
            return { success: true, data: result };

        } catch (error) {
            console.error('Image upload failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get weather data for location
     */
    async getWeatherData(lat, lon) {
        try {
            // This would typically call a weather API
            // For demo purposes, return mock data
            return {
                tempC: this.getRandomValue(15, 30, 0),
                humidity: this.getRandomValue(40, 80, 0),
                pressure: this.getRandomValue(1000, 1020, 0),
                windSpeed: this.getRandomValue(5, 20, 1),
                weather: this.getRandomWeather(),
                rain1h: Math.random() > 0.7 ? this.getRandomValue(0.1, 5.0, 1) : 0
            };
        } catch (error) {
            console.error('Weather data fetch failed:', error);
            return null;
        }
    }

    /**
     * Export analysis data
     */
    exportAnalysisData(analysisId) {
        try {
            // Get analysis from storage
            const analysis = window.soilStorage.getAnalysis(analysisId);
            if (!analysis) {
                throw new Error('Analysis not found');
            }

            // Create export data
            const exportData = {
                analysis: analysis,
                exportDate: new Date().toISOString(),
                version: '1.0.0'
            };

            // Create and download file
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `soilstory_analysis_${analysisId}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            return { success: true };
        } catch (error) {
            console.error('Export failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get API status and capabilities
     */
    async getAPIStatus() {
        try {
            const healthCheck = await this.checkHealth();
            const storageInfo = window.soilStorage.getStorageInfo();
            
            return {
                backend: healthCheck,
                storage: storageInfo.available,
                storageUsage: storageInfo.percentage,
                demoMode: !healthCheck,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('Status check failed:', error);
            return {
                backend: false,
                storage: false,
                demoMode: true,
                timestamp: new Date().toISOString()
            };
        }
    }
}

// Create global instance
window.soilAPI = new SoilAPI();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SoilAPI;
}
