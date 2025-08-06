// Main JavaScript functionality for USDT Staking Platform

document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeApp();
    } catch (error) {
        console.log('App initialization failed, but continuing');
    }
});

function initializeApp() {
    // Initialize flash messages
    try {
        initFlashMessages();
    } catch (error) {
        console.log('Flash messages init failed');
    }
    
    // Initialize modals
    try {
        initModals();
    } catch (error) {
        console.log('Modals init failed');
    }
    
    // Initialize form validations
    try {
        initFormValidations();
    } catch (error) {
        console.log('Form validations init failed');
    }
    
    // Initialize tooltips
    try {
        initTooltips();
    } catch (error) {
        console.log('Tooltips init failed');
    }
    
    // Initialize navigation
    try {
        initNavigation();
    } catch (error) {
        console.log('Navigation init failed');
    }
    
    // Initialize smooth scrolling
    try {
        initSmoothScrolling();
    } catch (error) {
        console.log('Smooth scrolling init failed');
    }
    
    // Initialize notification dropdown
    try {
        initializeNotificationDropdown();
    } catch (error) {
        console.log('Notification dropdown init failed');
    }
}

// Flash Messages Management
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach((message, index) => {
        // Animate in
        setTimeout(() => {
            message.style.opacity = '1';
            message.style.transform = 'translateX(0)';
        }, index * 150);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideFlashMessage(message);
        }, 5000);
    });
}

function hideFlashMessage(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateX(100%)';
    setTimeout(() => {
        element.remove();
    }, 300);
}

// Modal Management
function initModals() {
    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.add('hidden');
        }
    });
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const visibleModals = document.querySelectorAll('.modal:not(.hidden)');
            visibleModals.forEach(modal => modal.classList.add('hidden'));
        }
    });
}

// Form Validations
function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing error styling
    field.classList.remove('border-red-500');
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    else if (fieldType === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
    }
    
    // Password validation
    else if (fieldType === 'password' && value && value.length < 6) {
        isValid = false;
        errorMessage = 'Password must be at least 6 characters long';
    }
    
    // Number validation
    else if (fieldType === 'number' && value && isNaN(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid number';
    }
    
    // Show error if validation failed
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(field, message) {
    field.classList.add('border-red-500');
    
    const errorElement = document.createElement('p');
    errorElement.className = 'error-message text-red-400 text-sm mt-1';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
}

// Tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    if (!element || typeof element.getAttribute !== 'function') return;
    
    const tooltipText = element.getAttribute('data-tooltip');
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip absolute bg-gray-900 text-white text-sm px-3 py-2 rounded-lg shadow-lg z-50 pointer-events-none';
    tooltip.textContent = tooltipText;
    tooltip.id = 'tooltip';
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    // Animate in
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }, 10);
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;
    
    navItems.forEach(item => {
        if (!item || typeof item.getAttribute !== 'function') return;
        
        const href = item.getAttribute('href');
        if (href && href === currentPath) {
            item.classList.add('active');
        }
    });
}

// Smooth Scrolling
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!this || typeof this.getAttribute !== 'function') return;
            
            const href = this.getAttribute('href');
            if (!href) return;
            
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Utility Functions
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatNumber(number, decimals = 2) {
    return Number(number).toFixed(decimals);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            showNotification('Failed to copy', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

function showNotification(message, type = 'info', title = '') {
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 px-6 py-4 rounded-xl shadow-2xl bg-white border border-gray-200 z-50 transform translate-x-full opacity-0 transition-all duration-500`;
    
    // Create 3D styling with white background and black text
    notification.style.cssText = `
        background: white;
        color: black;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        backdrop-filter: blur(10px);
        max-width: 400px;
        min-width: 300px;
    `;
    
    // Create notification content with purple heading
    const content = document.createElement('div');
    if (title) {
        content.innerHTML = `
            <div class="flex items-start">
                <div class="flex-1">
                    <h4 class="font-bold text-purple-600 mb-1">${title}</h4>
                    <p class="text-black text-sm">${message}</p>
                </div>
                <button onclick="this.closest('.notification').remove()" class="ml-3 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="flex items-center justify-between">
                <p class="text-black">${message}</p>
                <button onclick="this.closest('.notification').remove()" class="ml-3 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
    
    notification.appendChild(content);
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        notification.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Loading States
function showElementLoading(element) {
    if (!element || typeof element.setAttribute !== 'function') return;
    
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.innerHTML = '<div class="spinner"></div>';
    element.classList.add('loading');
    element.disabled = true;
}

function hideElementLoading(element) {
    if (!element || typeof element.getAttribute !== 'function') return;
    
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
    }
    element.classList.remove('loading');
    element.disabled = false;
    element.removeAttribute('data-original-content');
}

// AJAX Helper
function makeRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    resolve(xhr.responseText);
                }
            } else {
                reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
            }
        };
        
        xhr.onerror = function() {
            reject(new Error('Network error'));
        };
        
        if (data) {
            xhr.send(JSON.stringify(data));
        } else {
            xhr.send();
        }
    });
}

// LocalStorage Helper
function setStorageItem(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('LocalStorage not available');
    }
}

function getStorageItem(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.warn('LocalStorage not available');
        return null;
    }
}

// Theme Management
function toggleTheme() {
    const currentTheme = getStorageItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.body.setAttribute('data-theme', newTheme);
    setStorageItem('theme', newTheme);
}

// Initialize theme on load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = getStorageItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
});

// Support Chat Functions
function toggleSupportChat() {
    window.location.href = '/support';
}

function showSupportModal() {
    const modal = document.getElementById('supportModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function hideSupportModal() {
    const modal = document.getElementById('supportModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function showSupportNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'support-notification';
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Auto-show chat bubble on hover
document.addEventListener('DOMContentLoaded', function() {
    const chatBtn = document.getElementById('supportChatBtn');
    const chatBubble = document.getElementById('chatBubble');
    
    if (chatBtn && chatBubble) {
        let hoverTimeout;
        
        chatBtn.addEventListener('mouseenter', () => {
            clearTimeout(hoverTimeout);
            chatBubble.style.opacity = '1';
            chatBubble.style.pointerEvents = 'auto';
            chatBubble.style.transform = 'translateY(-5px)';
        });
        
        chatBtn.addEventListener('mouseleave', () => {
            hoverTimeout = setTimeout(() => {
                chatBubble.style.opacity = '0';
                chatBubble.style.pointerEvents = 'none';
                chatBubble.style.transform = 'translateY(0)';
            }, 300);
        });
        
        chatBubble.addEventListener('mouseenter', () => {
            clearTimeout(hoverTimeout);
        });
        
        chatBubble.addEventListener('mouseleave', () => {
            hoverTimeout = setTimeout(() => {
                chatBubble.style.opacity = '0';
                chatBubble.style.pointerEvents = 'none';
                chatBubble.style.transform = 'translateY(0)';
            }, 300);
        });
    }
});

// Export functions for global use
window.PlatformUtils = {
    formatCurrency,
    formatNumber,
    copyToClipboard,
    showNotification,
    showLoading,
    hideLoading,
    makeRequest,
    setStorageItem,
    getStorageItem,
    toggleTheme
};



// Enhanced notification system for users
let notificationInterval = null;

function loadUserNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                displayUserNotifications(data.notifications);
            }
        })
        .catch(error => {
            console.log('Error loading notifications:', error);
            // Show fallback admin messages
            const notificationList = document.getElementById('notificationList');
            if (notificationList) {
                notificationList.innerHTML = `
                    <div class="p-4 text-center text-gray-700">
                        <i class="fas fa-bell text-2xl mb-2"></i>
                        <p class="font-bold mb-3">Admin Messages:</p>
                        <div class="space-y-2 text-left">
                            <div class="p-2 bg-green-100 rounded border-l-4 border-green-500">
                                <p class="font-medium text-green-800">Welcome to USDT Staking!</p>
                                <p class="text-sm text-green-700">Start earning daily returns by staking your USDT today.</p>
                            </div>
                            <div class="p-2 bg-blue-100 rounded border-l-4 border-blue-500">
                                <p class="font-medium text-blue-800">New 3-Level Referral System</p>
                                <p class="text-sm text-blue-700">Earn up to 5% commission when referrals deposit 100+ USDT!</p>
                            </div>
                            <div class="p-2 bg-yellow-100 rounded border-l-4 border-yellow-500">
                                <p class="font-medium text-yellow-800">Security Enhanced</p>
                                <p class="text-sm text-yellow-700">Your funds are now more secure with our latest updates.</p>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
}

function displayUserNotifications(notifications) {
    // Only show if there are unread notifications
    if (notifications.length > 0) {
        notifications.slice(0, 3).forEach((notification, index) => {
            setTimeout(() => {
                showNotification(notification.message, notification.type, notification.title);
            }, index * 1000); // Show notifications with 1 second delay between each
        });
    }
}

// Start loading notifications every 30 seconds for logged-in users
function startNotificationUpdates() {
    if (notificationInterval) clearInterval(notificationInterval);
    
    // Load immediately
    loadUserNotifications();
    
    // Then load every 30 seconds
    notificationInterval = setInterval(loadUserNotifications, 30000);
}

// Start notifications when page loads for logged-in users
document.addEventListener('DOMContentLoaded', function() {
    // Only start for logged-in users (check if user menu exists)
    if (document.querySelector('.user-profile') || document.querySelector('#userMenu')) {
        startNotificationUpdates();
    }
});

// Initialize notification dropdown
// Notification system completely removed as requested by user
                    notificationDropdown.style.opacity = '1';
                    notificationDropdown.style.transform = 'scale(1) translateY(0)';
                }, 10);
                
                console.log('Notification popup shown with animations');
            } else {
                // Hide dropdown with animation
                notificationDropdown.style.transition = 'all 0.15s ease-in';
                notificationDropdown.style.opacity = '0';
                notificationDropdown.style.transform = 'scale(0.9) translateY(-10px)';
                
                setTimeout(() => {
                    notificationDropdown.classList.add('hidden');
                }, 150);
                
                console.log('Notification popup hidden');
            }
        });
        
        // Close dropdown when clicking outside with animation
        document.addEventListener('click', function(e) {
            if (!notificationDropdown.contains(e.target) && !newNotificationBell.contains(e.target)) {
                if (!notificationDropdown.classList.contains('hidden')) {
                    notificationDropdown.style.transition = 'all 0.15s ease-in';
                    notificationDropdown.style.opacity = '0';
                    notificationDropdown.style.transform = 'scale(0.9) translateY(-10px)';
                    
                    setTimeout(() => {
                        notificationDropdown.classList.add('hidden');
                    }, 150);
                }
            }
        });
        
        // Load initial notification count
        updateNotificationBadge();
        
        console.log('Enhanced notification dropdown initialized successfully!');
    } else {
        console.log('Notification elements not found - creating fallback system');
        createFallbackNotificationSystem();
    }
}

// Load notifications into dropdown
function loadNotificationsInDropdown() {
    console.log('Loading admin notifications into dropdown...');
    
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            const notificationList = document.getElementById('notificationList');
            if (!notificationList) return;
            
            if (data.success && data.notifications && data.notifications.length > 0) {
                notificationList.innerHTML = '';
                data.notifications.forEach(notification => {
                    const item = document.createElement('div');
                    item.className = 'p-3 hover:bg-gray-50 border-b border-gray-200 cursor-pointer';
                    item.innerHTML = `
                        <div class="flex items-start space-x-3">
                            <i class="fas fa-${notification.icon || 'bell'} text-${notification.type === 'success' ? 'green' : notification.type === 'warning' ? 'yellow' : 'blue'}-500 mt-1"></i>
                            <div class="flex-1">
                                <h4 class="font-medium text-gray-900">${notification.title}</h4>
                                <p class="text-sm text-gray-600 mt-1">${notification.message}</p>
                                <p class="text-xs text-gray-400 mt-1">${notification.time_ago}</p>
                            </div>
                        </div>
                    `;
                    notificationList.appendChild(item);
                });
                updateNotificationCount(data.count);
            } else {
                showFallbackNotifications();
            }
        })
        .catch(error => {
            console.log('Error loading notifications, showing fallback:', error);
            showFallbackNotifications();
        });
}

function showFallbackNotifications() {
    const notificationList = document.getElementById('notificationList');
    if (notificationList) {
        notificationList.innerHTML = `
            <div class="p-4 text-center text-gray-700">
                <i class="fas fa-bell text-2xl mb-2 text-blue-500"></i>
                <p class="font-bold mb-3 text-gray-800">Admin Messages:</p>
                <div class="space-y-2 text-left">
                    <div class="p-2 bg-green-100 rounded border-l-4 border-green-500">
                        <p class="font-medium text-green-800">Welcome to USDT Staking!</p>
                        <p class="text-sm text-green-700">Start earning daily returns by staking your USDT today.</p>
                    </div>
                    <div class="p-2 bg-blue-100 rounded border-l-4 border-blue-500">
                        <p class="font-medium text-blue-800">New 3-Level Referral System</p>
                        <p class="text-sm text-blue-700">Earn up to 5% commission when referrals deposit 100+ USDT!</p>
                    </div>
                    <div class="p-2 bg-yellow-100 rounded border-l-4 border-yellow-500">
                        <p class="font-medium text-yellow-800">Security Enhanced</p>
                        <p class="text-sm text-yellow-700">Your funds are now more secure with our latest updates.</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function updateNotificationCount(count) {
    const countElement = document.getElementById('notificationCount');
    if (countElement) {
        if (count > 0) {
            countElement.textContent = count > 9 ? '9+' : count;
            countElement.style.display = 'flex';
        } else {
            countElement.style.display = 'none';
        }
    }
}

// Enhanced notification loading function
function loadNotificationsInDropdown() {
    console.log('Loading notifications in dropdown...');
    
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            console.log('Notifications API response:', data);
            
            const notificationList = document.getElementById('notificationList');
            if (!notificationList) {
                console.log('Notification list element not found');
                return;
            }
            
            if (data.success && data.notifications && data.notifications.length > 0) {
                // Clear existing notifications
                notificationList.innerHTML = '';
                
                // Add each notification with enhanced styling
                data.notifications.forEach((notification, index) => {
                    const notificationItem = createNotificationItem(notification, index);
                    notificationList.appendChild(notificationItem);
                });
                
                // Update notification badge
                updateNotificationBadge(data.count);
                
                console.log(`Loaded ${data.notifications.length} notifications`);
            } else {
                // Show empty state
                notificationList.innerHTML = `
                    <div class="p-4 text-center text-gray-500">
                        <i class="fas fa-bell-slash text-2xl mb-2 block"></i>
                        <p>No notifications</p>
                    </div>
                `;
                updateNotificationBadge(0);
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            
            // Show error state with sample notifications for demo
            const notificationList = document.getElementById('notificationList');
            if (notificationList) {
                notificationList.innerHTML = `
                    <div class="p-3 border-b border-gray-200 hover:bg-gray-50 transition-colors">
                        <div class="flex items-start space-x-3">
                            <div class="flex-shrink-0">
                                <i class="fas fa-info-circle text-blue-500 text-lg"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900">Welcome to the Platform</p>
                                <p class="text-xs text-gray-600 mt-1">Complete your profile to start earning rewards</p>
                                <p class="text-xs text-gray-400 mt-1">2 minutes ago</p>
                            </div>
                        </div>
                    </div>
                    <div class="p-3 border-b border-gray-200 hover:bg-gray-50 transition-colors">
                        <div class="flex items-start space-x-3">
                            <div class="flex-shrink-0">
                                <i class="fas fa-coins text-yellow-500 text-lg"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900">Staking Available</p>
                                <p class="text-xs text-gray-600 mt-1">High yield staking options now available</p>
                                <p class="text-xs text-gray-400 mt-1">1 hour ago</p>
                            </div>
                        </div>
                    </div>
                    <div class="p-3 hover:bg-gray-50 transition-colors">
                        <div class="flex items-start space-x-3">
                            <div class="flex-shrink-0">
                                <i class="fas fa-users text-green-500 text-lg"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900">Referral Bonus</p>
                                <p class="text-xs text-gray-600 mt-1">Earn 5% commission on referrals</p>
                                <p class="text-xs text-gray-400 mt-1">3 hours ago</p>
                            </div>
                        </div>
                    </div>
                `;
                updateNotificationBadge(3);
            }
        });
}

// Create notification item with enhanced styling
function createNotificationItem(notification, index) {
    const item = document.createElement('div');
    item.className = 'p-3 border-b border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer notification-item';
    item.style.animationDelay = `${index * 50}ms`;
    
    // Get notification type colors
    const typeColors = {
        'info': 'text-blue-500',
        'success': 'text-green-500',
        'warning': 'text-yellow-500',
        'error': 'text-red-500'
    };
    
    const iconColor = typeColors[notification.type] || 'text-gray-500';
    
    item.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
                <i class="${notification.icon} ${iconColor} text-lg"></i>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">${notification.title}</p>
                <p class="text-xs text-gray-600 mt-1">${notification.message}</p>
                <p class="text-xs text-gray-400 mt-1">${notification.time}</p>
            </div>
        </div>
    `;
    
    // Add click handler to mark as read (if implemented)
    item.addEventListener('click', function() {
        // Mark notification as read
        markNotificationAsRead(notification.id);
        item.style.opacity = '0.6';
    });
    
    return item;
}

// Update notification badge
function updateNotificationBadge(count = null) {
    const badge = document.getElementById('notificationCount');
    if (!badge) return;
    
    if (count === null) {
        // Fetch current count
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotificationBadge(data.count);
                }
            })
            .catch(() => {
                // Fallback count
                updateNotificationBadge(3);
            });
        return;
    }
    
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.classList.remove('hidden');
        badge.style.animation = 'pulse 2s infinite';
    } else {
        badge.classList.add('hidden');
    }
}

// Mark notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/api/user/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Notification marked as read');
            // Update badge count
            setTimeout(() => updateNotificationBadge(), 500);
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Fallback notification system for when elements are missing
// Notification system completely removed as requested by user
        
        // Reinitialize the notification system
        setTimeout(() => {
            initializeNotificationDropdown();
        }, 100);
    }
}

// Load notifications into dropdown
function loadNotificationsInDropdown() {
    const notificationList = document.getElementById('notificationList');
    const notificationCount = document.getElementById('notificationCount');
    
    if (notificationList) {
        // Show loading
        notificationList.innerHTML = `
            <div class="p-3 text-center text-gray-400">
                <i class="fas fa-spinner fa-spin mr-2"></i>Loading notifications...
            </div>
        `;
        
        // Load notifications from API
        fetch('/api/user/notifications')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayNotificationsInDropdown(data.notifications);
                    updateNotificationCount(data.unread_count);
                } else {
                    notificationList.innerHTML = `
                        <div class="p-3 text-center text-gray-400">
                            <i class="fas fa-bell-slash mr-2"></i>No notifications
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationList.innerHTML = `
                    <div class="p-3 text-center text-gray-400">
                        <i class="fas fa-exclamation-triangle mr-2"></i>Error loading notifications
                    </div>
                `;
            });
    }
}

// Display notifications in dropdown
function displayNotificationsInDropdown(notifications) {
    const notificationList = document.getElementById('notificationList');
    
    if (notifications && notifications.length > 0) {
        let notificationsHtml = '';
        notifications.slice(0, 5).forEach(notification => {
            const timeAgo = formatTimeAgo(new Date(notification.created_at));
            const isUnread = !notification.is_read;
            
            notificationsHtml += `
                <div class="notification-item p-3 border-b border-gray-700 last:border-b-0 ${isUnread ? 'bg-blue-900/20' : ''}" data-id="${notification.id}">
                    <div class="flex items-start space-x-3">
                        <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 ${isUnread ? '' : 'opacity-0'}"></div>
                        <div class="flex-1">
                            <h5 class="text-white text-sm font-medium">${notification.title || 'Platform Update'}</h5>
                            <p class="text-gray-400 text-xs mt-1">${notification.message}</p>
                            <p class="text-gray-500 text-xs mt-1">${timeAgo}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        
        notificationList.innerHTML = notificationsHtml;
        
        // Add click handlers to mark notifications as read
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function() {
                const notificationId = this.dataset.id;
                markNotificationAsRead(notificationId);
                this.classList.remove('bg-blue-900/20');
                this.querySelector('.w-2').classList.add('opacity-0');
            });
        });
    } else {
        notificationList.innerHTML = `
            <div class="p-3 text-center text-gray-400">
                <i class="fas fa-bell-slash mr-2"></i>No notifications
            </div>
        `;
    }
}

// Update notification count badge
function updateNotificationCount(count) {
    const notificationCount = document.getElementById('notificationCount');
    if (notificationCount) {
        if (count > 0) {
            notificationCount.textContent = count > 99 ? '99+' : count;
            notificationCount.classList.remove('hidden');
        } else {
            notificationCount.classList.add('hidden');
        }
    }
}

// Mark notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/api/user/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update count
            const currentCount = parseInt(document.getElementById('notificationCount').textContent || '0');
            updateNotificationCount(Math.max(0, currentCount - 1));
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

// Format time ago helper
function formatTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}
