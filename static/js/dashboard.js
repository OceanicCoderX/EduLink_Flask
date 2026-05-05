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

            // Chart Initialization
            if (data.chart_data && window.Chart) {
                // Pie Chart
                const pieCtx = document.getElementById('activityPieChart');
                if (pieCtx) {
                    new Chart(pieCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Focus Time', 'Tasks Completed', 'Notes Created', 'Classrooms Joined', 'Communities Joined'],
                            datasets: [{
                                data: [
                                    data.chart_data.pie.focus_minutes,
                                    data.chart_data.pie.tasks_completed,
                                    data.chart_data.pie.notes_created,
                                    data.chart_data.pie.classrooms_joined,
                                    data.chart_data.pie.communities_joined
                                ],
                                backgroundColor: [
                                    '#5e72e4', // primary
                                    '#2dce89', // success
                                    '#f5365c', // danger
                                    '#fb6340', // warning
                                    '#11cdef'  // info
                                ],
                                borderWidth: 0,
                                hoverOffset: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        color: '#8898aa',
                                        padding: 20,
                                        font: { family: "'Inter', sans-serif", size: 12 }
                                    }
                                }
                            },
                            cutout: '70%'
                        }
                    });
                }

                // Line Chart
                const lineCtx = document.getElementById('progressLineChart');
                if (lineCtx) {
                    const renderLineChart = (range) => {
                        let labels = [];
                        let timeSpent = [];

                        if (range === 'daily') {
                            for (let i = 6; i >= 0; i--) {
                                let d = new Date(); d.setDate(d.getDate() - i);
                                labels.push(d.toISOString().split('T')[0]);
                            }
                            labels.forEach(date => {
                                const t = data.chart_data.line.daily_time.find(x => x.date === date);
                                timeSpent.push(t ? t.minutes : 0);
                            });
                            labels = labels.map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short' }));
                        } else if (range === 'weekly') {
                            labels = data.chart_data.line.weekly_time.map(x => x.date);
                            labels.sort();
                            if (labels.length > 4) labels = labels.slice(-4);
                            labels.forEach(date => {
                                const t = data.chart_data.line.weekly_time.find(x => x.date === date);
                                timeSpent.push(t ? t.minutes : 0);
                            });
                        } else if (range === 'monthly') {
                            labels = data.chart_data.line.monthly_time.map(x => x.date);
                            labels.sort();
                            if (labels.length > 12) labels = labels.slice(-12);
                            labels.forEach(date => {
                                const t = data.chart_data.line.monthly_time.find(x => x.date === date);
                                timeSpent.push(t ? t.minutes : 0);
                            });
                            labels = labels.map(d => {
                                const [y, m] = d.split('-');
                                const dateObj = new Date(y, m - 1);
                                return dateObj.toLocaleDateString('en-US', { month: 'short' });
                            });
                        }

                        if (window.progressLineChartInst) {
                            window.progressLineChartInst.destroy();
                        }

                        window.progressLineChartInst = new Chart(lineCtx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [
                                    {
                                        label: 'Time Spent (Minutes)',
                                        data: timeSpent,
                                        borderColor: '#5e72e4',
                                        backgroundColor: 'rgba(94, 114, 228, 0.1)',
                                        tension: 0.4,
                                        fill: true
                                    }
                                ]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: { position: 'top', labels: { color: '#8898aa', font: { family: "'Inter', sans-serif" } } }
                                },
                                scales: {
                                    y: { beginAtZero: true, grid: { color: 'rgba(136, 152, 170, 0.1)', borderDash: [5, 5] }, ticks: { color: '#8898aa', stepSize: 1 } },
                                    x: { grid: { display: false }, ticks: { color: '#8898aa' } }
                                }
                            }
                        });
                    };

                    renderLineChart('daily');

                    document.querySelectorAll('.chart-filter .filter-btn').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            document.querySelectorAll('.chart-filter .filter-btn').forEach(b => b.classList.remove('active'));
                            e.target.classList.add('active');
                            const range = e.target.getAttribute('data-range');
                            document.getElementById('lineChartTitle').textContent = `Website Time Spent (${range.charAt(0).toUpperCase() + range.slice(1)})`;
                            renderLineChart(range);
                        });
                    });
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

// PDF Report Download Logic
const downloadReportBtn = document.getElementById('downloadReportBtn');
if (downloadReportBtn) {
    downloadReportBtn.addEventListener('click', () => {
        const timeframe = document.getElementById('reportTimeframe').value;
        const originalText = downloadReportBtn.innerHTML;
        downloadReportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        downloadReportBtn.disabled = true;

        fetch(`/api/progress-report?range=${timeframe}`)
            .then(r => r.json())
            .then(data => {
                // Populate template
                document.getElementById('pdfReportRange').textContent = timeframe.charAt(0).toUpperCase() + timeframe.slice(1) + ' Report';
                document.getElementById('pdfFocusMins').textContent = data.focus_minutes;
                document.getElementById('pdfTasksCount').textContent = data.tasks.length;
                document.getElementById('pdfNotesCount').textContent = data.notes.length;

                document.getElementById('pdfTasksList').innerHTML = data.tasks.length ?
                    data.tasks.map(t => `<li style="margin-bottom: 6px;"><span style="color:#2dce89">●</span> ${t.title} <span style="color:#adb5bd;font-size:12px">(${t.date})</span></li>`).join('') :
                    '<li style="color:#adb5bd">No tasks completed.</li>';

                document.getElementById('pdfNotesList').innerHTML = data.notes.length ?
                    data.notes.map(n => `<li style="margin-bottom: 6px;"><span style="color:#fb6340">●</span> ${n.title} <span style="color:#adb5bd;font-size:12px">(${n.date})</span></li>`).join('') :
                    '<li style="color:#adb5bd">No notes created.</li>';

                document.getElementById('pdfClassroomsList').innerHTML = data.classrooms.length ?
                    data.classrooms.map(c => `<li style="margin-bottom: 6px;"><span style="color:#11cdef">●</span> ${c.name} <span style="color:#adb5bd;font-size:12px">(${c.date})</span></li>`).join('') :
                    '<li style="color:#adb5bd">No classrooms joined.</li>';

                document.getElementById('pdfCommunitiesList').innerHTML = data.communities.length ?
                    data.communities.map(c => `<li style="margin-bottom: 6px;"><span style="color:#f5365c">●</span> ${c.name} <span style="color:#adb5bd;font-size:12px">(${c.date})</span></li>`).join('') :
                    '<li style="color:#adb5bd">No communities joined.</li>';

                const element = document.getElementById('pdfReportTemplate');
                const chartsContainer = document.querySelector('.charts-grid');

                const generatePdf = () => {
                    // Clone the element to ensure html2canvas can read it properly
                    const clone = element.cloneNode(true);
                    clone.id = 'pdfReportTemplateClone';
                    clone.style.display = 'block';
                    clone.style.position = 'absolute';
                    clone.style.left = '0';
                    clone.style.top = '0';
                    clone.style.zIndex = '-1';
                    document.body.appendChild(clone);

                    const opt = {
                        margin: 0.5,
                        filename: `EduLink_${timeframe}_report.pdf`,
                        image: { type: 'jpeg', quality: 1 },
                        html2canvas: { scale: 2, useCORS: true, logging: true, windowWidth: 800 },
                        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                    };

                    html2pdf().set(opt).from(clone).save().then(() => {
                        document.body.removeChild(clone);
                        downloadReportBtn.innerHTML = originalText;
                        downloadReportBtn.disabled = false;
                        document.getElementById('dashboardSnapshot').style.display = 'none';
                    }).catch(err => {
                        console.error(err);
                        if (document.body.contains(clone)) document.body.removeChild(clone);
                        downloadReportBtn.innerHTML = originalText;
                        downloadReportBtn.disabled = false;
                    });
                };

                if (chartsContainer && typeof html2canvas !== 'undefined') {
                    // Capture the charts grid first
                    html2canvas(chartsContainer, { scale: 2, useCORS: true }).then(canvas => {
                        const imgData = canvas.toDataURL('image/jpeg', 1.0);
                        const snapImg = document.getElementById('dashboardSnapshot');
                        snapImg.src = imgData;
                        snapImg.style.display = 'block';
                        generatePdf();
                    }).catch(err => {
                        console.error("Screenshot error:", err);
                        generatePdf();
                    });
                } else {
                    generatePdf();
                }
            })
            .catch(err => {
                console.error(err);
                downloadReportBtn.innerHTML = originalText;
                downloadReportBtn.disabled = false;
                alert('Failed to generate report.');
            });
    });
}