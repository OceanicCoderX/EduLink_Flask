// Load user profile
        window.addEventListener('load', () => {
            const userData = JSON.parse(localStorage.getItem('edulink_user'));
            if (userData) {
                document.getElementById('profileName').textContent = userData.fullName || 'Student';
                document.getElementById('profileEmail').textContent = userData.email || 'student@edulink.com';
                document.getElementById('profileAvatar').textContent = (userData.fullName || 'S')[0].toUpperCase();
            }
        });

        // Mobile Sidebar Toggle
        const sidebar = document.getElementById('sidebar');
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 968) {
                if (e.target.closest('.mobile-nav-item')) {
                    sidebar.classList.remove('open');
                }
            }
        });


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

        // Create Post
        document.getElementById('createPostBtn').addEventListener('click', function() {
            const postInput = document.getElementById('createPostInput');
            const content = postInput.value.trim();

            if (!content) {
                alert('Please write something to post!');
                return;
            }

            const feedPosts = document.getElementById('feedPosts');
            const newPost = document.createElement('div');
            newPost.className = 'post-card';
            newPost.innerHTML = `
                <div class="post-header">
                    <div class="post-avatar">K</div>
                    <div class="post-user-info">
                        <div class="post-username">Khushi (You)</div>
                        <div class="post-time">Just now</div>
                    </div>
                </div>
                <div class="post-content">${content}</div>
                <div class="post-actions">
                    <button class="post-action-btn">
                        <i class="far fa-heart"></i>
                        <span>0</span>
                    </button>
                    <button class="post-action-btn">
                        <i class="far fa-comment"></i>
                        <span>0</span>
                    </button>
                    <button class="post-action-btn">
                        <i class="fas fa-share"></i>
                        <span>0</span>
                    </button>
                </div>
            `;

            feedPosts.insertBefore(newPost, feedPosts.firstChild);
            postInput.value = '';
        });

        // Feed Filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                // Filter logic can be added here
            });
        });

        // Like Button
        document.addEventListener('click', function(e) {
            if (e.target.closest('.post-action-btn') && e.target.closest('.post-action-btn').querySelector('.fa-heart')) {
                const btn = e.target.closest('.post-action-btn');
                const icon = btn.querySelector('i');
                const count = btn.querySelector('span');
                
                if (icon.classList.contains('far')) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    btn.classList.add('liked');
                    count.textContent = parseInt(count.textContent) + 1;
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    btn.classList.remove('liked');
                    count.textContent = parseInt(count.textContent) - 1;
                }
            }
        });

        // Add Friend
        document.getElementById('addFriendBtn').addEventListener('click', function() {
            alert('Add friend feature coming soon!');
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => {
            alert('Settings panel will be integrated soon!');
        });