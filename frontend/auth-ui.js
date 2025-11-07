// Authentication UI Handler Functions

let pendingVerificationEmail = '';
let pendingResetEmail = '';

// Show/Hide different forms
function showSignInForm() {
    document.getElementById('signin-form').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verification-form').style.display = 'none';
    document.getElementById('forgot-password-form').style.display = 'none';
    document.getElementById('reset-password-form').style.display = 'none';
    clearAllMessages();
}

function showSignUpForm() {
    document.getElementById('signin-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('verification-form').style.display = 'none';
    document.getElementById('forgot-password-form').style.display = 'none';
    document.getElementById('reset-password-form').style.display = 'none';
    clearAllMessages();
}

function showVerificationForm() {
    document.getElementById('signin-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verification-form').style.display = 'block';
    document.getElementById('forgot-password-form').style.display = 'none';
    document.getElementById('reset-password-form').style.display = 'none';
    clearAllMessages();
}

function showForgotPasswordForm() {
    document.getElementById('signin-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verification-form').style.display = 'none';
    document.getElementById('forgot-password-form').style.display = 'block';
    document.getElementById('reset-password-form').style.display = 'none';
    clearAllMessages();
}

function showResetPasswordForm() {
    document.getElementById('signin-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verification-form').style.display = 'none';
    document.getElementById('forgot-password-form').style.display = 'none';
    document.getElementById('reset-password-form').style.display = 'block';
    clearAllMessages();
}

// Clear all messages
function clearAllMessages() {
    document.getElementById('signin-message').textContent = '';
    document.getElementById('signup-message').textContent = '';
    document.getElementById('verification-message').textContent = '';
    document.getElementById('forgot-message').textContent = '';
    document.getElementById('reset-message').textContent = '';
}

// Show message
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.color = isError ? '#ef4444' : '#10b981';
}

// Handle Sign In
async function handleSignIn() {
    const email = document.getElementById('signin-email').value.trim();
    const password = document.getElementById('signin-password').value;

    if (!email || !password) {
        showMessage('signin-message', 'Please enter email and password', true);
        return;
    }

    showMessage('signin-message', 'Signing in...');

    try {
        await authManager.signIn(email, password);
        showMessage('signin-message', 'Sign in successful!');
    } catch (error) {
        console.error('Sign in error:', error);
        if (error.code === 'UserNotConfirmedException') {
            pendingVerificationEmail = email;
            showMessage('signin-message', 'Please verify your email first', true);
            setTimeout(() => showVerificationForm(), 2000);
        } else {
            showMessage('signin-message', error.message || 'Sign in failed', true);
        }
    }
}

// Handle Sign Up
async function handleSignUp() {
    const username = document.getElementById('signup-username').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    if (!username || !email || !password || !confirmPassword) {
        showMessage('signup-message', 'Please fill in all fields', true);
        return;
    }

    if (username.length < 3 || username.length > 20) {
        showMessage('signup-message', 'Username must be 3-20 characters', true);
        return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showMessage('signup-message', 'Username can only contain letters, numbers, and underscores', true);
        return;
    }

    if (password !== confirmPassword) {
        showMessage('signup-message', 'Passwords do not match', true);
        return;
    }

    if (password.length < 8) {
        showMessage('signup-message', 'Password must be at least 8 characters', true);
        return;
    }

    showMessage('signup-message', 'Creating account...');

    try {
        await authManager.signUp(email, password, username);
        pendingVerificationEmail = email;
        showMessage('signup-message', 'Account created! Check your email for verification code.');
        setTimeout(() => showVerificationForm(), 2000);
    } catch (error) {
        console.error('Sign up error:', error);
        showMessage('signup-message', error.message || 'Sign up failed', true);
    }
}

// Handle Verification
async function handleVerification() {
    const code = document.getElementById('verification-code').value.trim();

    if (!code) {
        showMessage('verification-message', 'Please enter verification code', true);
        return;
    }

    if (!pendingVerificationEmail) {
        showMessage('verification-message', 'No pending verification. Please sign up first.', true);
        return;
    }

    showMessage('verification-message', 'Verifying...');

    try {
        await authManager.confirmSignUp(pendingVerificationEmail, code);
        showMessage('verification-message', 'Email verified! You can now sign in.');
        setTimeout(() => {
            document.getElementById('signin-email').value = pendingVerificationEmail;
            showSignInForm();
            pendingVerificationEmail = '';
        }, 2000);
    } catch (error) {
        console.error('Verification error:', error);
        showMessage('verification-message', error.message || 'Verification failed', true);
    }
}

// Resend Verification Code
async function resendVerificationCode() {
    if (!pendingVerificationEmail) {
        showMessage('verification-message', 'No pending verification', true);
        return;
    }

    showMessage('verification-message', 'Resending code...');

    try {
        await authManager.resendConfirmationCode(pendingVerificationEmail);
        showMessage('verification-message', 'Verification code sent to ' + pendingVerificationEmail);
    } catch (error) {
        console.error('Resend error:', error);
        showMessage('verification-message', error.message || 'Failed to resend code', true);
    }
}

// Handle Forgot Password
async function handleForgotPassword() {
    const email = document.getElementById('forgot-email').value.trim();

    if (!email) {
        showMessage('forgot-message', 'Please enter your email', true);
        return;
    }

    showMessage('forgot-message', 'Sending reset code...');

    try {
        await authManager.forgotPassword(email);
        pendingResetEmail = email;
        showMessage('forgot-message', 'Reset code sent to ' + email);
        setTimeout(() => showResetPasswordForm(), 2000);
    } catch (error) {
        console.error('Forgot password error:', error);
        showMessage('forgot-message', error.message || 'Failed to send reset code', true);
    }
}

// Handle Reset Password
async function handleResetPassword() {
    const code = document.getElementById('reset-code').value.trim();
    const password = document.getElementById('reset-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;

    if (!code || !password || !confirmPassword) {
        showMessage('reset-message', 'Please fill in all fields', true);
        return;
    }

    if (password !== confirmPassword) {
        showMessage('reset-message', 'Passwords do not match', true);
        return;
    }

    if (password.length < 8) {
        showMessage('reset-message', 'Password must be at least 8 characters', true);
        return;
    }

    if (!pendingResetEmail) {
        showMessage('reset-message', 'No pending reset. Please request a reset code first.', true);
        return;
    }

    showMessage('reset-message', 'Resetting password...');

    try {
        await authManager.confirmPassword(pendingResetEmail, code, password);
        showMessage('reset-message', 'Password reset successful! You can now sign in.');
        setTimeout(() => {
            document.getElementById('signin-email').value = pendingResetEmail;
            showSignInForm();
            pendingResetEmail = '';
        }, 2000);
    } catch (error) {
        console.error('Reset password error:', error);
        showMessage('reset-message', error.message || 'Password reset failed', true);
    }
}

// Handle Enter key press
document.addEventListener('DOMContentLoaded', function() {
    // Sign In form
    document.getElementById('signin-email')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleSignIn();
    });
    document.getElementById('signin-password')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleSignIn();
    });

    // Sign Up form
    document.getElementById('signup-confirm-password')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleSignUp();
    });

    // Verification form
    document.getElementById('verification-code')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleVerification();
    });

    // Forgot password form
    document.getElementById('forgot-email')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleForgotPassword();
    });

    // Reset password form
    document.getElementById('reset-confirm-password')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleResetPassword();
    });

    // Initialize auth manager
    if (authManager) {
        authManager.initialize();
    }
});
