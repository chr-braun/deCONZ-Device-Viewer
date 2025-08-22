// deCONZ Device Viewer JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('deCONZ Device Viewer loaded');
    
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Add loading states
    addLoadingStates();
    
    // Auto-refresh functionality (can be enabled later)
    // setInterval(refreshDevices, 30000); // Refresh every 30 seconds
    
    // Add device card interactions
    addDeviceCardInteractions();
}

function addLoadingStates() {
    // Add loading indicators for async operations
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.dataset.async === 'true') {
                this.innerHTML = '<span class="loading"></span> Loading...';
                this.disabled = true;
            }
        });
    });
}

function addDeviceCardInteractions() {
    const deviceCards = document.querySelectorAll('.device-card');
    
    deviceCards.forEach(card => {
        // Add click-to-expand functionality (for future use)
        card.addEventListener('click', function() {
            console.log('Device card clicked:', this);
            // Could expand to show more device details
        });
        
        // Add keyboard navigation support
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

// Future: Real-time updates with WebSocket or Server-Sent Events
function refreshDevices() {
    fetch('/api/devices')
        .then(response => response.json())
        .then(data => {
            console.log('Devices refreshed:', data);
            // Update the device display
        })
        .catch(error => {
            console.error('Error refreshing devices:', error);
        });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `<strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}`;
    
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Export functions for testing
window.deconzViewer = {
    refreshDevices,
    showAlert,
    formatDateTime
};