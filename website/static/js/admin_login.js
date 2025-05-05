// admin-script.js - For admin login page
document.addEventListener('DOMContentLoaded', function() {
    const adminLoginForm = document.getElementById('admin-login-form');
    const adminUsername = document.getElementById('admin-username');
    const adminPassword = document.getElementById('admin-password');
    const togglePassword = document.querySelector('.toggle-password');
    const loginAlert = document.getElementById('login-alert');

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = adminPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            adminPassword.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    // Form submission
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function(e) {
            // Basic validation
            if (!adminUsername.value.trim() || !adminPassword.value.trim()) {
                e.preventDefault();
                showAlert('Please enter both username and password.', 'error');
                return;
            }

            // Optionally disable the button here if desired
            const loginBtn = document.querySelector('.login-btn');
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
            // Allow the form to submit normally
        });
    }

    // Show alert message
    function showAlert(message, type) {
        if (loginAlert) {
            loginAlert.textContent = message;
            loginAlert.className = 'login-alert';
            loginAlert.classList.add(type);

            // Automatically hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    loginAlert.style.display = 'none';
                }, 5000);
            }
        }
    }

    // Add focus/blur effects for inputs
    document.querySelectorAll('.input-field input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
        });
        input.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = 'none';
        });
    });
});

// admin-dashboard.js - For admin dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar menu toggle for mobile
    const menuItems = document.querySelectorAll('.sidebar .menu li');

    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all menu items
            menuItems.forEach(mi => mi.classList.remove('active'));

            // Add active class to clicked item
            this.classList.add('active');
        });
    });

    // Notification dropdown toggle
    const notificationIcon = document.querySelector('.notification');
    if (notificationIcon) {
        notificationIcon.addEventListener('click', function() {
            // Toggle notification dropdown
            // This would be implemented with actual dropdown HTML
            console.log('Notification clicked');
        });
    }

    // Admin profile dropdown toggle
    const adminProfile = document.querySelector('.admin-profile');
    if (adminProfile) {
        adminProfile.addEventListener('click', function() {
            // Toggle profile dropdown
            // This would be implemented with actual dropdown HTML
            console.log('Admin profile clicked');
        });
    }

    // Time range change for charts
    const timeRange = document.getElementById('time-range');
    if (timeRange) {
        timeRange.addEventListener('change', function() {
            // Update chart data based on selected time range
            updateChartData(this.value);
        });
    }

    // Handle intervention buttons
    const interventionBtns = document.querySelectorAll('.intervention-btn');
    interventionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // In a real implementation, this would open a modal with intervention options
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name').textContent;
            alert(`Preparing intervention options for ${userName}`);
        });
    });

    // Mock function for updating chart data
    function updateChartData(timeRange) {
        console.log(`Updating chart data for time range: ${timeRange}`);
        // In a real implementation, this would make an API call and update the chart
    }

    // Mock function for initializing charts
    function initializeCharts() {
        // In a real implementation, this would use a charting library like Chart.js
        console.log('Charts initialized');
    }

    // Initialize charts on page load
    initializeCharts();
});