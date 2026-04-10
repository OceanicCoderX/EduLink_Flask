// Theme Toggle
const lightThemeBtn = document.getElementById('lightThemeBtn');
const darkThemeBtn = document.getElementById('darkThemeBtn');

if (lightThemeBtn && darkThemeBtn) {
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
}

// Load Dashboard Data from Server
function loadDashboardStats() {
    fetch('/api/dashboard-stats')
        .then(r => r.json())
        .then(data => {
            // Update Summary Stats
            if (document.getElementById('totalStudyTime')) document.getElementById('totalStudyTime').textContent = data.total_hours + 'h';
            if (document.getElementById('tasksCompleted')) document.getElementById('tasksCompleted').textContent = data.completed_tasks;
            if (document.getElementById('pomodoroSessions')) document.getElementById('pomodoroSessions').textContent = data.total_sessions;
            if (document.getElementById('totalStacks')) document.getElementById('totalStacks').textContent = data.total_stacks;

            // Load username from session-informed span
            const userSpan = document.getElementById('userName');
            // Dashboard.html already has this populated via Jinja, but we can sync if needed

            // Recent Tasks
            const taskList = document.getElementById('recentTasksList');
            if (taskList) {
                if (!data.recent_tasks || data.recent_tasks.length === 0) {
                    taskList.innerHTML = '<div style="color:var(--text-muted);padding:16px;">No tasks yet</div>';
                } else {
                    taskList.innerHTML = data.recent_tasks.map(t => `
                        <div class="task-item">
                            <div class="task-checkbox ${t.status === 'completed' ? 'checked' : ''}">
                                ${t.status === 'completed' ? '<i class="fas fa-check"></i>' : ''}
                            </div>
                            <div class="task-content">
                                <div class="task-title">${t.title}</div>
                                <div class="task-meta">
                                    <span class="task-category study">${t.priority || 'normal'}</span>
                                    <span><i class="far fa-calendar"></i> ${t.due_date}</span>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }
            }

            // Recent Notes
            const noteList = document.getElementById('recentNotesList');
            if (noteList) {
                if (!data.recent_notes || data.recent_notes.length === 0) {
                    noteList.innerHTML = '<div style="color:var(--text-muted);padding:16px;">No notes yet</div>';
                } else {
                    noteList.innerHTML = data.recent_notes.map(n => `
                        <div class="note-item">
                            <div class="note-title">${n.title}</div>
                            <div class="note-meta">
                                <span><i class="far fa-calendar"></i> ${n.date}</span>
                                <span><i class="far fa-folder"></i> ${n.category}</span>
                            </div>
                        </div>
                    `).join('');
                }
            }
        })
        .catch(err => {
            console.error('Error loading dashboard stats:', err);
        });
}

// Initialize
window.addEventListener('load', loadDashboardStats);

// Sidebar Toggle
const sidebar = document.getElementById('sidebar');
if (sidebar) {
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 968) {
            if (e.target.closest('.mobile-nav-item')) {
                sidebar.classList.remove('open');
            }
        }
    });

    document.addEventListener('click', function (e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        }
    });
}