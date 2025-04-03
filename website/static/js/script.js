document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const user_name = document.getElementById('name');
    const user_id = document.getElementById('user_id');
    const togglePassword = document.querySelector('.toggle-password');
    const loginAlert = document.getElementById('login-alert');

    // Toggle password visibility
    togglePassword.addEventListener('click', function() {
        const type = user_id.getAttribute('type') === 'password' ? 'text' : 'password';
        user_id.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });

    // Form submission without intercepting navigation
    loginForm.addEventListener('submit', function(e) {
        // Basic validation
        if (!user_id.value.trim() || !user_name.value.trim()) {
            e.preventDefault();
            showAlert('Please enter both email and password.', 'error');
            return;
        }

        // const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        // if (!emailPattern.test(emailInput.value.trim())) {
        //     e.preventDefault();
        //     showAlert('Please enter a valid email address.', 'error');
        //     return;
        // }
        // Optionally disable the button here if desired
        const loginBtn = document.querySelector('.login-btn');
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
        // Allow the form to submit normally.
    });

    // Show alert message
    function showAlert(message, type) {
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

    // Add focus/blur effects for inputs
    document.querySelectorAll('.input-field input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
        });
        input.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = 'none';
        });
    });

    // Detect browser autofill and apply styles
    setTimeout(() => {
        const autofilled = document.querySelectorAll('input:-webkit-autofill');
        autofilled.forEach(input => {
            input.parentElement.classList.add('autofilled');
        });
    }, 500);
});
