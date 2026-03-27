// Profile Picture Upload
        const profilePicInput = document.getElementById('profilePicInput');
        const profilePicBox = document.getElementById('profilePicBox');
        const profilePicPreview = document.getElementById('profilePicPreview');
        const removeProfilePic = document.getElementById('removeProfilePic');

        profilePicInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicPreview.src = e.target.result;
                    profilePicBox.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            }
        });

        removeProfilePic.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            profilePicInput.value = '';
            profilePicPreview.src = '';
            profilePicBox.classList.remove('has-image');
        });

        // Cover Picture Upload
        const coverPicInput = document.getElementById('coverPicInput');
        const coverPicBox = document.getElementById('coverPicBox');
        const coverPicPreview = document.getElementById('coverPicPreview');
        const removeCoverPic = document.getElementById('removeCoverPic');

        coverPicInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    coverPicPreview.src = e.target.result;
                    coverPicBox.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            }
        });

        removeCoverPic.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            coverPicInput.value = '';
            coverPicPreview.src = '';
            coverPicBox.classList.remove('has-image');
        });

        // Bio Character Count
        const bioTextarea = document.getElementById('bio');
        const bioCharCount = document.getElementById('bioCharCount');

        bioTextarea.addEventListener('input', function() {
            const count = this.value.length;
            bioCharCount.textContent = `${count}/200`;
            
            if (count > 180) {
                bioCharCount.style.color = 'var(--accent-2)';
            } else if (count > 150) {
                bioCharCount.style.color = 'var(--accent-4)';
            } else {
                bioCharCount.style.color = 'var(--text-muted)';
            }
        });

        // Password Visibility Toggle
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');
        const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
        const confirmPasswordInput = document.getElementById('confirmPassword');

        togglePassword.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });

        toggleConfirmPassword.addEventListener('click', function() {
            const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
            confirmPasswordInput.type = type;
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });

        // Password Strength Checker
        const passwordStrengthBar = document.getElementById('passwordStrengthBar');
        const reqLength = document.getElementById('req-length');
        const reqUppercase = document.getElementById('req-uppercase');
        const reqLowercase = document.getElementById('req-lowercase');
        const reqNumber = document.getElementById('req-number');

        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            // Check length
            if (password.length >= 8) {
                reqLength.classList.add('valid');
                reqLength.classList.remove('invalid');
                strength++;
            } else {
                reqLength.classList.remove('valid');
                reqLength.classList.add('invalid');
            }

            // Check uppercase
            if (/[A-Z]/.test(password)) {
                reqUppercase.classList.add('valid');
                reqUppercase.classList.remove('invalid');
                strength++;
            } else {
                reqUppercase.classList.remove('valid');
                reqUppercase.classList.add('invalid');
            }

            // Check lowercase
            if (/[a-z]/.test(password)) {
                reqLowercase.classList.add('valid');
                reqLowercase.classList.remove('invalid');
                strength++;
            } else {
                reqLowercase.classList.remove('valid');
                reqLowercase.classList.add('invalid');
            }

            // Check number
            if (/[0-9]/.test(password)) {
                reqNumber.classList.add('valid');
                reqNumber.classList.remove('invalid');
                strength++;
            } else {
                reqNumber.classList.remove('valid');
                reqNumber.classList.add('invalid');
            }

            // Update strength bar
            passwordStrengthBar.className = 'password-strength-bar';
            if (strength === 1 || strength === 2) {
                passwordStrengthBar.classList.add('weak');
            } else if (strength === 3) {
                passwordStrengthBar.classList.add('medium');
            } else if (strength === 4) {
                passwordStrengthBar.classList.add('strong');
            }
        });

        // Password Match Validation
        const passwordMatchError = document.getElementById('passwordMatchError');

        confirmPasswordInput.addEventListener('input', function() {
            if (this.value !== passwordInput.value && this.value.length > 0) {
                passwordMatchError.style.display = 'block';
            } else {
                passwordMatchError.style.display = 'none';
            }
        });

   
        
        // Social Login Placeholders
        document.getElementById('googleSignup').addEventListener('click', function() {
            alert('Google sign-up will be integrated in future versions');
        });

        document.getElementById('githubSignup').addEventListener('click', function() {
            alert('GitHub sign-up will be integrated in future versions');
        });

        // Username availability check (simulation)
        const usernameInput = document.getElementById('username');
        const usernameError = document.getElementById('usernameError');
        const takenUsernames = ['admin', 'test', 'user123']; // Simulated taken usernames

        usernameInput.addEventListener('blur', function() {
            const username = this.value.toLowerCase();
            if (takenUsernames.includes(username)) {
                usernameError.style.display = 'block';
                this.style.borderColor = 'var(--accent-2)';
            } else {
                usernameError.style.display = 'none';
                this.style.borderColor = '';
            }
        });