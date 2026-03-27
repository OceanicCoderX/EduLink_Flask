  // Password Visibility Toggle
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');

        togglePassword.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });

        

        // Shake animation for error
        const style = document.createElement('style');
        style.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                75% { transform: translateX(10px); }
            }
        `;
        document.head.appendChild(style);

        // Forgot Password Handler
        const forgotPasswordLink = document.getElementById('forgotPassword');
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            if (!email) {
                alert('Please enter your email address first');
                document.getElementById('email').focus();
                return;
            }
            else{
                window.location.href = "OTPBackend.py?email=" + encodeURIComponent(email);
            }
        });

        // Social Login Placeholders
        document.getElementById('googleLogin').addEventListener('click', function() {
            alert('Google login will be integrated in future versions');
        });

        document.getElementById('githubLogin').addEventListener('click', function() {
            alert('GitHub login will be integrated in future versions');
        });

     

        // Input validation - real-time feedback
        const emailInput = document.getElementById('email');
        emailInput.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.style.borderColor = 'var(--accent-2)';
            } else {
                this.style.borderColor = '';
            }
        });

        emailInput.addEventListener('input', function() {
            this.style.borderColor = '';
        });


        