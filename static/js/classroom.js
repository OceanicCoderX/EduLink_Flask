// ============================================================
// classroom.js — EduLink Classroom Page (DB-backed, no localStorage)
// ============================================================

let currentTab      = 'active';
let pendingJoinId   = null;  // Room ID waiting for password confirm

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadMyRooms();
    loadJoinedRooms();
    initListeners();
});

// ── Stats ─────────────────────────────────────────────────────

function loadStats() {
    fetch('/api/get-classroom-stats')
        .then(r => r.json())
        .then(d => {
            document.getElementById('totalCreated').textContent = d.rooms_created;
            document.getElementById('totalJoined').textContent  = d.rooms_joined;
            document.getElementById('totalHours').textContent   = d.hours_spent + 'h';
            document.getElementById('totalStacks').textContent  = d.stacks;
        })
        .catch(() => {});
}


// ── My Rooms ──────────────────────────────────────────────────

function loadMyRooms() {
    fetch('/api/get-my-rooms')
        .then(r => r.json())
        .then(rooms => {
            const el = document.getElementById('myRoomsList');
            const filtered = rooms.filter(r =>
                currentTab === 'active' ? r.status === 'active' : r.status === 'closed'
            );

            if (filtered.length === 0) {
                el.innerHTML = `<div class="empty-state"><div class="empty-icon"><i class="fas fa-door-closed"></i></div><div class="empty-text">No ${currentTab} rooms</div></div>`;
                renderInviteLinks([]);
                return;
            }

            el.innerHTML = filtered.map(r => `
                <div class="room-card ${r.status === 'closed' ? 'closed-room' : ''}">
                    <div class="room-info">
                        <div class="room-name">
                            ${r.room_name}
                            ${r.has_password ? '<i class="fas fa-lock" style="font-size:12px;color:var(--accent-2);margin-left:4px;"></i>' : ''}
                            ${r.status === 'closed' ? '<span style="font-size:11px;color:#f5494a;margin-left:6px;">[Closed]</span>' : '<span style="font-size:11px;color:#2dce89;margin-left:6px;">● Active</span>'}
                        </div>
                        <div class="room-meta">
                            ${r.subject} · Created ${r.created_date}
                            · <i class="fas fa-users"></i> ${r.member_count} members
                            · <i class="fas fa-clock"></i> ${Math.round((r.total_minutes || 0) / 60 * 10) / 10}h
                        </div>
                        <div class="room-desc">${r.description || ''}</div>
                        <div style="margin-top:4px;font-size:12px;color:var(--text-muted);">
                            Room ID: <strong>${r.room_id}</strong>
                        </div>
                    </div>
                    <div class="room-actions">
                        ${r.status === 'active' ? `
                            <a href="/room/${r.room_id}" class="room-btn enter-btn">
                                <i class="fas fa-sign-in-alt"></i> Enter
                            </a>
                        ` : ''}
                        <button onclick="deleteRoom(${r.room_id})" class="room-btn delete-btn">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');

            // Render invite links for active rooms
            renderInviteLinks(rooms.filter(r => r.status === 'active'));
        });
}


// ── Joined Rooms ──────────────────────────────────────────────

function loadJoinedRooms() {
    fetch('/api/get-joined-rooms')
        .then(r => r.json())
        .then(rooms => {
            const el = document.getElementById('joinedRoomsList');

            if (rooms.length === 0) {
                el.innerHTML = `<div class="empty-state"><div class="empty-icon"><i class="fas fa-users-slash"></i></div><div class="empty-text">You haven't joined any rooms yet</div></div>`;
                return;
            }

            el.innerHTML = rooms.map(r => `
                <div class="room-card ${r.status === 'closed' ? 'closed-room' : ''}">
                    <div class="room-info">
                        <div class="room-name">
                            ${r.room_name}
                            ${r.status === 'closed'
                                ? '<span style="font-size:11px;color:#f5494a;margin-left:6px;">[Closed by admin]</span>'
                                : '<span style="font-size:11px;color:#2dce89;margin-left:6px;">● Active</span>'}
                        </div>
                        <div class="room-meta">
                            ${r.subject} · Host: ${r.admin_name} · Joined ${r.join_date}
                        </div>
                    </div>
                    <div class="room-actions">
                        ${r.status === 'active' ? `
                            <a href="/room/${r.room_id}" class="room-btn enter-btn">
                                <i class="fas fa-sign-in-alt"></i> Enter
                            </a>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        });
}


// ── Invite Links ──────────────────────────────────────────────

function renderInviteLinks(activeRooms) {
    const el = document.getElementById('inviteLinksList');

    if (!activeRooms || activeRooms.length === 0) {
        el.innerHTML = `<div class="empty-state"><div class="empty-text" style="font-size:12px;padding:20px 0;">Create a room to generate invite links</div></div>`;
        return;
    }

    el.innerHTML = activeRooms.map(r => {
        const link = `${window.location.origin}/room/${r.room_id}`;
        const waText = encodeURIComponent(`Join my EduLink study room "${r.room_name}"!\n🔗 Room ID: ${r.room_id}\n⬇️ Link: ${link}`);
        return `
            <div class="link-item">
                <div class="link-room-name">${r.room_name}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">ID: ${r.room_id}</div>
                <div class="link-actions" style="display:flex;gap:6px;flex-wrap:wrap;">
                    <button class="link-btn" onclick="copyInviteLink('${link}', this)">
                        <i class="fas fa-copy"></i> Copy Link
                    </button>
                    <a class="link-btn" href="https://wa.me/?text=${waText}" target="_blank"
                       style="text-decoration:none;color:inherit;">
                        <i class="fab fa-whatsapp" style="color:#25D366;"></i> WhatsApp
                    </a>
                    <button class="link-btn" onclick="nativeShare('${r.room_name}', '${link}')">
                        <i class="fas fa-share-alt"></i> Share
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function copyInviteLink(link, btn) {
    navigator.clipboard.writeText(link).then(() => {
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => { btn.innerHTML = '<i class="fas fa-copy"></i> Copy Link'; }, 2000);
    });
}

function nativeShare(name, link) {
    if (navigator.share) {
        navigator.share({ title: name, text: `Join my EduLink study room: ${name}`, url: link });
    } else {
        navigator.clipboard.writeText(link);
        showToast('Link copied to clipboard!', 'success');
    }
}


// ── Create Room ───────────────────────────────────────────────

function initListeners() {
    // Tab switching
    document.querySelectorAll('.room-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.room-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentTab = this.dataset.tab;
            loadMyRooms();
        });
    });

    // Modal: open / close
    document.getElementById('createRoomBtn').onclick  = openModal;
    document.getElementById('closeModalBtn').onclick  = closeModal;
    document.getElementById('cancelCreateBtn').onclick = closeModal;

    // Password checkbox toggle
    document.getElementById('passwordProtected').addEventListener('change', function () {
        document.getElementById('roomPassword').style.display = this.checked ? 'block' : 'none';
        if (!this.checked) document.getElementById('roomPassword').value = '';
    });

    // Save room
    document.getElementById('saveRoomBtn').onclick = createRoom;

    // Join by ID
    document.getElementById('joinRoomBtn').onclick = handleJoinById;
    document.getElementById('joinRoomIdInput').addEventListener('keydown', e => {
        if (e.key === 'Enter') handleJoinById();
    });

    // Password modal confirm
    document.getElementById('closePwdModalBtn').onclick = closePwdModal;
    document.getElementById('cancelPwdBtn').onclick     = closePwdModal;
    document.getElementById('confirmJoinBtn').onclick   = confirmJoin;
    document.getElementById('joinPasswordInput').addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmJoin();
    });

    // Close modals on backdrop click
    document.getElementById('createRoomModal').addEventListener('click', e => {
        if (e.target.id === 'createRoomModal') closeModal();
    });
    document.getElementById('passwordModal').addEventListener('click', e => {
        if (e.target.id === 'passwordModal') closePwdModal();
    });
}

function openModal() {
    document.getElementById('createRoomModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('createRoomModal').style.display = 'none';
    document.getElementById('createRoomForm').reset();
    document.getElementById('roomPassword').style.display = 'none';
}

function closePwdModal() {
    document.getElementById('passwordModal').style.display = 'none';
    document.getElementById('joinPasswordInput').value = '';
    pendingJoinId = null;
}


function createRoom() {
    const name    = document.getElementById('roomName').value.trim();
    const subject = document.getElementById('roomSubject').value.trim();
    const desc    = document.getElementById('roomDescription').value.trim();
    const pwdProtected = document.getElementById('passwordProtected').checked;
    const password = pwdProtected ? document.getElementById('roomPassword').value.trim() : '';

    if (!name)    return showToast('Room name is required!', 'error');
    if (!subject) return showToast('Subject is required!', 'error');
    if (pwdProtected && !password) return showToast('Enter a password!', 'error');

    const fd = new FormData();
    fd.append('room_name', name);
    fd.append('subject', subject);
    fd.append('room_description', desc);
    if (password) fd.append('room_password', password);

    fetch('/api/create-room', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                closeModal();
                showToast(`Room "${data.room_name}" created! +1 Stack 🔥`, 'success');
                loadMyRooms();
                loadStats();
            } else {
                showToast(data.error || 'Failed to create room', 'error');
            }
        });
}


// ── Join by ID ────────────────────────────────────────────────

function handleJoinById() {
    const roomId = document.getElementById('joinRoomIdInput').value.trim();
    if (!roomId) return showToast('Enter a Room ID!', 'error');
    attemptJoin(roomId, '');
}

function attemptJoin(roomId, password) {
    const fd = new FormData();
    fd.append('room_id', roomId);
    if (password) fd.append('password', password);

    fetch('/api/join-room', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                closePwdModal();
                showToast('Joined! Entering room...', 'success');
                setTimeout(() => { window.location.href = '/room/' + data.room_id; }, 600);
            } else if (data.error === 'Incorrect password') {
                // Show password modal
                pendingJoinId = roomId;
                document.getElementById('passwordModal').style.display = 'flex';
                document.getElementById('joinPasswordInput').focus();
                if (password) showToast('Incorrect password, try again.', 'error');
            } else {
                showToast(data.error || 'Could not join room', 'error');
            }
        });
}

function confirmJoin() {
    const password = document.getElementById('joinPasswordInput').value.trim();
    if (!password) return showToast('Enter the password!', 'error');
    if (!pendingJoinId) return;
    attemptJoin(pendingJoinId, password);
}


// ── Delete Room ───────────────────────────────────────────────

function deleteRoom(roomId) {
    if (!confirm('Delete this room permanently? All messages will be lost.')) return;
    const fd = new FormData();
    fd.append('room_id', roomId);
    fetch('/api/delete-room', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('Room deleted', 'success');
                loadMyRooms();
                loadStats();
            } else {
                showToast(data.error || 'Could not delete', 'error');
            }
        });
}

// ── Inline styles for join-room card and closed-room ─────────

const style = document.createElement('style');
style.textContent = `
    .join-room-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border: 1px solid var(--border-color);
    }
    .join-room-card h3 {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 6px;
        color: var(--text-primary);
    }
    .join-room-card p {
        font-size: 13px;
        color: var(--text-muted);
        margin-bottom: 12px;
    }
    .join-input-row {
        display: flex;
        gap: 8px;
    }
    .join-id-input {
        flex: 1;
        padding: 10px 14px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-primary);
        color: var(--text-primary);
        font-size: 14px;
        outline: none;
    }
    .join-id-input:focus { border-color: var(--primary); }
    .join-id-btn {
        padding: 10px 18px;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        white-space: nowrap;
    }
    .join-id-btn:hover { opacity: 0.85; }

    .closed-room { opacity: 0.65; }

    .link-item {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
    }
    .link-item:last-child { border-bottom: none; }
    .link-room-name {
        font-weight: 600;
        font-size: 14px;
        color: var(--text-primary);
        margin-bottom: 2px;
    }
    .link-btn {
        padding: 6px 12px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background: var(--bg-primary);
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        text-decoration: none;
    }
    .link-btn:hover { background: var(--primary); color: white; border-color: var(--primary); }

    .stat-icon.orange { background: rgba(251,137,64,0.12); color:#fb8940; }
`;
document.head.appendChild(style);


// ── Toast helper (uses common.js if available, else inline) ───

function showToast(msg, type) {
    if (typeof window.showToast === 'function' && window.showToast !== showToast) {
        window.showToast(msg, type); return;
    }
    const t = document.createElement('div');
    t.style.cssText = `position:fixed;top:20px;right:20px;z-index:9999;
        background:${type==='error'?'#f5494a':'#2dce89'};color:white;
        padding:12px 20px;border-radius:10px;font-size:14px;font-weight:500;
        box-shadow:0 4px 20px rgba(0,0,0,0.2);animation:slideIn .3s ease;`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
}