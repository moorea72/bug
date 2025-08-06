// Simple Loading System - No Conflicts
let SimpleLoader;
if (typeof SimpleLoader === 'undefined') {
    SimpleLoader = class {
        constructor() {
            this.overlay = null;
            this.init();
        }

        init() {
            // Create loading overlay if it doesn't exist
            if (!document.getElementById('simpleLoader')) {
                this.createOverlay();
            }
            this.overlay = document.getElementById('simpleLoader');
            
            // Add event listeners for page navigation
            this.addNavigationListeners();
        }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'simpleLoader';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="simple-spinner"></div>
                <div class="loading-text">Loading...</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    show(message = 'Loading...') {
        if (this.overlay) {
            const textElement = this.overlay.querySelector('.loading-text');
            if (textElement) textElement.textContent = message;
            
            this.overlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    addNavigationListeners() {
        // Handle link clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href && !link.href.includes('#') && !link.classList.contains('no-loading')) {
                this.show('Loading...');
            }
        });

        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (!e.target.classList.contains('no-loading')) {
                this.show('Processing...');
            }
        });

        // Handle navigation buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-item') && !e.target.closest('.nav-item').classList.contains('no-loading')) {
                this.show('Loading...');
            }
        });

        // Hide loading on page load
        window.addEventListener('load', () => {
            this.hide();
        });

        // Hide loading on page show (back/forward navigation)
        window.addEventListener('pageshow', () => {
            this.hide();
        });

        // Fallback timeout
        setTimeout(() => {
            this.hide();
        }, 3000);
    }
}

// Initialize the loader immediately
if (!window.simpleLoader) {
    window.simpleLoader = new SimpleLoader();
}

// Also initialize on DOM ready as backup
document.addEventListener('DOMContentLoaded', () => {
    if (!window.simpleLoader) {
        window.simpleLoader = new SimpleLoader();
    }
    
    // Ensure loading works on all clicks
    document.body.addEventListener('click', function(e) {
        const target = e.target;
        if (target.tagName === 'A' && target.href && !target.href.includes('#')) {
            window.simpleLoader.show('Loading...');
        }
        if (target.closest('.nav-item, .bottom-nav a')) {
            window.simpleLoader.show('Loading...');
        }
    });
});

// Global functions for backward compatibility
function showLoading(message = 'Loading...') {
    if (window.simpleLoader) {
        window.simpleLoader.show(message);
    }
}

function hideLoading() {
    if (window.simpleLoader) {
        window.simpleLoader.hide();
    }
}