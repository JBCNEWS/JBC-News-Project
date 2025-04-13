/**
 * JBC News - Main JavaScript File
 */

document.addEventListener("DOMContentLoaded", function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    // Initialize popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popovers.length > 0) {
        popovers.forEach(popover => {
            new bootstrap.Popover(popover);
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }
    
    // Update local times based on country
    updateLocalTimes();
    setInterval(updateLocalTimes, 30000); // Update every 30 seconds
    
    // Initialize search functionality
    initSearch();
    
    // Initialize news sliders if present
    initNewsSliders();
});

/**
 * Updates all local time elements based on country data attribute
 */
function updateLocalTimes() {
    const timeElements = document.querySelectorAll('.local-time');
    if (timeElements.length > 0) {
        timeElements.forEach(el => {
            const countryCode = el.getAttribute('data-country');
            if (countryCode) {
                el.textContent = getLocalTime(countryCode);
            }
        });
    }
}

/**
 * Get formatted local time for a given country code
 * @param {string} countryCode - The 2-letter country code
 * @return {string} Formatted time string
 */
function getLocalTime(countryCode) {
    const date = new Date();
    let options = { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true
    };
    
    let timezone = 'UTC';
    
    // Map country codes to timezones
    switch(countryCode) {
        case 'IN':
            timezone = 'Asia/Kolkata';
            break;
        case 'PK':
            timezone = 'Asia/Karachi';
            break;
        case 'US':
            timezone = 'America/New_York';
            break;
        case 'SA':
            timezone = 'Asia/Riyadh';
            break;
        case 'LK':
            timezone = 'Asia/Colombo';
            break;
    }
    
    options.timeZone = timezone;
    return date.toLocaleTimeString('en-US', options);
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchInput');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
            } else {
                searchInput.classList.remove('is-invalid');
            }
        });
    }
}

/**
 * Initialize news sliders for homepage
 */
function initNewsSliders() {
    // Breaking news ticker animation (CSS handles most of it)
    const breakingNewsContainer = document.querySelector('.breaking-news-container');
    if (breakingNewsContainer) {
        const breakingItems = document.querySelectorAll('.breaking-news-item');
        if (breakingItems.length > 0) {
            // JavaScript can be used to pause the animation on hover
            breakingNewsContainer.addEventListener('mouseenter', function() {
                document.querySelector('.breaking-news-items').style.animationPlayState = 'paused';
            });
            
            breakingNewsContainer.addEventListener('mouseleave', function() {
                document.querySelector('.breaking-news-items').style.animationPlayState = 'running';
            });
        }
    }
}

/**
 * Confirm action (used for delete operations)
 * @param {string} message - Confirmation message
 * @return {boolean} True if confirmed, false otherwise
 */
function confirmAction(message = 'Are you sure you want to proceed?') {
    return confirm(message);
}

/**
 * Format relative time (e.g., "2 hours ago")
 * @param {string} dateString - ISO date string
 * @return {string} Formatted relative time
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) {
        return 'just now';
    } else if (diffMin < 60) {
        return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    } else if (diffHour < 24) {
        return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    } else if (diffDay < 7) {
        return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
}

/**
 * Truncate text to a certain length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @return {string} Truncated text
 */
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}
