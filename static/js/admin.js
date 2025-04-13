/**
 * JBC News - Admin Dashboard JavaScript
 */

document.addEventListener("DOMContentLoaded", function() {
    // Initialize dashboard stats charts
    initDashboardCharts();
    
    // Initialize user management features
    initUserManagement();
    
    // Initialize news management
    initNewsManagement();
    
    // Initialize support ticket management
    initTicketManagement();
    
    // Initialize broadcast messaging
    initBroadcastMessaging();
});

/**
 * Initialize dashboard charts
 */
function initDashboardCharts() {
    // User registration chart (by country)
    const userChart = document.getElementById('userRegistrationChart');
    if (userChart) {
        const userCtx = userChart.getContext('2d');
        
        // Get data from data attributes or use defaults
        const countries = JSON.parse(userChart.getAttribute('data-countries') || '["India", "Pakistan", "USA", "Saudi Arabia", "Sri Lanka"]');
        const userCounts = JSON.parse(userChart.getAttribute('data-counts') || '[45, 35, 25, 20, 15]');
        
        new Chart(userCtx, {
            type: 'pie',
            data: {
                labels: countries,
                datasets: [{
                    data: userCounts,
                    backgroundColor: [
                        '#ff9933', // India
                        '#01411c', // Pakistan
                        '#3c3b6e', // USA
                        '#006c35', // Saudi Arabia
                        '#8d153a'  // Sri Lanka
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'User Distribution by Country'
                    }
                }
            }
        });
    }
    
    // News articles chart (by category)
    const newsChart = document.getElementById('newsDistributionChart');
    if (newsChart) {
        const newsCtx = newsChart.getContext('2d');
        
        // Get data from data attributes or use defaults
        const categories = JSON.parse(newsChart.getAttribute('data-categories') || '["Politics", "Business", "Technology", "Sports", "Entertainment", "Health", "Science", "World"]');
        const newsCounts = JSON.parse(newsChart.getAttribute('data-counts') || '[65, 59, 80, 81, 56, 55, 40, 70]');
        
        new Chart(newsCtx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Number of Articles',
                    data: newsCounts,
                    backgroundColor: '#0056b3',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'News Articles by Category'
                    }
                }
            }
        });
    }
    
    // Activity timeline chart (last 7 days)
    const activityChart = document.getElementById('activityTimelineChart');
    if (activityChart) {
        const activityCtx = activityChart.getContext('2d');
        
        // Get last 7 days
        const days = [];
        const date = new Date();
        for (let i = 6; i >= 0; i--) {
            const d = new Date();
            d.setDate(date.getDate() - i);
            days.push(d.toLocaleDateString('en-US', { weekday: 'short' }));
        }
        
        // Get data from data attributes or use defaults
        const newsActivity = JSON.parse(activityChart.getAttribute('data-news') || '[12, 19, 3, 5, 2, 3, 15]');
        const userActivity = JSON.parse(activityChart.getAttribute('data-users') || '[2, 5, 1, 3, 7, 4, 9]');
        const ticketActivity = JSON.parse(activityChart.getAttribute('data-tickets') || '[1, 2, 3, 4, 2, 1, 5]');
        
        new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [
                    {
                        label: 'News Published',
                        data: newsActivity,
                        borderColor: '#0056b3',
                        backgroundColor: 'rgba(0, 86, 179, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'User Registrations',
                        data: userActivity,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Support Tickets',
                        data: ticketActivity,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Activity Timeline (Last 7 Days)'
                    }
                }
            }
        });
    }
}

/**
 * Initialize user management features
 */
function initUserManagement() {
    // User status toggle buttons
    const statusToggleButtons = document.querySelectorAll('.toggle-user-status');
    if (statusToggleButtons.length > 0) {
        statusToggleButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const userId = this.getAttribute('data-user-id');
                const username = this.getAttribute('data-username');
                const isActive = this.getAttribute('data-is-active') === 'true';
                
                const action = isActive ? 'deactivate' : 'activate';
                if (confirm(`Are you sure you want to ${action} user "${username}"?`)) {
                    // Submit the form
                    const form = document.querySelector(`#toggle-user-form-${userId}`);
                    if (form) {
                        form.submit();
                    }
                }
            });
        });
    }
    
    // User filter form
    const userFilterForm = document.getElementById('userFilterForm');
    if (userFilterForm) {
        const filterInputs = userFilterForm.querySelectorAll('select');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                userFilterForm.submit();
            });
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
    
    // Fetch news button
    const fetchNewsBtn = document.getElementById('fetchNewsBtn');
    if (fetchNewsBtn) {
        fetchNewsBtn.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Fetching...';
            
            // Submit the form
            const form = document.getElementById('fetchNewsForm');
            if (form) {
                form.submit();
            }
        });
    }
    
    // Toggle breaking news status
    const breakingNewsToggles = document.querySelectorAll('.toggle-breaking-news');
    if (breakingNewsToggles.length > 0) {
        breakingNewsToggles.forEach(toggle => {
            toggle.addEventListener('change', function() {
                const newsId = this.getAttribute('data-news-id');
                const isBreaking = this.checked;
                
                fetch(`/admin/news/${newsId}/toggle_breaking`, {
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
                        showAlert('News status updated successfully', 'success');
                    } else {
                        showAlert('Failed to update news status', 'danger');
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
    
    // Ticket status update
    const statusSelects = document.querySelectorAll('.ticket-status-select');
    if (statusSelects.length > 0) {
        statusSelects.forEach(select => {
            select.addEventListener('change', function() {
                const ticketId = this.getAttribute('data-ticket-id');
                const status = this.value;
                
                fetch(`/admin/tickets/${ticketId}/update_status`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ status: status })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Ticket status updated successfully', 'success');
                        
                        // Update ticket UI
                        const ticketItem = document.querySelector(`.ticket-item[data-ticket-id="${ticketId}"]`);
                        if (ticketItem) {
                            ticketItem.className = `ticket-item ${status}`;
                            
                            const statusBadge = ticketItem.querySelector('.ticket-status');
                            if (statusBadge) {
                                statusBadge.className = `ticket-status ${status}`;
                                statusBadge.textContent = status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                            }
                        }
                    } else {
                        showAlert('Failed to update ticket status', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred', 'danger');
                });
            });
        });
    }
}

/**
 * Initialize broadcast messaging
 */
function initBroadcastMessaging() {
    const broadcastForm = document.getElementById('broadcastForm');
    if (broadcastForm) {
        const countrySelect = document.getElementById('countries');
        const userCountDisplay = document.getElementById('userCountDisplay');
        
        if (countrySelect && userCountDisplay) {
            countrySelect.addEventListener('change', function() {
                const country = this.value;
                
                fetch(`/admin/broadcast/user_count?country=${country}`)
                .then(response => response.json())
                .then(data => {
                    userCountDisplay.textContent = `This message will be sent to ${data.count} user(s)`;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        }
        
        broadcastForm.addEventListener('submit', function(e) {
            const messageInput = document.getElementById('message');
            const titleInput = document.getElementById('title');
            
            if (!titleInput.value.trim() || !messageInput.value.trim()) {
                e.preventDefault();
                showAlert('Please enter both title and message', 'danger');
            } else if (messageInput.value.length > 500) {
                e.preventDefault();
                showAlert('Message is too long (maximum 500 characters)', 'danger');
            }
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
