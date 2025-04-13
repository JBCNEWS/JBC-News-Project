/**
 * JBC News - Staff Dashboard JavaScript
 */

document.addEventListener("DOMContentLoaded", function() {
    // Initialize news editor if present
    initNewsEditor();
    
    // Initialize news management
    initNewsManagement();
    
    // Initialize support ticket management
    initTicketManagement();
    
    // Initialize news translation
    initNewsTranslation();
});

/**
 * Initialize rich text editor for news content
 */
function initNewsEditor() {
    const contentTextarea = document.getElementById('content');
    if (contentTextarea) {
        // Check if we have access to a rich text editor library
        // If not, we'll use a simple enhancement
        if (typeof ClassicEditor !== 'undefined') {
            ClassicEditor
                .create(contentTextarea)
                .catch(error => {
                    console.error(error);
                });
        } else {
            // Simple textarea enhancements
            contentTextarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
            
            // Fire the event once to adjust initial size
            const inputEvent = new Event('input');
            contentTextarea.dispatchEvent(inputEvent);
        }
    }
    
    // Image URL preview
    const imageUrlInput = document.getElementById('image_url');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageUrlInput && imagePreview) {
        imageUrlInput.addEventListener('input', function() {
            const url = this.value.trim();
            if (url) {
                imagePreview.src = url;
                imagePreview.classList.remove('d-none');
            } else {
                imagePreview.classList.add('d-none');
            }
        });
        
        // Check if we already have a URL
        if (imageUrlInput.value.trim()) {
            imagePreview.src = imageUrlInput.value.trim();
            imagePreview.classList.remove('d-none');
        }
    }
    
    // Random image button
    const randomImageBtn = document.getElementById('randomImageBtn');
    if (randomImageBtn && imageUrlInput) {
        randomImageBtn.addEventListener('click', function() {
            // Array of sample news images from Unsplash
            const randomImages = [
                'https://images.unsplash.com/photo-1495020689067-958852a7765e',
                'https://images.unsplash.com/photo-1504711434969-e33886168f5c',
                'https://images.unsplash.com/photo-1560957123-e8e019c66980',
                'https://images.unsplash.com/photo-1581092787765-e3feb951d987',
                'https://images.unsplash.com/photo-1585282263861-f55e341878f8',
                'https://images.unsplash.com/photo-1593789198777-f29bc259780e'
            ];
            
            const randomUrl = randomImages[Math.floor(Math.random() * randomImages.length)];
            imageUrlInput.value = randomUrl;
            
            // Trigger input event to update preview
            const inputEvent = new Event('input');
            imageUrlInput.dispatchEvent(inputEvent);
        });
    }
}

/**
 * Initialize news management features
 */
function initNewsManagement() {
    // News filter form
    const newsFilterForm = document.getElementById('newsFilterForm');
    if (newsFilterForm) {
        const filterInputs = newsFilterForm.querySelectorAll('select');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                newsFilterForm.submit();
            });
        });
    }
    
    // News publish/unpublish buttons
    const publishButtons = document.querySelectorAll('.publish-news-btn');
    if (publishButtons.length > 0) {
        publishButtons.forEach(button => {
            button.addEventListener('click', function() {
                const newsId = this.getAttribute('data-news-id');
                const action = this.getAttribute('data-action'); // 'publish' or 'unpublish'
                const title = this.getAttribute('data-title');
                
                if (confirm(`Are you sure you want to ${action} "${title}"?`)) {
                    // Create and submit form
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/staff/news/${newsId}/${action}`;
                    
                    // Add CSRF token
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrf_token';
                    csrfInput.value = getCsrfToken();
                    form.appendChild(csrfInput);
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    }
    
    // Breaking news toggle
    const breakingNewsToggles = document.querySelectorAll('.toggle-breaking-news');
    if (breakingNewsToggles.length > 0) {
        breakingNewsToggles.forEach(toggle => {
            toggle.addEventListener('change', function() {
                const newsId = this.getAttribute('data-news-id');
                const isBreaking = this.checked;
                
                fetch(`/staff/news/${newsId}/toggle_breaking`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ is_breaking: isBreaking })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Breaking news status updated', 'success');
                    } else {
                        showAlert('Failed to update breaking news status', 'danger');
                        toggle.checked = !isBreaking; // Revert toggle
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred', 'danger');
                    toggle.checked = !isBreaking; // Revert toggle
                });
            });
        });
    }
}

/**
 * Initialize support ticket management
 */
function initTicketManagement() {
    // Ticket filter form
    const ticketFilterForm = document.getElementById('ticketFilterForm');
    if (ticketFilterForm) {
        const filterInputs = ticketFilterForm.querySelectorAll('select');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                ticketFilterForm.submit();
            });
        });
    }
    
    // Response form
    const responseForm = document.getElementById('responseForm');
    if (responseForm) {
        responseForm.addEventListener('submit', function(e) {
            const messageInput = document.getElementById('message');
            if (!messageInput.value.trim()) {
                e.preventDefault();
                showAlert('Please enter a message', 'danger');
            }
        });
    }
}

/**
 * Initialize news translation features
 */
function initNewsTranslation() {
    const translateBtn = document.getElementById('translateNewsBtn');
    if (translateBtn) {
        translateBtn.addEventListener('click', function() {
            const newsId = this.getAttribute('data-news-id');
            const loadingSpinner = document.getElementById('translationSpinner');
            
            if (loadingSpinner) {
                loadingSpinner.classList.remove('d-none');
            }
            
            this.disabled = true;
            
            fetch(`/staff/news/${newsId}/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('News article translated successfully', 'success');
                } else {
                    showAlert('Failed to translate news article', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred during translation', 'danger');
            })
            .finally(() => {
                this.disabled = false;
                if (loadingSpinner) {
                    loadingSpinner.classList.add('d-none');
                }
            });
        });
    }
    
    // Language tabs for translations
    const languageTabs = document.querySelectorAll('.translation-tab');
    if (languageTabs.length > 0) {
        languageTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all tabs
                languageTabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Show corresponding translation content
                const lang = this.getAttribute('data-lang');
                const translationContents = document.querySelectorAll('.translation-content');
                
                translationContents.forEach(content => {
                    if (content.getAttribute('data-lang') === lang) {
                        content.classList.remove('d-none');
                    } else {
                        content.classList.add('d-none');
                    }
                });
            });
        });
    }
}

/**
 * Show an alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) {
        console.error('Alerts container not found');
        return;
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

/**
 * Get CSRF token from cookies
 * @return {string} CSRF token
 */
function getCsrfToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    
    return '';
}
