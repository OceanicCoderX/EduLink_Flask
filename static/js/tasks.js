// ============================================================
// EDULINK TASKS.JS — FULLY FIXED VERSION
// Sab kuch DOMContentLoaded ke andar wrap kiya hai
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // ── Global State ──────────────────────────────────────────
    let tasks = [];
    let currentView = 'daily';
    let currentDate = new Date();
    let editingTaskId = null;
    let selectedPriority = 'medium';
    let activeFilter = 'all';
    let currentSort = 'date';
    let showCompleted = true;

    // ── DOM Elements ──────────────────────────────────────────
    const taskModal = document.getElementById('taskModal');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const saveTaskBtn = document.getElementById('saveTaskBtn');
    const taskForm = document.getElementById('taskForm');
    const tasksList = document.getElementById('tasksList');
    const emptyState = document.getElementById('emptyState');
    const searchInput = document.getElementById('searchInput');
    const viewBtns = document.querySelectorAll('.view-btn');
    const filterChips = document.querySelectorAll('.filter-chip');
    const priorityOptions = document.querySelectorAll('.priority-option');
    const exportExcelBtn = document.getElementById('exportExcelBtn');
    const filterBtn = document.getElementById('filterBtn');
    const filterDropdown = document.getElementById('filterDropdown');

    // Optional elements (header se aate hain — null safe)
    const lightThemeBtn = document.getElementById('lightThemeBtn');
    const darkThemeBtn = document.getElementById('darkThemeBtn');
    const settingsBtnEl = document.getElementById('settingsBtn');
    const timeEstimateToggle = document.getElementById('timeEstimateToggle');
    const pomodoroToggle = document.getElementById('pomodoroToggle');
    const timeEstimateInputs = document.getElementById('timeEstimateInputs');
    const exportPdfBtn = document.getElementById('exportPdfBtn');

    // ── Init ──────────────────────────────────────────────────
    if (typeof loadUserProfile === 'function') loadUserProfile();
    if (typeof initializeTheme === 'function') initializeTheme();
    updateCurrentDate();
    setDefaultDateTime();
    loadTasks();
    applyTheme();

    // ── Theme ─────────────────────────────────────────────────
    function applyTheme() {
        const saved = localStorage.getItem('edulink_theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
        if (saved === 'dark') {
            if (darkThemeBtn) darkThemeBtn.classList.add('active');
            if (lightThemeBtn) lightThemeBtn.classList.remove('active');
        }
    }

    if (lightThemeBtn) lightThemeBtn.addEventListener('click', () => {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('edulink_theme', 'light');
        lightThemeBtn.classList.add('active');
        if (darkThemeBtn) darkThemeBtn.classList.remove('active');
    });

    if (darkThemeBtn) darkThemeBtn.addEventListener('click', () => {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('edulink_theme', 'dark');
        darkThemeBtn.classList.add('active');
        if (lightThemeBtn) lightThemeBtn.classList.remove('active');
    });

    // ── Date / Time helpers ───────────────────────────────────
    function updateCurrentDate() {
        const el = document.getElementById('currentDate');
        if (!el) return;
        el.textContent = currentDate.toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });
    }

    function setDefaultDateTime() {
        const today = new Date();
        const dateEl = document.getElementById('taskDate');
        const timeEl = document.getElementById('taskTime');
        if (dateEl) dateEl.value = today.toISOString().split('T')[0];
        if (timeEl) timeEl.value = today.toTimeString().slice(0, 5);
    }

    // ── Load Tasks from DB ────────────────────────────────────
    async function loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            tasks = data.map(task => ({
                task_id: task.task_id,
                user_id: task.user_id,
                title: task.title || '',
                description: task.description || '',
                date: task.date || '',
                time: task.time || '',
                recurring: task.recurring || 'once',
                priority: task.priority || 'medium',
                status: task.status || 'pending',
                createdAt: task.createdAt || '',
                completedDate: task.completedDate || ''
            }));
            renderTasks();
            updateStats();
            initializeCalendarViews();
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    }

    // ── Modal ─────────────────────────────────────────────────
    if (addTaskBtn) addTaskBtn.addEventListener('click', () => openModal('add'));
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    window.addEventListener('click', (e) => {
        if (e.target === taskModal) closeModal();
    });

    function openModal(mode, taskId = null) {
        taskModal.classList.add('show');
        document.body.style.overflow = 'hidden';

        if (mode === 'add') {
            document.getElementById('modalTitle').textContent = 'Add New Task';
            if (taskForm) taskForm.reset();
            setDefaultDateTime();
            selectedPriority = 'medium';
            updatePrioritySelection();
            editingTaskId = null;
        } else if (mode === 'edit') {
            document.getElementById('modalTitle').textContent = 'Edit Task';
            const task = tasks.find(t => t.task_id === taskId);
            if (task) {
                document.getElementById('taskTitle').value = task.title;
                document.getElementById('taskDescription').value = task.description || '';
                document.getElementById('taskDate').value = task.date;
                document.getElementById('taskTime').value = task.time ? task.time.slice(0, 5) : '';
                document.getElementById('taskRecurring').value = task.recurring || 'once';
                selectedPriority = task.priority || 'medium';
                updatePrioritySelection();
                editingTaskId = taskId;
            }
        }
    }

    function closeModal() {
        taskModal.classList.remove('show');
        document.body.style.overflow = 'auto';
        if (taskForm) taskForm.reset();
        setDefaultDateTime();
        editingTaskId = null;
    }

    // ── Priority Selection ────────────────────────────────────
    priorityOptions.forEach(option => {
        option.addEventListener('click', () => {
            selectedPriority = option.dataset.priority;
            updatePrioritySelection();
        });
    });

    function updatePrioritySelection() {
        priorityOptions.forEach(option => {
            option.classList.toggle('selected', option.dataset.priority === selectedPriority);
        });
    }

    // ── Save Task (AJAX) ──────────────────────────────────────
    if (saveTaskBtn) {
        saveTaskBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const title = document.getElementById('taskTitle').value.trim();
            const description = document.getElementById('taskDescription').value.trim();
            const date = document.getElementById('taskDate').value;
            const time = document.getElementById('taskTime').value;
            const recurring = document.getElementById('taskRecurring').value;

            if (!title || !date || !time) {
                alert('Please fill in all required fields!');
                return;
            }

            // Button disable karo double-click rokne ke liye
            saveTaskBtn.disabled = true;
            saveTaskBtn.textContent = 'Saving...';

            const formData = new FormData();
            formData.append('taskTitle', title);
            formData.append('taskDescription', description);
            formData.append('taskDate', date);
            formData.append('taskTime', time);
            formData.append('taskRecurring', recurring);
            formData.append('taskPriority', selectedPriority);
            if (editingTaskId) formData.append('task_id', editingTaskId);

            try {
                const url = editingTaskId ? '/api/update-task' : '/api/save-task';
                const response = await fetch(url, { method: 'POST', body: formData });
                const result = await response.json();

                if (result.success) {
                    await loadTasks();
                    closeModal();
                    showNotification(editingTaskId ? '✅ Task updated!' : '✅ Task added!');
                } else {
                    alert('Error saving task: ' + (result.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Save error:', error);
                alert('Error saving task. Check console.');
            } finally {
                saveTaskBtn.disabled = false;
                saveTaskBtn.innerHTML = '<i class="fas fa-save"></i> Save Task';
            }
        });
    }

    // Form submit se page redirect rokna — safety net
    if (taskForm) {
        taskForm.addEventListener('submit', (e) => e.preventDefault());
    }

    // ── Render Tasks ──────────────────────────────────────────

    function renderTasks(filter = activeFilter, searchQuery = '') {
        let filtered = [...tasks];

        if (filter === 'pending') filtered = filtered.filter(t => t.status === 'pending');
        if (filter === 'completed') filtered = filtered.filter(t => t.status === 'completed');
        if (filter === 'high') filtered = filtered.filter(t => t.priority === 'high');

        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            filtered = filtered.filter(t =>
                (t.title && t.title.toLowerCase().includes(q)) ||
                (t.description && t.description.toLowerCase().includes(q))
            );
        }

        // ── Advanced Sorting ──────────────────────────────────
        if (currentSort === 'date') {
            filtered.sort((a, b) => new Date(a.date + ' ' + (a.time || '00:00')) - new Date(b.date + ' ' + (b.time || '00:00')));
        } else if (currentSort === 'priority') {
            const pMap = { 'high': 3, 'medium': 2, 'low': 1, 'None': 1 };
            filtered.sort((a, b) => pMap[b.priority || 'medium'] - pMap[a.priority || 'medium']);
        } else if (currentSort === 'title') {
            filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
        }

        if (!showCompleted) {
            filtered = filtered.filter(t => t.status !== 'completed');
        }

        if (tasksList) tasksList.innerHTML = '';
        else return;

        if (filtered.length === 0) {
            if (emptyState) {
                emptyState.style.display = 'block';
                tasksList.appendChild(emptyState);
            }
        } else {
            if (emptyState) emptyState.style.display = 'none';
            filtered.forEach(task => {
                tasksList.innerHTML += createTaskHTML(task);
            });
        }
    }

    // ── Create Task HTML ──────────────────────────────────────
    function createTaskHTML(task) {
        // Time format — "HH:MM:SS" se "HH:MM" lo
        const timeDisplay = task.time ? task.time.slice(0, 5) : '--:--';

        // Date format
        let dateDisplay = task.date;
        try {
            const d = new Date(task.date);
            if (!isNaN(d)) {
                dateDisplay = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }
        } catch (e) { }

        // Priority — None/null ke liye default
        const priority = (task.priority && task.priority !== 'None') ? task.priority : 'medium';
        const status = task.status || 'pending';

        // Title — None/null ke liye default
        const title = (task.title && task.title !== 'None') ? task.title : '(No Title)';
        const desc = (task.description && task.description !== 'None') ? task.description : '';

        return `
            <div class="task-item ${priority} ${status}" data-id="${task.task_id}">
                <div class="task-checkbox ${status === 'completed' ? 'checked' : ''}"
                     onclick="window._toggleTask(${task.task_id})">
                    ${status === 'completed' ? '<i class="fas fa-check"></i>' : ''}
                </div>
                <div class="task-content">
                    <div class="task-title ${status === 'completed' ? 'completed-text' : ''}">${title}</div>
                    ${desc ? `<div class="task-description">${desc}</div>` : ''}
                    <div class="task-meta">
                        <span class="task-badge"><i class="fas fa-calendar"></i> ${dateDisplay}</span>
                        <span class="task-badge"><i class="fas fa-clock"></i> ${timeDisplay}</span>
                        ${task.recurring && task.recurring !== 'once' ? `
                            <span class="task-badge"><i class="fas fa-redo"></i> ${task.recurring}</span>
                        ` : ''}
                        <span class="priority-badge priority-${priority}">${priority.toUpperCase()}</span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-action-btn" onclick="window._editTask(${task.task_id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="task-action-btn" onclick="window._deleteTask(${task.task_id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // ── Global task action functions (onclick me use hoti hain) ──
    window._toggleTask = function (taskId) {
        const task = tasks.find(t => t.task_id === taskId);
        if (!task) return;
        const newStatus = task.status === 'pending' ? 'completed' : 'pending';

        fetch('/api/update-task-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `task_id=${taskId}&status=${newStatus}`
        })
            .then(r => r.json())
            .then(result => {
                if (result.success) {
                    loadTasks();
                    showNotification(newStatus === 'completed' ? '✅ Task completed!' : '🔄 Task reopened!');
                }
            })
            .catch(err => console.error('Toggle error:', err));
    };

    window._editTask = function (taskId) {
        openModal('edit', taskId);
    };

    window._deleteTask = function (taskId) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        fetch('/api/delete-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `task_id=${taskId}`
        })
            .then(r => r.json())
            .then(result => {
                if (result.success || result.status === 'deleted') {
                    loadTasks();
                    showNotification('🗑️ Task deleted!');
                }
            })
            .catch(err => console.error('Delete error:', err));
    };

    // ── Stats ─────────────────────────────────────────────────
    function updateStats() {
        const total = tasks.length;
        const completed = tasks.filter(t => t.status === 'completed').length;
        const pending = tasks.filter(t => t.status === 'pending').length;
        const today = new Date().toISOString().split('T')[0];
        const todayCount = tasks.filter(t => t.date === today).length;
        const streak = 0;

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        set('totalTasksCount', total);
        set('completedTasksCount', completed);
        set('pendingTasksCount', pending);
        set('todayTasksCount', getTasksForDate(today).length);
        set('streakCount', streak)

        // Donut
        const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
        const circle = document.getElementById('progressCircle');
        if (circle) {
            const circ = 2 * Math.PI * 70; // r=70 in SVG
            circle.style.strokeDasharray = circ;
            circle.style.strokeDashoffset = circ - (circ * pct / 100);
        }
        const pctEl = document.getElementById('progressPercentage');
        if (pctEl) pctEl.textContent = pct + '%';
    }

    // ── Search ────────────────────────────────────────────────
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            renderTasks(activeFilter, e.target.value);
        });
    }

    // ── Filter Chips ──────────────────────────────────────────
    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            activeFilter = chip.dataset.filter;
            renderTasks(activeFilter, searchInput ? searchInput.value : '');
        });
    });

    // ── View Toggle ───────────────────────────────────────────
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            switchView(currentView);
            updateCalendarTitle();
        });
    });

    function switchView(view) {
        ['dailyView', 'weeklyView', 'monthlyView'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.remove('active');
        });
        const target = document.getElementById(
            view === 'daily' ? 'dailyView' : view === 'weekly' ? 'weeklyView' : 'monthlyView'
        );
        if (target) target.classList.add('active');

        if (view === 'daily') renderDailyView();
        if (view === 'weekly') renderWeeklyView();
        if (view === 'monthly') renderMonthlyView();
    }

    // ── Calendar Views ────────────────────────────────────────
    function initializeCalendarViews() {
        updateCalendarTitle();
        renderDailyView();
        renderWeeklyView();
        renderMonthlyView();
    }

    function updateCalendarTitle() {
        const titleEl = document.getElementById('calendarTitle');
        if (!titleEl) return;
        const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        if (currentView === 'daily') {
            titleEl.textContent = 'Today - ' + currentDate.toLocaleDateString('en-US', opts);
        } else if (currentView === 'weekly') {
            const s = new Date(currentDate);
            s.setDate(currentDate.getDate() - currentDate.getDay());
            const e = new Date(s); e.setDate(s.getDate() + 6);
            titleEl.textContent = `Week: ${s.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${e.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        } else {
            titleEl.textContent = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        }
    }

    function renderDailyView() {
        const timeline = document.getElementById('dailyTimeline');
        if (!timeline) return;

        // currentDate ko use karo — nav buttons se change hoti hai
        const viewDateStr = currentDate.toISOString().split('T')[0];
        const dayTasks = getTasksForDate(viewDateStr);

        if (dayTasks.length === 0) {
            timeline.innerHTML = `<div class="empty-state">
                <div class="empty-icon"><i class="fas fa-calendar-check"></i></div>
                <div class="empty-text">No pending tasks for this day 🎉</div>
            </div>`;
            return;
        }

        timeline.innerHTML = dayTasks.map(task => `
            <div class="timeline-slot" data-id="${task.task_id}" style="display:flex;align-items:flex-start;gap:12px;padding:14px 16px;background:var(--card-bg,#1e2235);border-radius:12px;margin-bottom:10px;border:1px solid var(--border-color,rgba(255,255,255,0.08))">

                <!-- Checkbox -->
                <div onclick="window._toggleTask(${task.task_id})"
                     style="width:24px;height:24px;border-radius:6px;border:2px solid var(--primary,#5e72e4);
                            display:flex;align-items:center;justify-content:center;cursor:pointer;
                            flex-shrink:0;margin-top:2px;transition:all 0.2s;
                            background:${task.status === 'completed' || task.completedDate === viewDateStr ? 'var(--primary,#5e72e4)' : 'transparent'}"
                     title="Mark complete">
                    ${task.status === 'completed' || task.completedDate === viewDateStr ? '<i class="fas fa-check" style="color:white;font-size:12px"></i>' : ''}
                </div>

                <!-- Time + Content -->
                <div style="flex:1;min-width:0">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                        <span style="font-size:12px;color:var(--text-muted,#8892b0);font-weight:600">
                            ${task.time ? task.time.slice(0, 5) : '--:--'}
                        </span>
                        <span class="priority-badge priority-${task.priority || 'medium'}" style="font-size:11px">
                            ${(task.priority || 'medium').toUpperCase()}
                        </span>
                        ${task.recurring && task.recurring !== 'once' ? `<span style="font-size:11px;color:var(--accent-1,#2dceb1)"><i class="fas fa-redo"></i> ${task.recurring}</span>` : ''}
                    </div>
                    <div style="font-weight:600;font-size:15px;color:var(--text-primary,#fff);margin-bottom:3px;
                                text-decoration:${task.status === 'completed' || task.completedDate === viewDateStr ? 'line-through' : 'none'};
                                opacity:${task.status === 'completed' || task.completedDate === viewDateStr ? '0.6' : '1'}">
                        ${task.title}
                    </div>
                    ${task.description ? `<div style="font-size:13px;color:var(--text-secondary,#aab);margin-top:2px">${task.description}</div>` : ''}
                </div>

                <!-- Action Buttons -->
                <div style="display:flex;gap:6px;flex-shrink:0">
                    <button onclick="window._editTask(${task.task_id})"
                            style="width:32px;height:32px;border-radius:8px;border:1px solid var(--border-color,rgba(255,255,255,0.1));
                                   background:transparent;color:var(--text-secondary,#aab);cursor:pointer;
                                   display:flex;align-items:center;justify-content:center;transition:all 0.2s"
                            title="Edit" onmouseover="this.style.color='#5e72e4'" onmouseout="this.style.color=''">
                        <i class="fas fa-edit" style="font-size:13px"></i>
                    </button>
                    <button onclick="window._deleteTask(${task.task_id})"
                            style="width:32px;height:32px;border-radius:8px;border:1px solid var(--border-color,rgba(255,255,255,0.1));
                                   background:transparent;color:var(--text-secondary,#aab);cursor:pointer;
                                   display:flex;align-items:center;justify-content:center;transition:all 0.2s"
                            title="Delete" onmouseover="this.style.color='#f5365c'" onmouseout="this.style.color=''">
                        <i class="fas fa-trash" style="font-size:13px"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    function renderWeeklyView() {
        const weekGrid = document.getElementById('weekGrid');
        if (!weekGrid) return;
        const startOfWeek = new Date(currentDate);
        startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

        let html = '';
        for (let i = 0; i < 7; i++) {
            const day = new Date(startOfWeek);
            day.setDate(startOfWeek.getDate() + i);
            const dateStr = day.toISOString().split('T')[0];
            const dayTasks = tasks.filter(t => t.date === dateStr);
            const isToday = dateStr === new Date().toISOString().split('T')[0];

            html += `
                <div class="week-day ${isToday ? 'today' : ''}">
                    <div class="day-name">${day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                    <div class="day-date">${day.getDate()}</div>
                    <div class="day-tasks-count">${dayTasks.length} task${dayTasks.length !== 1 ? 's' : ''}</div>
                </div>
            `;
        }
        weekGrid.innerHTML = html;
    }

    function renderMonthlyView() {
        const monthGrid = document.getElementById('monthGrid');
        if (!monthGrid) return;
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const todayStr = new Date().toISOString().split('T')[0];
        let html = '';

        ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(d => {
            html += `<div class="month-day-header" style="text-align:center;font-size:12px;font-weight:700;padding:8px 0;color:var(--text-muted,#8892b0)">${d}</div>`;
        });

        // Empty cells
        for (let i = 0; i < firstDay; i++) {
            html += `<div class="month-day other-month" style="opacity:0.3;min-height:70px"></div>`;
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isToday = dateStr === todayStr;

            // ✅ FIX: Recurring tasks bhi include karo
            const dayTasks = getTasksForDate(dateStr);
            const pending = dayTasks.filter(t => t.status !== 'completed').length;
            const completed = dayTasks.filter(t => t.status === 'completed').length;

            html += `
                <div class="month-day ${isToday ? 'today' : ''}"
                     style="min-height:70px;padding:6px;border-radius:8px;cursor:pointer;
                            border:1px solid ${isToday ? 'var(--primary,#5e72e4)' : 'transparent'};
                            background:${isToday ? 'rgba(94,114,228,0.08)' : 'transparent'};
                            transition:all 0.2s"
                     onclick="window._jumpToDay('${dateStr}')"
                     onmouseover="this.style.background='rgba(94,114,228,0.05)'"
                     onmouseout="this.style.background='${isToday ? 'rgba(94,114,228,0.08)' : 'transparent'}'">
                    <div style="font-size:13px;font-weight:${isToday ? '700' : '500'};
                                color:${isToday ? 'var(--primary,#5e72e4)' : 'var(--text-primary,#fff)'};
                                margin-bottom:4px">${day}</div>
                    <div style="display:flex;flex-wrap:wrap;gap:3px">
                        ${pending > 0 ? `<span style="font-size:10px;background:rgba(94,114,228,0.25);color:#5e72e4;padding:1px 5px;border-radius:4px;font-weight:600">${pending}p</span>` : ''}
                        ${completed > 0 ? `<span style="font-size:10px;background:rgba(45,206,177,0.2);color:#2dceb1;padding:1px 5px;border-radius:4px;font-weight:600">${completed}✓</span>` : ''}
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:2px">
                        ${dayTasks.slice(0, 3).map(t => `<div style="width:6px;height:6px;border-radius:50%;background:${t.priority === 'high' ? '#f5365c' : t.priority === 'low' ? '#2dceb1' : '#fb6340'}"></div>`).join('')}
                    </div>
                </div>`;
        }
        monthGrid.innerHTML = html;
    }

    // ✅ NEW: Recurring tasks ke liye date check — ek task ke multiple dates calculate karo
    function getTasksForDate(dateStr) {
        if (!dateStr) return [];
        const checkDate = new Date(dateStr + 'T12:00:00');

        return tasks.filter(task => {
            if (task.date === dateStr) return true;
            if (task.completedDate === dateStr) return true;

            const taskDate = new Date(task.date + 'T12:00:00');
            // ❌ Task should NOT appear on dates before its initial Due Date
            if (checkDate < taskDate) return false;

            if (!task.recurring || task.recurring === 'once') return false;

            if (task.recurring === 'daily') return true;
            if (task.recurring === 'weekly') return taskDate.getDay() === checkDate.getDay();
            if (task.recurring === 'monthly') return taskDate.getDate() === checkDate.getDate();
            if (task.recurring === 'yearly') {
                return taskDate.getDate() === checkDate.getDate() &&
                    taskDate.getMonth() === checkDate.getMonth();
            }
            return false;
        });
    }

    // ── Calendar Navigation ───────────────────────────────────
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const todayBtn = document.getElementById('todayBtn');

    if (prevBtn) prevBtn.addEventListener('click', () => {
        if (currentView === 'daily') currentDate.setDate(currentDate.getDate() - 1);
        if (currentView === 'weekly') currentDate.setDate(currentDate.getDate() - 7);
        if (currentView === 'monthly') currentDate.setMonth(currentDate.getMonth() - 1);
        switchView(currentView);
        updateCalendarTitle();
    });

    if (nextBtn) nextBtn.addEventListener('click', () => {
        if (currentView === 'daily') currentDate.setDate(currentDate.getDate() + 1);
        if (currentView === 'weekly') currentDate.setDate(currentDate.getDate() + 7);
        if (currentView === 'monthly') currentDate.setMonth(currentDate.getMonth() + 1);
        switchView(currentView);
        updateCalendarTitle();
    });

    if (todayBtn) todayBtn.addEventListener('click', () => {
        currentDate = new Date();
        switchView(currentView);
        updateCalendarTitle();
    });

    // ── Export ────────────────────────────────────────────────
    if (exportExcelBtn) exportExcelBtn.addEventListener('click', exportToExcel);
    if (exportPdfBtn) exportPdfBtn.addEventListener('click', exportToPDF);

    function exportToExcel() {
        if (tasks.length === 0) { alert('No tasks to export!'); return; }
        let csv = 'Title,Description,Date,Time,Priority,Status,Recurring\n';
        tasks.forEach(t => {
            csv += `"${t.title}","${t.description}","${t.date}","${t.time}","${t.priority}","${t.status}","${t.recurring}"\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `edulink_tasks_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(a.href);
        showNotification('📊 Tasks exported!');
    }

    function exportToPDF() {
        if (tasks.length === 0) { alert('No tasks to export!'); return; }
        const win = window.open('', '', 'width=800,height=600');
        let html = `<html><head><title>EduLink Tasks</title>
        <style>body{font-family:Arial,sans-serif;padding:40px}h1{color:#5e72e4}
        table{width:100%;border-collapse:collapse;margin-top:20px}
        th,td{border:1px solid #ddd;padding:12px;text-align:left}
        th{background:#5e72e4;color:white}</style></head><body>
        <h1>📋 EduLink Tasks Report</h1>
        <p>Generated: ${new Date().toLocaleDateString()}</p>
        <table><thead><tr><th>Title</th><th>Date</th><th>Time</th><th>Priority</th><th>Status</th><th>Description</th></tr></thead><tbody>`;
        tasks.forEach(t => {
            html += `<tr><td>${t.title}</td><td>${t.date}</td><td>${t.time ? t.time.slice(0, 5) : ''}</td>
            <td>${t.priority.toUpperCase()}</td><td>${t.status.toUpperCase()}</td><td>${t.description || '-'}</td></tr>`;
        });
        html += `</tbody></table></body></html>`;
        win.document.write(html);
        win.document.close();
        win.print();
    }

    // ── Notification ──────────────────────────────────────────
    function showNotification(message) {
        const n = document.createElement('div');
        n.style.cssText = `position:fixed;top:20px;right:20px;background:linear-gradient(135deg,#5e72e4,#2dceb1);
            color:white;padding:16px 24px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.2);
            z-index:10001;font-weight:600;font-size:14px;animation:slideInNotif 0.3s ease`;
        n.textContent = message;
        document.body.appendChild(n);
        setTimeout(() => { n.style.opacity = '0'; n.style.transition = 'opacity 0.3s'; setTimeout(() => n.remove(), 300); }, 3000);
    }

    // Notification animation
    const style = document.createElement('style');
    style.textContent = `@keyframes slideInNotif { from { transform: translateX(400px); opacity:0 } to { transform: translateX(0); opacity:1 } }
    .completed-text { text-decoration: line-through; opacity: 0.6; }`;
    document.head.appendChild(style);

    // ── Settings ──────────────────────────────────────────────
    if (settingsBtnEl) settingsBtnEl.addEventListener('click', () => {
        alert('Settings panel will be integrated soon!');
    });

    // ── Mobile Sidebar ────────────────────────────────────────
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && window.innerWidth <= 968 && e.target.closest('.mobile-nav-item')) {
            sidebar.classList.remove('open');
        }
    });


    // ✅ Monthly view se click karke daily view pe jaao
    window._jumpToDay = function (dateStr) {
        currentDate = new Date(dateStr + 'T12:00:00');
        currentView = 'daily';
        viewBtns.forEach(b => {
            b.classList.toggle('active', b.dataset.view === 'daily');
        });
        switchView('daily');
        updateCalendarTitle();
        // Scroll to calendar
        const cal = document.querySelector('.calendar-container');
        if (cal) cal.scrollIntoView({ behavior: 'smooth' });
    };

    // ── Filter Dropdown Logic ────────────────────────────────
    if (filterBtn && filterDropdown) {
        filterBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            filterDropdown.classList.toggle('show');
            filterBtn.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            filterDropdown.classList.remove('show');
            filterBtn.classList.remove('active');
        });

        filterDropdown.addEventListener('click', (e) => e.stopPropagation());

        const sortItems = filterDropdown.querySelectorAll('[data-sort]');
        sortItems.forEach(item => {
            item.addEventListener('click', () => {
                sortItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                currentSort = item.dataset.sort;
                renderTasks(activeFilter, searchInput ? searchInput.value : '');
                filterDropdown.classList.remove('show');
                filterBtn.classList.remove('active');
            });
        });

        const toggleComp = document.getElementById('toggleCompleted');
        if (toggleComp) {
            toggleComp.addEventListener('click', () => {
                showCompleted = !showCompleted;
                toggleComp.innerHTML = showCompleted ?
                    '<i class="fas fa-eye-slash"></i> Hide Completed' :
                    '<i class="fas fa-eye"></i> Show Completed';
                renderTasks(activeFilter, searchInput ? searchInput.value : '');
                filterDropdown.classList.remove('show');
                filterBtn.classList.remove('active');
            });
        }
    }

}); // END DOMContentLoaded