document.addEventListener('DOMContentLoaded', () => {
    const signupButton = document.getElementById('signup-button');
    const loginButton = document.getElementById('login-button');
    const deleteButton = document.getElementById('delete-button');
    const message = document.getElementById('message');
    const deleteForm = document.getElementById('delete-form');

    signupButton.addEventListener('click', async () => {
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        message.textContent = result.message || result.error;
    });

    loginButton.addEventListener('click', async () => {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        if (response.ok) {
            message.textContent = result.message;
            deleteForm.style.display = 'block';
        } else {
            message.textContent = result.error;
        }
    });

    deleteButton.addEventListener('click', async () => {
        const username = document.getElementById('delete-username').value;
        const password = document.getElementById('delete-password').value;

        const response = await fetch('/delete_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        message.textContent = result.message || result.error;
        if (response.ok) {
            deleteForm.style.display = 'none';
        }
    });
});
