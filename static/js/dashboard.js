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

// Load User Data
function loadUserData() {
    const userData = JSON.parse(localStorage.getItem('edulink_user') || '{}');
    if (userData.fullName) {
        document.getElementById('userName').textContent = userData.fullName.split(' ')[0];
    }

    // Load stats from localStorage
    const stats = JSON.parse(localStorage.getItem('edulink_stats') || '{}');
    if (stats.totalStudyTime) {
        document.getElementById('totalStudyTime').textContent = stats.totalStudyTime;
    }
    if (stats.tasksCompleted) {
        document.getElementById('tasksCompleted').textContent = stats.tasksCompleted;
    }
    if (stats.pomodoroSessions) {
        document.getElementById('pomodoroSessions').textContent = stats.pomodoroSessions;
    }
    if (stats.studyStreak) {
        document.getElementById('studyStreak').textContent = stats.studyStreak;
    }
}

loadUserData();

// Logout Function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('edulink_logged_in');
        window.location.href = '../index.html';
    }
}

// Study Time Chart
const studyTimeCtx = document.getElementById('studyTimeChart').getContext('2d');
const studyTimeChart = new Chart(studyTimeCtx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Study Hours',
            data: [3.5, 4.2, 2.8, 5.1, 3.9, 4.5, 2.5],
            borderColor: 'rgb(94, 114, 228)',
            backgroundColor: 'rgba(94, 114, 228, 0.1)',
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(94, 114, 228)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Task Distribution Chart
const taskDistCtx = document.getElementById('taskDistributionChart').getContext('2d');
const taskDistChart = new Chart(taskDistCtx, {
    type: 'doughnut',
    data: {
        labels: ['Study', 'Work', 'Personal', 'Other'],
        datasets: [{
            data: [45, 25, 20, 10],
            backgroundColor: [
                'rgb(94, 114, 228)',
                'rgb(251, 137, 64)',
                'rgb(45, 206, 177)',
                'rgb(245, 73, 74)'
            ],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    usePointStyle: true
                }
            }
        }
    }
});

// Weekly Activity Chart
const weeklyCtx = document.getElementById('weeklyActivityChart').getContext('2d');
const weeklyChart = new Chart(weeklyCtx, {
    type: 'bar',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Pomodoro Sessions',
            data: [8, 10, 6, 12, 9, 11, 5],
            backgroundColor: 'rgba(94, 114, 228, 0.8)',
            borderRadius: 8
        }, {
            label: 'Tasks Completed',
            data: [5, 7, 4, 8, 6, 9, 3],
            backgroundColor: 'rgba(45, 206, 177, 0.8)',
            borderRadius: 8
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Chart Filter Buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        // Update chart data based on period (you can customize this)
        const period = this.dataset.period;
        // Add logic to update chart data
    });
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

// Auto-hide sidebar on mobile when clicking outside
document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
    }
});