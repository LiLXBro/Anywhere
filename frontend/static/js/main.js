// Main JavaScript file for Parking App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the app
    initializeApp();
});

function initializeApp() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 5000);
    
    // Form validation
    setupFormValidation();
    
    // Setup dynamic updates
    setupDynamicUpdates();
    
    // Setup confirmation dialogs
    setupConfirmationDialogs();
}

function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#ff0000';
                    showFieldError(field, 'This field is required');
                } else {
                    field.style.borderColor = '#000000';
                    hideFieldError(field);
                }
                
                // Specific validations
                if (field.type === 'email' && field.value) {
                    if (!isValidEmail(field.value)) {
                        isValid = false;
                        field.style.borderColor = '#ff0000';
                        showFieldError(field, 'Please enter a valid email');
                    }
                }
                
                if (field.name === 'phone' && field.value) {
                    if (!isValidPhone(field.value)) {
                        isValid = false;
                        field.style.borderColor = '#ff0000';
                        showFieldError(field, 'Please enter a valid phone number');
                    }
                }
                
                if (field.name === 'vehicle_number' && field.value) {
                    if (!isValidVehicleNumber(field.value)) {
                        isValid = false;
                        field.style.borderColor = '#ff0000';
                        showFieldError(field, 'Please enter a valid vehicle number');
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function setupDynamicUpdates() {
    // Auto-refresh dashboard data every 30 seconds
    if (window.location.pathname.includes('dashboard')) {
        setInterval(function() {
            updateDashboardStats();
        }, 30000);
    }
}

function setupConfirmationDialogs() {
    // Setup delete confirmations
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = button.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    hideFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#ff0000';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[6-9]\d{9}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

function isValidVehicleNumber(vehicleNumber) {
    // Indian vehicle number format: XX00XX0000 or XX-00-XX-0000
    const vehicleRegex = /^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$|^[A-Z]{2}-[0-9]{2}-[A-Z]{2}-[0-9]{4}$/;
    return vehicleRegex.test(vehicleNumber.toUpperCase().replace(/\s/g, ''));
}

function updateDashboardStats() {
    // Fetch updated statistics via API
    fetch('/api/lots')
        .then(response => response.json())
        .then(data => {
            // Update stats if elements exist
            updateStatElement('total-lots', data.length);
            updateStatElement('available-spots', data.reduce((sum, lot) => sum + lot.available_spots, 0));
            updateStatElement('occupied-spots', data.reduce((sum, lot) => sum + lot.occupied_spots, 0));
        })
        .catch(error => console.log('Update failed:', error));
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

// Utility functions
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN');
}

function toggleLoading(show, element) {
    if (show) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    } else {
        element.innerHTML = '';
    }
}