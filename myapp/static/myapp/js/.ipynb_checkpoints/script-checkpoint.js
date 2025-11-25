// Cosmetic Management System Frontend JavaScript

// Utility function: Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US');
}

// Utility function: Get expiry status text
function getExpiryStatusText(status) {
    const statusMap = {
        'good': 'Good',
        'soon': 'Expiring Soon', 
        'urgent': 'Urgent',
        'expired': 'Expired',
        'unknown': 'Unknown'
    };
    return statusMap[status] || 'Unknown';
}

// Utility function: Get expiry status class
function getExpiryStatusClass(status) {
    return `status-${status}`;
}

// Confirm deletion dialog
function confirmDelete(productName, deleteUrl) {
    if (confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) {
        // Create hidden form to submit delete request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = deleteUrl;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const productCards = document.querySelectorAll('.product-card, tbody tr');
            
            productCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Set up search functionality
    setupSearch();
    
    // Set up tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alert messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Set up form validation
    enhanceForms();
});

// Form validation enhancement
function enhanceForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Add error message if not exists
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'invalid-feedback';
                        errorDiv.textContent = 'This field is required';
                        field.parentNode.appendChild(errorDiv);
                    }
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Show error message
                const errorDiv = this.querySelector('.alert-danger') || document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.textContent = 'Please fill in all required fields';
                this.insertBefore(errorDiv, this.firstChild);
            }
        });
    });
}

// Calculate days until expiration
function calculateDaysUntil(expirationDate) {
    const today = new Date();
    const expiry = new Date(expirationDate);
    const diffTime = expiry - today;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// Calculate expiry status
function calculateExpiryStatus(expirationDate) {
    const days = calculateDaysUntil(expirationDate);
    if (days < 0) return 'expired';
    if (days <= 7) return 'urgent';
    if (days <= 30) return 'soon';
    return 'good';
}