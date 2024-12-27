document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const toggleButtons = document.querySelectorAll('.toggle-button');
    const forms = document.querySelectorAll('#signup-form, #login-form');
    const signupButton = document.getElementById('signup-button');
    const loginButton = document.getElementById('login-button');
    const message = document.getElementById('message');

    // Handle form toggle
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update button states
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Show corresponding form
            const formToShow = button.getAttribute('data-form');
            forms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${formToShow}-form`) {
                    form.classList.add('active');
                }
            });

            // Clear message and form fields
            message.textContent = '';
            document.querySelectorAll('input').forEach(input => input.value = '');
        });
    });

    // Handle form submission
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

    // Add input animation effects
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });
    });

    // Signup event listener
    signupButton.addEventListener('click', async () => {
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        if (!username || !password) {
            message.textContent = 'Please fill in all fields';
            message.style.color = '#dc3545';
            return;
        }

        signupButton.disabled = true;
        signupButton.textContent = 'Creating Account...';

        const result = await handleRequest('/signup', { username, password });
        
        signupButton.disabled = false;
        signupButton.textContent = 'Create Account';

        message.textContent = result.message || result.error;
        message.style.color = result.error ? '#dc3545' : '#28a745';

        if (!result.error) {
            setTimeout(() => {
                document.querySelector('[data-form="login"]').click();
            }, 1500);
        }
    });

    // Login event listener
    loginButton.addEventListener('click', async () => {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            message.textContent = 'Please fill in all fields';
            message.style.color = '#dc3545';
            return;
        }

        loginButton.disabled = true;
        loginButton.textContent = 'Logging in...';

        const result = await handleRequest('/login', { username, password });
        
        loginButton.disabled = false;
        loginButton.textContent = 'Login';

        message.textContent = result.message || result.error;
        message.style.color = result.error ? '#dc3545' : '#28a745';

        if (!result.error) {
            // Handle successful login (e.g., redirect)
            // window.location.href = '/dashboard';
        }
    });
});