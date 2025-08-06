// Optimized Loading System with Error Handling

class OptimizedLoader {
    constructor() {
        this.isShowing = false;
        this.timeouts = [];
        this.init();
    }

    init() {
        // Create loading overlay if not exists
        if (!document.getElementById('globalLoader')) {
            this.createLoader();
        }
        
        // Attach form and navigation listeners
        this.attachListeners();
        
        // Auto-hide loader on page load
        this.hideLoading();
    }

    createLoader() {
        const loader = document.createElement('div');
        loader.id = 'globalLoader';
        loader.className = 'loading-container hide';
        loader.innerHTML = `
            <div class="loading-backdrop"></div>
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p class="loading-text">Loading...</p>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .loading-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: opacity 0.15s ease-out;
                pointer-events: none;
            }
            
            .loading-container.show {
                opacity: 1;
                pointer-events: all;
            }
            
            .loading-container.hide {
                opacity: 0;
                pointer-events: none;
            }
            
            .loading-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(4px);
            }
            
            .loading-content {
                position: relative;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                text-align: center;
                min-width: 200px;
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #e2e8f0;
                border-radius: 50%;
                border-top-color: #3b82f6;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 15px;
            }
            
            .loading-text {
                margin: 0;
                color: #374151;
                font-weight: 500;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(loader);
    }

    showLoading(message = 'Loading...', timeout = 8000) {
        if (this.isShowing) return;
        
        this.isShowing = true;
        const loader = document.getElementById('globalLoader');
        const textElement = loader.querySelector('.loading-text');
        
        if (textElement) {
            textElement.textContent = message;
        }
        
        loader.classList.remove('hide');
        loader.classList.add('show');
        
        console.log('Showing loading:', message);
        
        // Auto-hide after timeout to prevent stuck screens
        const timeoutId = setTimeout(() => {
            this.hideLoading();
            console.warn('Loading timeout reached, auto-hiding');
        }, timeout);
        
        this.timeouts.push(timeoutId);
    }

    hideLoading() {
        if (!this.isShowing) return;
        
        this.isShowing = false;
        const loader = document.getElementById('globalLoader');
        
        if (loader) {
            loader.classList.remove('show');
            loader.classList.add('hide');
        }
        
        // Clear all timeouts
        this.timeouts.forEach(id => clearTimeout(id));
        this.timeouts = [];
        
        console.log('Hiding loading');
    }

    attachListeners() {
        // Only show loading for form submissions, not navigation
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                this.showLoading('Processing...', 8000);
            }
        });

        // Remove automatic navigation loading - user complained about it

        // Page visibility change (hide loader when page becomes visible)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                setTimeout(() => this.hideLoading(), 100);
            }
        });

        // Window load event
        window.addEventListener('load', () => {
            setTimeout(() => this.hideLoading(), 100);
        });

        // DOMContentLoaded event
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => this.hideLoading(), 100);
        });
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fee2e2;
            color: #991b1b;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            errorDiv.style.transform = 'translateX(100%)';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-notification';
        successDiv.textContent = message;
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dcfce7;
            color: #166534;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.style.opacity = '0';
            successDiv.style.transform = 'translateX(100%)';
            setTimeout(() => successDiv.remove(), 300);
        }, 4000);
    }
}

// Initialize loader when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.optimizedLoader = new OptimizedLoader();
    });
} else {
    window.optimizedLoader = new OptimizedLoader();
}

// Global functions for manual control
window.showLoading = (message, timeout) => {
    if (window.optimizedLoader) {
        window.optimizedLoader.showLoading(message, timeout);
    }
};

window.hideLoading = () => {
    if (window.optimizedLoader) {
        window.optimizedLoader.hideLoading();
    }
};

window.showError = (message) => {
    if (window.optimizedLoader) {
        window.optimizedLoader.showError(message);
    }
};

window.showSuccess = (message) => {
    if (window.optimizedLoader) {
        window.optimizedLoader.showSuccess(message);
    }
};