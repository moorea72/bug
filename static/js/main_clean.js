// Clean main.js without notification system
// All notification functionality removed as requested by user

// Show loading function for forms
function showLoading(message = 'Loading...') {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        const loadingText = loadingOverlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loadingOverlay.classList.add('show');
        
        // Auto-hide after 2 seconds for better UX
        setTimeout(() => {
            hideLoading();
        }, 2000);
    }
}

function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('show');
    }
}

// Form submission with loading
document.addEventListener('DOMContentLoaded', function() {
    // Add loading to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoading('Processing...');
        });
    });
    
    console.log('✅ Clean main.js loaded - no notification system');
});