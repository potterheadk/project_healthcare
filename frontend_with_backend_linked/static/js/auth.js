// Static/js/auth.js

document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const signupToggle = document.getElementById('signup-toggle');
    const loginToggle = document.getElementById('login-toggle');
    const toggleFormLink = document.getElementById('toggle-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    // Generic message handling function
    const showMessage = (message, isError = false) => {
        const messageElement = isError ? errorMessage : successMessage;
        const otherElement = isError ? successMessage : errorMessage;
        
        messageElement.textContent = message;
        messageElement.classList.remove('hidden');
        otherElement.classList.add('hidden');
        setTimeout(() => messageElement.classList.add('hidden'), 5000);
    };

    // Handle API requests
    const handleRequest = async (url, data) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            return { error: 'An error occurred. Please try again.' };
        }
    };

    // Toggle form visibility functions
    const showSignup = () => {
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        signupToggle.classList.add('bg-orange-500', 'text-white');
        loginToggle.classList.remove('bg-orange-500', 'text-white');
        // Clear messages and form fields
        errorMessage.classList.add('hidden');
        successMessage.classList.add('hidden');
        document.querySelectorAll('input').forEach(input => input.value = '');
    };

    const showLogin = () => {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        loginToggle.classList.add('bg-orange-500', 'text-white');
        signupToggle.classList.remove('bg-orange-500', 'text-white');
        // Clear messages and form fields
        errorMessage.classList.add('hidden');
        successMessage.classList.add('hidden');
        document.querySelectorAll('input').forEach(input => input.value = '');
    };

    // Add input animation effects
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('ring-2', 'ring-orange-500');
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('ring-2', 'ring-orange-500');
            }
        });
    });

    // Event listeners for toggling forms
    signupToggle.addEventListener('click', showSignup);
    loginToggle.addEventListener('click', showLogin);
    toggleFormLink.addEventListener('click', showSignup);

    // Handle signup form submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        if (!username || !password) {
            showMessage('Please fill in all fields', true);
            return;
        }

        const submitButton = signupForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Creating Account...';

        const result = await handleRequest('/signup', { username, password });
        
        submitButton.disabled = false;
        submitButton.textContent = originalText;

        if (result.error) {
            showMessage(result.error, true);
        } else {
            showMessage(result.message || 'Account created successfully!');
            setTimeout(() => {
                showLogin();
            }, 1500);
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            showMessage('Please fill in all fields', true);
            return;
        }

        const submitButton = loginForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';

        const result = await handleRequest('/login', { username, password });
        
        submitButton.disabled = false;
        submitButton.textContent = originalText;

        if (result.error) {
            showMessage(result.error, true);
        } else {
            showMessage('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        }
    });

    // Show login form by default
    showLogin();
});



















