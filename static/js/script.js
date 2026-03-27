/* =========================================================
   EDULINK - COMBINED SCRIPT.JS
   Includes:
   - Theme System
   - Profile Management (No DB persistence yet)
   - Task Management (In-memory only)
   - Calendar Views
   - Notifications
   - Utility Functions
   NOTE:
   - Only Authentication can use localStorage
   - All other data currently in-memory (ready for Flask API later)
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

// Profile State
let currentAvatarType = 'initials';
let currentAvatarData = 'JD';
let currentBackgroundImage = '';

// Task State (NO localStorage now)
let tasks = [];
let currentView = 'daily';
let currentDate = new Date();
let editingTaskId = null;
let selectedPriority = 'medium';
let timeEstimateEnabled = false;
let pomodoroEnabled = false;


/* =========================================================
   THEME MANAGEMENT (Shared)
========================================================= */

function initializeTheme() {
    const lightThemeBtn = document.getElementById('lightThemeBtn');
    const darkThemeBtn = document.getElementById('darkThemeBtn');

    if (!lightThemeBtn || !darkThemeBtn) return;
    // Load saved theme from localStorage (use unified key 'edulink_theme')
    const saved = localStorage.getItem('edulink_theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    if (saved === 'dark') {
        darkThemeBtn.classList.add('active');
        lightThemeBtn.classList.remove('active');
    } else {
        lightThemeBtn.classList.add('active');
        darkThemeBtn.classList.remove('active');
    }

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
}


/* =========================================================
   PROFILE MANAGEMENT (NO localStorage persistence)
========================================================= */

function updateProfileDisplay() {
    const fullName = document.getElementById('fullName')?.value || '';
    const username = document.getElementById('username')?.value || '';
    const location = document.getElementById('location')?.value || '';
    const bio = document.getElementById('bio')?.value || '';

    if (document.getElementById('displayName'))
        document.getElementById('displayName').textContent = fullName;

    if (document.getElementById('displayUsername'))
        document.getElementById('displayUsername').textContent = '@' + username;

    if (document.getElementById('displayLocation'))
        document.getElementById('displayLocation').textContent = location;

    if (document.getElementById('displayBio'))
        document.getElementById('displayBio').textContent = bio;
}

function setupProfileForm() {
    const form = document.getElementById('personalInfoForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        updateProfileDisplay();
        showNotification('Profile updated (temporary memory only)');
    });
}


/* =========================================================
   TASK MANAGEMENT (IN-MEMORY ONLY)
========================================================= */

function renderTasks(filter = 'all', searchQuery = '') {
    const tasksList = document.getElementById('tasksList');
    const emptyState = document.getElementById('emptyState');

    if (!tasksList) return;

    let filteredTasks = tasks;

    if (filter === 'completed')
        filteredTasks = tasks.filter(t => t.status === 'completed');

    if (filter === 'pending')
        filteredTasks = tasks.filter(t => t.status === 'pending');

    if (searchQuery)
        filteredTasks = filteredTasks.filter(t =>
            t.title.toLowerCase().includes(searchQuery.toLowerCase())
        );

    tasksList.innerHTML = '';

    if (filteredTasks.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    filteredTasks.forEach(task => {
        tasksList.innerHTML += createTaskHTML(task);
    });
}

function createTaskHTML(task) {
    return `
        <div class="task-item ${task.priority} ${task.status}">
            <div class="task-content">
                <div class="task-title">${task.title}</div>
                <div class="priority-badge">${task.priority}</div>
            </div>
        </div>
    `;
}

function addTask(taskData) {
    tasks.push(taskData);
    renderTasks();
}

function deleteTask(taskId) {
    tasks = tasks.filter(t => t.id !== taskId);
    renderTasks();
    showNotification('Task deleted');
}


/* =========================================================
   CALENDAR MANAGEMENT
========================================================= */

function updateCalendarTitle() {
    const titleEl = document.getElementById('calendarTitle');
    if (!titleEl) return;

    titleEl.textContent = currentDate.toDateString();
}


/* =========================================================
   NOTIFICATION SYSTEM (Merged Version)
========================================================= */

function showNotification(message) {
    const notification = document.createElement('div');

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #5e72e4, #825ee4);
        color: white;
        padding: 14px 20px;
        border-radius: 10px;
        z-index: 9999;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}


/* =========================================================
   MODAL UTILITIES
========================================================= */

function openModal(modalId) {
    document.getElementById(modalId)?.classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId)?.classList.remove('active');
}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener('DOMContentLoaded', function () {
    initializeTheme();
    setupProfileForm();
    renderTasks();
    updateCalendarTitle();
});


/* =========================================================
   GLOBAL ANIMATIONS
========================================================= */

const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from { transform: translateX(300px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
`;
document.head.appendChild(style);
