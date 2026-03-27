// ==========================================
        // GLOBAL STATE
        // ==========================================
        let currentAvatarType = 'initials';
        let currentAvatarData = 'JD';
        let currentBackgroundImage = '';

        // ==========================================
        // INITIALIZATION
        // ==========================================
        // Theme Toggle
        const lightThemeBtn = document.getElementById('lightThemeBtn');
        const darkThemeBtn = document.getElementById('darkThemeBtn');

        lightThemeBtn.addEventListener('click', () => {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('edulink_theme', 'light');
            lightThemeBtn.classList.add('active');
            darkThemeBtn.classList.remove('active');
        });

        darkThemeBtn.addEventListener('click', () => {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('edulink_theme', 'dark');
            darkThemeBtn.classList.add('active');
            lightThemeBtn.classList.remove('active');
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('edulink_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            darkThemeBtn.classList.add('active');
            lightThemeBtn.classList.remove('active');
        }

        // ==========================================
        // PROFILE DATA MANAGEMENT
        // ==========================================
        function loadUserProfile() {
            const savedProfile = localStorage.getItem('edulink_user_profile');
            if (savedProfile) {
                const profile = JSON.parse(savedProfile);
                
                // Update form fields
                document.getElementById('fullName').value = profile.fullName || 'John Doe';
                document.getElementById('username').value = profile.username || 'johndoe';
                document.getElementById('email').value = profile.email || 'john@edulink.com';
                document.getElementById('phone').value = profile.phone || '+91 98765 43210';
                document.getElementById('location').value = profile.location || 'Mumbai, India';
                document.getElementById('birthday').value = profile.birthday || '2000-01-15';
                document.getElementById('bio').value = profile.bio || 'Passionate learner, focused achiever. Studying to make a difference! 🎓';
                
                // Update display
                updateProfileDisplay();
            }
        }

        function saveUserProfile() {
            const profile = {
                fullName: document.getElementById('fullName').value,
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                location: document.getElementById('location').value,
                birthday: document.getElementById('birthday').value,
                bio: document.getElementById('bio').value,
                avatarType: currentAvatarType,
                avatarData: currentAvatarData,
                backgroundImage: currentBackgroundImage
            };
            
            localStorage.setItem('edulink_user_profile', JSON.stringify(profile));
        }

        function updateProfileDisplay() {
            const fullName = document.getElementById('fullName').value;
            const username = document.getElementById('username').value;
            const location = document.getElementById('location').value;
            const bio = document.getElementById('bio').value;
            
            document.getElementById('displayName').textContent = fullName;
            document.getElementById('displayUsername').textContent = '@' + username;
            document.getElementById('displayLocation').textContent = location;
            document.getElementById('displayBio').textContent = bio;
            
            // Update sidebar
            document.querySelector('.profile-name').textContent = fullName;
        }

        // Mobile Sidebar Toggle
        const sidebar = document.getElementById('sidebar');
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 968) {
                if (e.target.closest('.mobile-nav-item')) {
                    sidebar.classList.remove('open');
                }
            }
        });


        // ==========================================
        // FORM HANDLING
        // ==========================================
        function setupFormListeners() {
            // Personal Info Form Submit
            document.getElementById('personalInfoForm').addEventListener('submit', function(e) {
                e.preventDefault();
                saveUserProfile();
                updateProfileDisplay();
                showNotification('Profile updated successfully!', 'success');
            });

            // Bio Character Count
            const bioInput = document.getElementById('bio');
            const charCount = document.getElementById('bioCharCount');
            
            bioInput.addEventListener('input', function() {
                charCount.textContent = this.value.length;
            });

            // Avatar Upload
            document.getElementById('avatarUpload').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;

                if (file.size > 2 * 1024 * 1024) {
                    showNotification('Image size should be less than 2MB', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(event) {
                    const base64 = event.target.result;
                    currentAvatarType = 'image';
                    currentAvatarData = base64;
                    updateAvatarDisplay(base64, 'image');
                    saveUserProfile();
                    closeModal('avatarModal');
                    showNotification('Avatar updated!', 'success');
                };
                reader.readAsDataURL(file);
            });

            // Background Upload
            document.getElementById('backgroundUpload').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;

                if (file.size > 5 * 1024 * 1024) {
                    showNotification('Image size should be less than 5MB', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(event) {
                    const base64 = event.target.result;
                    currentBackgroundImage = base64;
                    document.getElementById('backgroundImage').src = base64;
                    saveUserProfile();
                    showNotification('Background updated!', 'success');
                };
                reader.readAsDataURL(file);
            });
        }

        function cancelEdit() {
            loadUserProfile();
            showNotification('Changes discarded', 'info');
        }

        // ==========================================
        // AVATAR MANAGEMENT
        // ==========================================
        function openAvatarModal() {
            openModal('avatarModal');
        }

        function selectAvatar(element, gradientId) {
            document.querySelectorAll('.avatar-option').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            
            const gradient = element.style.background;
            currentAvatarType = 'gradient';
            currentAvatarData = gradient;
            
            updateAvatarDisplay(gradient, 'gradient');
            saveUserProfile();
            
            setTimeout(() => {
                closeModal('avatarModal');
                showNotification('Avatar updated!', 'success');
            }, 500);
        }

        function updateAvatarDisplay(data, type) {
            const mainAvatar = document.getElementById('mainAvatar');
            const sidebarAvatar = document.getElementById('sidebarAvatar');
            
            if (type === 'image') {
                mainAvatar.style.backgroundImage = `url(${data})`;
                mainAvatar.style.backgroundSize = 'cover';
                mainAvatar.textContent = '';
                
                sidebarAvatar.style.backgroundImage = `url(${data})`;
                sidebarAvatar.style.backgroundSize = 'cover';
                sidebarAvatar.textContent = '';
            } else if (type === 'gradient') {
                mainAvatar.style.background = data;
                mainAvatar.textContent = getInitials(document.getElementById('fullName').value);
                
                sidebarAvatar.style.background = data;
                sidebarAvatar.textContent = getInitials(document.getElementById('fullName').value);
            }
        }

        function getInitials(name) {
            return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
        }

        function changeBackground() {
            document.getElementById('backgroundUpload').click();
        }

        // ==========================================
        // ACHIEVEMENTS
        // ==========================================
        function checkAndUnlockAchievements() {
            // Get stats from localStorage
            const pomodoroSessions = localStorage.getItem('edulink_pomodoro_sessions') || 0;
            const tasks = JSON.parse(localStorage.getItem('edulink_tasks') || '[]');
            const notes = JSON.parse(localStorage.getItem('edulink_notes') || '[]');
            
            const tasksCompleted = tasks.filter(t => t.completed).length;
            const notesCreated = notes.length;
            
            // Auto-unlock achievements based on dummy data
            const achievements = {
                first_note: notesCreated >= 1,
                ten_notes: notesCreated >= 10,
                hundred_tasks: tasksCompleted >= 100,
                seven_day_streak: true, // Dummy
                fifty_hours: true // Dummy
            };
            
            localStorage.setItem('edulink_achievements', JSON.stringify(achievements));
        }

        // ==========================================
        // EXPORT FUNCTIONS
        // ==========================================
        function openExportModal() {
            openModal('exportModal');
        }

        function exportAsImage() {
            const element = document.getElementById('profileContent');
            
            showNotification('Generating image...', 'info');
            
            html2canvas(element, {
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-secondary'),
                scale: 2
            }).then(canvas => {
                const link = document.createElement('a');
                link.download = `EduLink_Profile_${Date.now()}.png`;
                link.href = canvas.toDataURL();
                link.click();
                
                closeModal('exportModal');
                showNotification('Profile exported as image!', 'success');
            });
        }

        function exportAsPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            const fullName = document.getElementById('fullName').value;
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const bio = document.getElementById('bio').value;
            
            // Add content
            doc.setFontSize(20);
            doc.setFont(undefined, 'bold');
            doc.text('EduLink Profile', 20, 20);
            
            doc.setFontSize(16);
            doc.text(fullName, 20, 35);
            
            doc.setFontSize(12);
            doc.setFont(undefined, 'normal');
            doc.text(`@${username}`, 20, 45);
            doc.text(email, 20, 55);
            
            doc.setFontSize(10);
            doc.text('Bio:', 20, 70);
            const splitBio = doc.splitTextToSize(bio, 170);
            doc.text(splitBio, 20, 78);
            
            doc.text('Statistics:', 20, 100);
            doc.text('Total Focus Time: 156h 24m', 20, 108);
            doc.text('Pomodoro Sessions: 89', 20, 116);
            doc.text('Tasks Completed: 145', 20, 124);
            doc.text('Current Streak: 12 Days', 20, 132);
            
            doc.save(`EduLink_Profile_${fullName.replace(/\s+/g, '_')}.pdf`);
            
            closeModal('exportModal');
            showNotification('Profile exported as PDF!', 'success');
        }

        function exportAsJSON() {
            const profileData = {
                fullName: document.getElementById('fullName').value,
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                location: document.getElementById('location').value,
                birthday: document.getElementById('birthday').value,
                bio: document.getElementById('bio').value,
                stats: {
                    focusTime: '156h 24m',
                    pomodoroSessions: 89,
                    tasksCompleted: 145,
                    currentStreak: 12
                },
                achievements: JSON.parse(localStorage.getItem('edulink_achievements') || '{}'),
                exportDate: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(profileData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `EduLink_Data_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            closeModal('exportModal');
            showNotification('Data exported as JSON!', 'success');
        }

        // ==========================================
        // SOCIAL FEATURES
        // ==========================================
        function shareProfile() {
            const username = document.getElementById('username').value;
            const profileUrl = `https://edulink.com/u/${username}`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'My EduLink Profile',
                    text: 'Check out my EduLink profile!',
                    url: profileUrl
                }).catch(() => {
                    copyToClipboard(profileUrl);
                });
            } else {
                copyToClipboard(profileUrl);
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Profile link copied to clipboard!', 'success');
            }).catch(() => {
                showNotification('Failed to copy link', 'error');
            });
        }

        // ==========================================
        // SETTINGS
        // ==========================================
        function toggleSetting(element) {
            element.classList.toggle('active');
            showNotification('Setting updated', 'success');
        }

        function changePassword() {
            const newPassword = prompt('Enter new password:');
            if (newPassword && newPassword.length >= 8) {
                showNotification('Password changed successfully!', 'success');
            } else if (newPassword) {
                showNotification('Password must be at least 8 characters', 'error');
            }
        }

        // ==========================================
        // UTILITY FUNCTIONS
        // ==========================================
        function scrollToEdit() {
            document.getElementById('personalInfoForm').scrollIntoView({ behavior: 'smooth' });
        }

        function openModal(modalId) {
            document.getElementById(modalId).classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        function showNotification(message, type = 'info') {
            const colors = {
                success: 'linear-gradient(135deg, var(--accent-3), #26b89e)',
                error: 'linear-gradient(135deg, var(--accent-2), #e63946)',
                warning: 'linear-gradient(135deg, var(--accent-4), #ff7043)',
                info: 'linear-gradient(135deg, var(--primary), var(--accent-1))'
            };

            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${colors[type]};
                color: white;
                padding: 16px 24px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                z-index: 10001;
                animation: slideIn 0.3s ease;
                font-weight: 500;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        // Animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        // Close modals on outside click
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    this.classList.remove('active');
                }
            });
        });

        // Settings button
        document.getElementById('settingsBtn').addEventListener('click', () => {
            alert('Settings panel will be integrated soon!');
        });