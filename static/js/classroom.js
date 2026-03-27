// Global Variables
        let myRooms = JSON.parse(localStorage.getItem('edulink_my_rooms')) || [];
        let joinedRooms = JSON.parse(localStorage.getItem('edulink_joined_rooms')) || [];
        let invitations = JSON.parse(localStorage.getItem('edulink_invitations')) || [];
        let currentUser = JSON.parse(localStorage.getItem('edulink_user')) || { fullName: 'Khushi', email: 'khushi@edulink.com' };
        let currentRoomTab = 'active';

        // DOM Elements
        const sidebar = document.getElementById('sidebar');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const createRoomModal = document.getElementById('createRoomModal');
        const createRoomBtn = document.getElementById('createRoomBtn');
        const closeModalBtn = document.getElementById('closeModalBtn');
        const cancelCreateBtn = document.getElementById('cancelCreateBtn');
        const saveRoomBtn = document.getElementById('saveRoomBtn');
        const passwordProtectedCheckbox = document.getElementById('passwordProtected');
        const roomPasswordInput = document.getElementById('roomPassword');

        // Mobile Sidebar Toggle
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 968) {
                if (e.target.closest('.mobile-nav-item')) {
                    sidebar.classList.remove('open');
                }
            }
        });


        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializeTheme();
            updateCurrentDate();
            loadUserProfile();
            updateStats();
            renderMyRooms();
            renderJoinedRooms();
            renderInvitations();
            renderInviteLinks();
            initializeEventListeners();
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



        function updateCurrentDate() {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const currentDateEl = document.getElementById('currentDate');
            if (currentDateEl) {
                currentDateEl.textContent = new Date().toLocaleDateString('en-US', options);
            }
        }

        function loadUserProfile() {
            document.getElementById('profileName').textContent = currentUser.fullName || 'Student';
            document.getElementById('profileEmail').textContent = currentUser.email || 'student@edulink.com';
            document.getElementById('profileAvatar').textContent = (currentUser.fullName || 'S')[0].toUpperCase();
        }

        

        function initializeEventListeners() {
            // Mobile Menu
            mobileMenuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });

            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 968) {
                    if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                        sidebar.classList.remove('open');
                    }
                }
            });

            // Modal Controls
            createRoomBtn.addEventListener('click', openCreateRoomModal);
            closeModalBtn.addEventListener('click', closeCreateRoomModal);
            cancelCreateBtn.addEventListener('click', closeCreateRoomModal);
            saveRoomBtn.addEventListener('click', createRoom);

            // Password Toggle
            passwordProtectedCheckbox.addEventListener('change', function() {
                roomPasswordInput.style.display = this.checked ? 'block' : 'none';
                if (!this.checked) roomPasswordInput.value = '';
            });

            // Room Tabs
            document.querySelectorAll('.room-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.room-tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    currentRoomTab = this.dataset.tab;
                    renderMyRooms();
                });
            });

            // Settings
            document.getElementById('settingsBtn').addEventListener('click', () => {
                alert('Settings will be available soon!');
            });
        }

        function openCreateRoomModal() {
            createRoomModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }

        function closeCreateRoomModal() {
            createRoomModal.classList.remove('show');
            document.body.style.overflow = 'auto';
            document.getElementById('createRoomForm').reset();
            roomPasswordInput.style.display = 'none';
        }

        function generateRoomCode() {
            return Math.random().toString(36).substring(2, 8).toUpperCase();
        }

        function createRoom() {
            const name = document.getElementById('roomName').value.trim();
            const topic = document.getElementById('roomTopic').value.trim();
            const subject = document.getElementById('roomSubject').value;
            const description = document.getElementById('roomDescription').value.trim();
            const isPasswordProtected = passwordProtectedCheckbox.checked;
            const password = isPasswordProtected ? roomPasswordInput.value : null;
            const date = document.getElementById('roomDate').value;
            const time = document.getElementById('roomTime').value;
            const isPublic = document.getElementById('publicRoom').checked;

            if (!name || !topic) {
                alert('Please fill in all required fields!');
                return;
            }

            if (isPasswordProtected && !password) {
                alert('Please enter a password!');
                return;
            }

            const room = {
                id: 'room_' + Date.now(),
                name,
                topic,
                subject,
                description,
                host: currentUser.fullName,
                hostId: 'user_' + currentUser.fullName.toLowerCase(),
                password,
                isPasswordProtected,
                isPublic,
                participants: [currentUser.fullName],
                participantCount: 1,
                status: date && time ? 'scheduled' : 'active',
                scheduledDate: date || null,
                scheduledTime: time || null,
                createdAt: new Date().toISOString(),
                roomCode: generateRoomCode()
            };

            myRooms.push(room);
            saveData();
            renderMyRooms();
            renderInviteLinks();
            updateStats();
            closeCreateRoomModal();
            showNotification('Room created successfully!');
        }

        function updateStats() {
            const totalCreated = myRooms.length;
            const totalJoined = joinedRooms.length;
            const activeNow = myRooms.filter(r => r.status === 'active').length + 
                             joinedRooms.filter(r => r.status === 'active').length;
            
            // Calculate total hours (placeholder - would need tracking)
            const totalHours = Math.floor(Math.random() * 100); // Placeholder

            document.getElementById('totalCreated').textContent = totalCreated;
            document.getElementById('totalJoined').textContent = totalJoined;
            document.getElementById('activeNow').textContent = activeNow;
            document.getElementById('totalHours').textContent = totalHours + 'h';
        }

        function renderMyRooms() {
            const container = document.getElementById('myRoomsList');
            let filteredRooms = myRooms;

            if (currentRoomTab === 'active') {
                filteredRooms = myRooms.filter(r => r.status === 'active');
            } else if (currentRoomTab === 'scheduled') {
                filteredRooms = myRooms.filter(r => r.status === 'scheduled');
            } else if (currentRoomTab === 'past') {
                filteredRooms = myRooms.filter(r => r.status === 'ended');
            }

            if (filteredRooms.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-door-closed"></i></div>
                        <div class="empty-text">No ${currentRoomTab} rooms</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = filteredRooms.map(room => `
                <div class="room-card ${room.status}">
                    <div class="room-header">
                        <div class="room-info">
                            <div class="room-name">
                                ${room.name} ${room.isPasswordProtected ? '<i class="fas fa-lock" style="font-size: 14px; color: var(--accent-4);"></i>' : ''}
                            </div>
                            <div class="room-topic">${room.topic}</div>
                            <div class="room-meta">
                                <span class="room-badge">
                                    <i class="fas fa-users"></i> ${room.participantCount}
                                </span>
                                <span class="room-badge">
                                    <i class="fas fa-book"></i> ${room.subject}
                                </span>
                                <span class="status-badge status-${room.status}">
                                    ${room.status === 'active' ? '🟢' : room.status === 'scheduled' ? '🟡' : '⚪'} ${room.status}
                                </span>
                                ${room.scheduledDate ? `
                                    <span class="room-badge">
                                        <i class="fas fa-calendar"></i> ${room.scheduledDate} ${room.scheduledTime}
                                    </span>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="room-actions">
                        ${room.status !== 'ended' ? `
                            <button class="room-btn btn-join" onclick="joinRoom('${room.id}')">
                                <i class="fas fa-sign-in-alt"></i> Join Room
                            </button>
                        ` : ''}
                        <button class="room-btn btn-secondary" onclick="editRoom('${room.id}')">
                            <i class="fas fa-cog"></i>
                        </button>
                        <button class="room-btn btn-delete" onclick="deleteRoom('${room.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function renderJoinedRooms() {
            const container = document.getElementById('joinedRoomsList');
            
            if (joinedRooms.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-users-slash"></i></div>
                        <div class="empty-text">You haven't joined any rooms yet</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = joinedRooms.map(room => `
                <div class="room-card ${room.status}">
                    <div class="room-header">
                        <div class="room-info">
                            <div class="room-name">${room.name}</div>
                            <div class="room-topic">Host: ${room.host}</div>
                            <div class="room-meta">
                                <span class="room-badge">
                                    <i class="fas fa-users"></i> ${room.participantCount}
                                </span>
                                <span class="status-badge status-${room.status}">
                                    ${room.status === 'active' ? '🟢' : '⚪'} ${room.status}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="room-actions">
                        ${room.status === 'active' ? `
                            <button class="room-btn btn-join" onclick="joinRoom('${room.id}')">
                                <i class="fas fa-sign-in-alt"></i> Join
                            </button>
                        ` : `
                            <button class="room-btn btn-secondary">
                                <i class="fas fa-info-circle"></i> Details
                            </button>
                        `}
                        <button class="room-btn btn-delete" onclick="leaveRoom('${room.id}')">
                            <i class="fas fa-sign-out-alt"></i> Leave
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function renderInvitations() {
            const container = document.getElementById('invitationsList');
            const badge = document.getElementById('inviteCount');
            
            const pendingInvites = invitations.filter(i => i.status === 'pending');
            badge.textContent = pendingInvites.length;

            if (pendingInvites.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i class="fas fa-inbox"></i></div>
                        <div class="empty-text">No pending invitations</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = pendingInvites.map(invite => `
                <div class="invitation-card">
                    <div class="invitation-header">
                        <div class="invitation-room">${invite.roomName}</div>
                        <div class="invitation-from">From: ${invite.fromUserName}</div>
                    </div>
                    <div class="invitation-actions">
                        <button class="invitation-btn btn-accept" onclick="acceptInvite('${invite.id}')">
                            <i class="fas fa-check"></i> Accept
                        </button>
                        <button class="invitation-btn btn-decline" onclick="declineInvite('${invite.id}')">
                            <i class="fas fa-times"></i> Decline
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function renderInviteLinks() {
            const container = document.getElementById('inviteLinksList');
            const activeRooms = myRooms.filter(r => r.status === 'active' || r.status === 'scheduled');

            if (activeRooms.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-text" style="font-size: 12px; padding: 20px 0;">Create a room to generate invite links</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = activeRooms.map(room => `
                <div class="link-item">
                    <div class="link-room-name">${room.name}</div>
                    <div class="link-code">
                        <span class="code-text">${room.roomCode}</span>
                        <button class="copy-btn" onclick="copyCode('${room.roomCode}')">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <div class="link-actions">
                        <button class="link-btn" onclick="shareLink('${room.id}')">
                            <i class="fas fa-share-alt"></i> Share
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function joinRoom(roomId) {
            // Redirect to room page
            localStorage.setItem('current_room_id', roomId);
            window.location.href = 'room.html?id=' + roomId;
        }

        function deleteRoom(roomId) {
            if (confirm('Delete this room? This action cannot be undone.')) {
                myRooms = myRooms.filter(r => r.id !== roomId);
                saveData();
                renderMyRooms();
                renderInviteLinks();
                updateStats();
                showNotification('Room deleted!');
            }
        }

        function editRoom(roomId) {
            alert('Edit room settings - Coming soon!');
        }

        function leaveRoom(roomId) {
            if (confirm('Leave this room?')) {
                joinedRooms = joinedRooms.filter(r => r.id !== roomId);
                saveData();
                renderJoinedRooms();
                updateStats();
                showNotification('Left room');
            }
        }

        function acceptInvite(inviteId) {
            const invite = invitations.find(i => i.id === inviteId);
            if (invite) {
                invite.status = 'accepted';
                // Add to joined rooms (would fetch from server in real app)
                joinedRooms.push({
                    id: invite.roomId,
                    name: invite.roomName,
                    host: invite.fromUserName,
                    participantCount: 5,
                    status: 'active'
                });
                saveData();
                renderInvitations();
                renderJoinedRooms();
                updateStats();
                showNotification('Invitation accepted!');
            }
        }

        function declineInvite(inviteId) {
            const invite = invitations.find(i => i.id === inviteId);
            if (invite) {
                invite.status = 'declined';
                saveData();
                renderInvitations();
                showNotification('Invitation declined');
            }
        }

        function copyCode(code) {
            navigator.clipboard.writeText(code).then(() => {
                showNotification('Code copied: ' + code);
            });
        }

        function shareLink(roomId) {
            const room = myRooms.find(r => r.id === roomId);
            if (room) {
                const link = `${window.location.origin}/room.html?code=${room.roomCode}`;
                if (navigator.share) {
                    navigator.share({
                        title: room.name,
                        text: `Join my study room: ${room.name}`,
                        url: link
                    });
                } else {
                    navigator.clipboard.writeText(link);
                    showNotification('Link copied!');
                }
            }
        }

        function saveData() {
            localStorage.setItem('edulink_my_rooms', JSON.stringify(myRooms));
            localStorage.setItem('edulink_joined_rooms', JSON.stringify(joinedRooms));
            localStorage.setItem('edulink_invitations', JSON.stringify(invitations));
        }

        function showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, var(--primary), var(--accent-1));
                color: white;
                padding: 16px 24px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                z-index: 10001;
                animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

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

        // Add some demo data for testing
        if (myRooms.length === 0) {
            // Demo data will be added when user creates rooms
        }

        // Add demo invitations
        if (invitations.length === 0) {
            invitations = [
                {
                    id: 'inv_001',
                    roomId: 'room_demo_1',
                    roomName: 'Mathematics Study Group',
                    fromUserId: 'user_priya',
                    fromUserName: 'Priya',
                    status: 'pending'
                },
                {
                    id: 'inv_002',
                    roomId: 'room_demo_2',
                    roomName: 'CS Algorithms',
                    fromUserId: 'user_rahul',
                    fromUserName: 'Rahul',
                    status: 'pending'
                }
            ];
            localStorage.setItem('edulink_invitations', JSON.stringify(invitations));
            renderInvitations();
        }