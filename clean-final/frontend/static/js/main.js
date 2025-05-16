/**
 * Main JavaScript for Pocket AI Frontend
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle 
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Check if backend is available
    checkBackendStatus();
    
    // Set up any global event listeners
    setupFormValidation();
});

/**
 * Check if the backend API is available
 */
function checkBackendStatus() {
    const statusIndicator = document.getElementById('api-status-indicator');
    
    if (!statusIndicator) return;
    
    fetch('/api/health')
        .then(response => {
            if (response.ok) {
                statusIndicator.classList.add('bg-green-500');
                statusIndicator.classList.remove('bg-red-500');
                statusIndicator.title = 'API is online';
            } else {
                statusIndicator.classList.add('bg-red-500');
                statusIndicator.classList.remove('bg-green-500');
                statusIndicator.title = 'API is offline';
            }
        })
        .catch(() => {
            statusIndicator.classList.add('bg-red-500');
            statusIndicator.classList.remove('bg-green-500');
            statusIndicator.title = 'API is offline';
        });
}

/**
 * Set up common form validation
 */
function setupFormValidation() {
    // Add form validation for all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                
                // Highlight invalid fields
                form.querySelectorAll('input, textarea, select').forEach(input => {
                    if (!input.validity.valid) {
                        input.classList.add('border-red-500');
                        
                        // Add error message if not present
                        const errorId = `error-${input.id}`;
                        if (!document.getElementById(errorId)) {
                            const errorMsg = document.createElement('p');
                            errorMsg.id = errorId;
                            errorMsg.className = 'text-red-500 text-xs mt-1';
                            errorMsg.textContent = input.validationMessage;
                            input.parentNode.appendChild(errorMsg);
                        }
                    } else {
                        input.classList.remove('border-red-500');
                        
                        // Remove error message if present
                        const errorEl = document.getElementById(`error-${input.id}`);
                        if (errorEl) errorEl.remove();
                    }
                });
            }
        });
        
        // Clear validation styling on input
        form.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('input', function() {
                if (input.validity.valid) {
                    input.classList.remove('border-red-500');
                    
                    const errorEl = document.getElementById(`error-${input.id}`);
                    if (errorEl) errorEl.remove();
                }
            });
        });
    });
} 