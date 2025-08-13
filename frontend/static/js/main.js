/**
 * SoilStory Main Application Logic
 * Handles UI interactions, event listeners, and coordinates all components
 */

class SoilStoryApp {
    constructor() {
        this.currentAnalysis = null;
        this.isAnalyzing = false;
        this.isGeneratingVideo = false;
        this.currentPage = 'index'; // 'index' or 'history'
        
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.detectCurrentPage();
        this.setupEventListeners();
        this.loadInitialData();
        this.setupDragAndDrop();
        this.checkAPIStatus();
    }

    /**
     * Detect which page we're on
     */
    detectCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('history')) {
            this.currentPage = 'history';
        } else {
            this.currentPage = 'index';
        }
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        if (this.currentPage === 'index') {
            this.setupIndexPageListeners();
        } else if (this.currentPage === 'history') {
            this.setupHistoryPageListeners();
        }
    }

    /**
     * Setup event listeners for the main index page
     */
    setupIndexPageListeners() {
        // Photo upload
        const photoInput = document.getElementById('photoInput');
        const uploadArea = document.getElementById('uploadArea');
        const uploadPlaceholder = document.getElementById('uploadPlaceholder');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const removePhoto = document.getElementById('removePhoto');
        const analyzeBtn = document.getElementById('analyzeBtn');

        if (uploadArea) {
            uploadArea.addEventListener('click', () => photoInput.click());
        }

        if (photoInput) {
            photoInput.addEventListener('change', (e) => this.handlePhotoUpload(e.target.files[0]));
        }

        if (removePhoto) {
            removePhoto.addEventListener('click', () => this.removePhoto());
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeSoil());
        }

        // Location handling
        const useLocationCheckbox = document.getElementById('useLocation');
        if (useLocationCheckbox) {
            useLocationCheckbox.addEventListener('change', (e) => this.handleLocationToggle(e.target.checked));
        }

        // Video generation
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        if (generateVideoBtn) {
            generateVideoBtn.addEventListener('click', () => this.generateVideo());
        }
    }

    /**
     * Setup event listeners for the history page
     */
    setupHistoryPageListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Clear history
        const clearHistoryBtn = document.getElementById('clearHistoryBtn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handlePhotoUpload(files[0]);
            }
        });
    }

    /**
     * Handle photo upload
     */
    handlePhotoUpload(file) {
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showAlert('Please select an image file.', 'danger');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showAlert('Image file is too large. Please select an image under 10MB.', 'danger');
            return;
        }

        // Display preview
        this.displayImagePreview(file);
        
        // Enable analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
        }

        // Store file reference
        this.currentPhotoFile = file;
    }

    /**
     * Display image preview
     */
    displayImagePreview(file) {
        const uploadPlaceholder = document.getElementById('uploadPlaceholder');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');

        if (uploadPlaceholder && imagePreview && previewImg) {
            uploadPlaceholder.classList.add('d-none');
            imagePreview.classList.remove('d-none');

            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    /**
     * Remove photo
     */
    removePhoto() {
        const uploadPlaceholder = document.getElementById('uploadPlaceholder');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const photoInput = document.getElementById('photoInput');

        if (uploadPlaceholder && imagePreview) {
            uploadPlaceholder.classList.remove('d-none');
            imagePreview.classList.add('d-none');
        }

        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }

        if (photoInput) {
            photoInput.value = '';
        }

        this.currentPhotoFile = null;
        this.resetResults();
    }

    /**
     * Handle location toggle
     */
    async handleLocationToggle(useLocation) {
        if (useLocation) {
            try {
                const position = await this.getCurrentPosition();
                const latInput = document.getElementById('latitude');
                const lonInput = document.getElementById('longitude');

                if (latInput && lonInput) {
                    latInput.value = position.coords.latitude;
                    lonInput.value = position.coords.longitude;
                }

                this.showAlert('Location obtained successfully!', 'success');
            } catch (error) {
                this.showAlert('Could not get your location. Please enter coordinates manually.', 'warning');
                const useLocationCheckbox = document.getElementById('useLocation');
                if (useLocationCheckbox) {
                    useLocationCheckbox.checked = false;
                }
            }
        }
    }

    /**
     * Get current position
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(resolve, reject, {
                timeout: 10000,
                enableHighAccuracy: false
            });
        });
    }

    /**
     * Analyze soil
     */
    async analyzeSoil() {
        if (!this.currentPhotoFile) {
            this.showAlert('Please select a photo first.', 'warning');
            return;
        }

        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.showLoadingState(true);

        try {
            // Get location data
            let location = null;
            const latInput = document.getElementById('latitude');
            const lonInput = document.getElementById('longitude');
            
            if (latInput && lonInput && latInput.value && lonInput.value) {
                location = {
                    lat: parseFloat(latInput.value),
                    lon: parseFloat(lonInput.value)
                };
            }

            // Call API
            const result = await window.soilAPI.analyzeSoil(this.currentPhotoFile, location);
            
            if (result.success) {
                this.displayResults(result.data);
                this.saveAnalysis(result.data);
            } else {
                throw new Error(result.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.showAlert('Analysis failed. Please try again.', 'danger');
        } finally {
            this.isAnalyzing = false;
            this.showLoadingState(false);
        }
    }

    /**
     * Display analysis results
     */
    displayResults(data) {
        this.currentAnalysis = data;

        // Hide initial state
        const initialState = document.getElementById('initialState');
        const resultsContent = document.getElementById('resultsContent');
        
        if (initialState) initialState.classList.add('d-none');
        if (resultsContent) resultsContent.classList.remove('d-none');

        // Update soil properties
        this.updateSoilProperties(data.analysis);

        // Update AI story
        const aiStory = document.getElementById('aiStory');
        if (aiStory && data.story) {
            aiStory.textContent = data.story;
        }

        // Show video generation button
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        if (generateVideoBtn) {
            generateVideoBtn.classList.remove('d-none');
        }

        // Add animation
        if (resultsContent) {
            resultsContent.classList.add('fade-in');
        }
    }

    /**
     * Update soil properties display
     */
    updateSoilProperties(analysis) {
        const properties = [
            { id: 'ph', value: analysis.pH, progress: 'phProgress', display: 'phValue' },
            { id: 'om', value: analysis.OM, progress: 'omProgress', display: 'omValue' },
            { id: 'p', value: analysis.P, progress: 'pProgress', display: 'pValue' },
            { id: 'ec', value: analysis.EC, progress: 'ecProgress', display: 'ecValue' }
        ];

        properties.forEach(prop => {
            const progressBar = document.getElementById(prop.progress);
            const valueDisplay = document.getElementById(prop.display);

            if (progressBar && valueDisplay) {
                // Calculate percentage based on typical ranges
                let percentage = 0;
                switch (prop.id) {
                    case 'ph':
                        percentage = ((prop.value - 5.0) / (8.5 - 5.0)) * 100;
                        break;
                    case 'om':
                        percentage = (prop.value / 8.0) * 100;
                        break;
                    case 'p':
                        percentage = (prop.value / 60.0) * 100;
                        break;
                    case 'ec':
                        percentage = (prop.value / 3.0) * 100;
                        break;
                }

                percentage = Math.max(0, Math.min(100, percentage));
                progressBar.style.width = percentage + '%';
                valueDisplay.textContent = prop.value;
            }
        });
    }

    /**
     * Generate video from story
     */
    async generateVideo() {
        if (!this.currentAnalysis || this.isGeneratingVideo) return;

        this.isGeneratingVideo = true;
        this.showVideoLoading(true);

        try {
            const result = await window.soilAPI.generateVideo(
                this.currentAnalysis.id,
                this.currentAnalysis.story,
                this.currentAnalysis.imagePath
            );

            if (result.success) {
                this.displayVideoResult(result.data);
                this.updateAnalysisWithVideo(result.data);
            } else {
                throw new Error(result.error || 'Video generation failed');
            }

        } catch (error) {
            console.error('Video generation error:', error);
            this.showAlert('Video generation failed. Please try again.', 'danger');
        } finally {
            this.isGeneratingVideo = false;
            this.showVideoLoading(false);
        }
    }

    /**
     * Display video result
     */
    displayVideoResult(videoData) {
        const videoResult = document.getElementById('videoResult');
        const resultVideo = document.getElementById('resultVideo');
        const downloadVideo = document.getElementById('downloadVideo');

        if (videoResult && resultVideo && downloadVideo) {
            videoResult.classList.remove('d-none');
            resultVideo.src = videoData.videoUrl;
            downloadVideo.href = videoData.videoUrl;
            downloadVideo.download = `soilstory_video_${this.currentAnalysis.id}.mp4`;
        }
    }

    /**
     * Save analysis to localStorage
     */
    saveAnalysis(analysis) {
        try {
            const analysisData = {
                ...analysis,
                timestamp: new Date().toISOString(),
                imageFile: this.currentPhotoFile ? this.currentPhotoFile.name : 'Unknown'
            };

            window.soilStorage.saveAnalysis(analysisData);
        } catch (error) {
            console.error('Failed to save analysis:', error);
            this.showAlert('Failed to save analysis to local storage.', 'warning');
        }
    }

    /**
     * Update analysis with video data
     */
    updateAnalysisWithVideo(videoData) {
        if (!this.currentAnalysis) return;

        try {
            window.soilStorage.updateAnalysis(this.currentAnalysis.id, {
                videoPath: videoData.videoPath,
                videoUrl: videoData.videoUrl
            });
        } catch (error) {
            console.error('Failed to update analysis:', error);
        }
    }

    /**
     * Load initial data
     */
    loadInitialData() {
        if (this.currentPage === 'history') {
            this.loadHistory();
        }
    }

    /**
     * Load analysis history
     */
    async loadHistory() {
        const historyLoading = document.getElementById('historyLoading');
        const emptyHistory = document.getElementById('emptyHistory');
        const historyGrid = document.getElementById('historyGrid');

        if (historyLoading) {
            historyLoading.classList.add('d-none');
        }

        try {
            // Try to get from API first
            const apiResult = await window.soilAPI.getHistory();
            let analyses = [];

            if (apiResult.success && apiResult.data.items) {
                analyses = apiResult.data.items;
            } else {
                // Fallback to localStorage
                analyses = window.soilStorage.getAnalyses();
            }

            if (analyses.length === 0) {
                if (emptyHistory) emptyHistory.classList.remove('d-none');
                return;
            }

            this.displayHistory(analyses);

        } catch (error) {
            console.error('Failed to load history:', error);
            if (emptyHistory) emptyHistory.classList.remove('d-none');
        }
    }

    /**
     * Display history items
     */
    displayHistory(analyses) {
        const historyGrid = document.getElementById('historyGrid');
        if (!historyGrid) return;

        const historyHTML = analyses.map(analysis => this.createHistoryItemHTML(analysis)).join('');
        historyGrid.innerHTML = historyHTML;

        // Add event listeners to history items
        this.setupHistoryItemListeners();
    }

    /**
     * Create HTML for a history item
     */
    createHistoryItemHTML(analysis) {
        const date = new Date(analysis.timestamp || analysis.createdAt).toLocaleDateString();
        const hasVideo = analysis.videoUrl || analysis.videoPath;
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="card history-item h-100">
                    <div class="history-thumbnail">
                        <img src="${analysis.imagePath || '/static/placeholder-soil.jpg'}" 
                             alt="Soil sample" 
                             class="img-fluid">
                        ${hasVideo ? '<span class="history-badge">Video</span>' : ''}
                    </div>
                    <div class="card-body">
                        <h6 class="card-title">Analysis ${analysis.id ? analysis.id.slice(-8) : 'Unknown'}</h6>
                        <p class="small text-muted mb-2">${date}</p>
                        
                        <div class="mb-3">
                            <div class="row g-2">
                                <div class="col-6">
                                    <small class="text-muted">pH</small>
                                    <div class="fw-bold">${analysis.analysis?.pH || 'N/A'}</div>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">OM</small>
                                    <div class="fw-bold">${analysis.analysis?.OM || 'N/A'}</div>
                                </div>
                            </div>
                        </div>
                        
                        <details class="mb-3">
                            <summary class="small text-success">View Story</summary>
                            <p class="small mt-2">${(analysis.story || 'No story available').substring(0, 100)}...</p>
                        </details>
                        
                        <div class="d-flex gap-2">
                            ${hasVideo ? 
                                `<button class="btn btn-sm btn-success flex-fill" onclick="window.soilStoryApp.playVideo('${analysis.videoUrl || analysis.videoPath}')">
                                    <i class="bi bi-play me-1"></i>Play Video
                                </button>` : 
                                '<span class="text-muted small">No video</span>'
                            }
                            <button class="btn btn-sm btn-outline-secondary" onclick="window.soilStoryApp.exportAnalysis('${analysis.id}')">
                                <i class="bi bi-download"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Setup event listeners for history items
     */
    setupHistoryItemListeners() {
        // Event listeners are added inline in the HTML for simplicity
        // In a production app, you might want to use event delegation
    }

    /**
     * Handle search
     */
    handleSearch(query) {
        const analyses = window.soilStorage.searchAnalyses(query);
        this.displayHistory(analyses);
    }

    /**
     * Clear history
     */
    async clearHistory() {
        if (!confirm('Are you sure you want to clear all analysis history? This action cannot be undone.')) {
            return;
        }

        try {
            window.soilStorage.clearAnalyses();
            this.loadHistory();
            this.showAlert('History cleared successfully.', 'success');
        } catch (error) {
            console.error('Failed to clear history:', error);
            this.showAlert('Failed to clear history.', 'danger');
        }
    }

    /**
     * Play video
     */
    playVideo(videoUrl) {
        // Open video in new tab or modal
        window.open(videoUrl, '_blank');
    }

    /**
     * Export analysis
     */
    exportAnalysis(analysisId) {
        try {
            const result = window.soilAPI.exportAnalysisData(analysisId);
            if (result.success) {
                this.showAlert('Analysis exported successfully!', 'success');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Export failed:', error);
            this.showAlert('Failed to export analysis.', 'danger');
        }
    }

    /**
     * Show loading state
     */
    showLoadingState(show) {
        const loadingState = document.getElementById('loadingState');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (loadingState) {
            loadingState.classList.toggle('d-none', !show);
        }
        
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
        }
    }

    /**
     * Show video loading state
     */
    showVideoLoading(show) {
        const videoLoading = document.getElementById('videoLoading');
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        
        if (videoLoading) {
            videoLoading.classList.toggle('d-none', !show);
        }
        
        if (generateVideoBtn) {
            generateVideoBtn.disabled = show;
        }
    }

    /**
     * Reset results display
     */
    resetResults() {
        const initialState = document.getElementById('initialState');
        const resultsContent = document.getElementById('resultsContent');
        const generateVideoBtn = document.getElementById('generateVideoBtn');
        const videoResult = document.getElementById('videoResult');

        if (initialState) initialState.classList.remove('d-none');
        if (resultsContent) resultsContent.classList.add('d-none');
        if (generateVideoBtn) generateVideoBtn.classList.add('d-none');
        if (videoResult) videoResult.classList.add('d-none');

        this.currentAnalysis = null;
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of main content
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(alertDiv, main.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    /**
     * Check API status
     */
    async checkAPIStatus() {
        try {
            const status = await window.soilAPI.getAPIStatus();
            
            if (status.demoMode) {
                this.showAlert('Running in demo mode. Backend server is not available.', 'info');
            }
            
            console.log('API Status:', status);
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.soilStoryApp = new SoilStoryApp();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SoilStoryApp;
}
