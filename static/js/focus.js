        // Timer State
        let currentMode = 'classic';
        let focusTime = 25 * 60;
        let breakTime = 5 * 60;
        let currentTime = focusTime;
        let isRunning = false;
        let isBreak = false;
        let timerInterval = null;
        let currentTask = 'Study';
        
        // Stats
        let sessionsCompleted = 0;
        let totalFocusMinutes = 0;
        let currentStreak = 0;

        // DOM Elements
        const timerDisplay = document.getElementById('timerDisplay');
        const timerLabel = document.getElementById('timerLabel');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const circleProgress = document.getElementById('circleProgress');
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const modeBtns = document.querySelectorAll('.mode-btn') || [];
        const taskSelect = document.getElementById('taskSelect');
        const customTaskInput = document.getElementById('customTaskInput');
        const customTimeModal = document.getElementById('customTimeModal');
        const breakModal = document.getElementById('breakModal');
        // Sound via Web Audio API (no audio element needed)

        // Initialize
        updateDisplay();
        initializeEventListeners();
        loadStatsFromBackend();



        function initializeEventListeners() {
            // Mobile Menu
            if (mobileMenuBtn) {
                mobileMenuBtn.addEventListener('click', () => {
                    const sb = document.getElementById('sidebar');
                    if (sb) sb.classList.toggle('open');
                });
            }

            document.addEventListener('click', (e) => {
                const sidebarEl = document.getElementById('sidebar');
                if (window.innerWidth <= 968 && sidebarEl && mobileMenuBtn) {
                    if (!sidebarEl.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                        sidebarEl.classList.remove('open');
                    }
                }
            });

        }

        function loadStatsFromBackend() {
            fetch('/api/get-focus-stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('sessionsCount').textContent = data.total_sessions;
                    document.getElementById('totalTime').textContent = data.total_sessions;
                    document.getElementById('streakCount').textContent = data.total_stacks;

                    // JS variables bhi update karo taaki current session sahi calculate ho
                    sessionsCompleted = data.total_sessions;
                    totalFocusMinutes = data.total_minutes;
                    currentStreak = data.total_stacks;
                })
                .catch(error => console.error('Stats load error:', error));
        }
        
        // Theme Toggle
        const lightThemeBtn = document.getElementById('lightThemeBtn');
        const darkThemeBtn = document.getElementById('darkThemeBtn');

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

        // Load saved theme
        const savedTheme = localStorage.getItem('edulink_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark' && darkThemeBtn) {
            darkThemeBtn.classList.add('active');
            if (lightThemeBtn) lightThemeBtn.classList.remove('active');
        }

        // Mode Selection
        modeBtns.forEach(btn => {
            if (!btn) return;
            btn.addEventListener('click', () => {
                if (isRunning && !confirm('Timer is running! Switch mode?')) return;
                
                stopTimer();
                modeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMode = btn.dataset.mode;

                if (currentMode === 'classic') {
                    focusTime = 25 * 60;
                    breakTime = 5 * 60;
                    resetTimer();
                } else if (currentMode === 'deep') {
                    focusTime = 50 * 60;
                    breakTime = 10 * 60;
                    resetTimer();
                } else if (currentMode === 'custom') {
                    customTimeModal.style.display = 'flex';
                }
            });
        });

        // Custom Time Modal
        if (document.getElementById('closeCustomModal')) {
            document.getElementById('closeCustomModal').addEventListener('click', () => {
                customTimeModal.style.display = 'none';
                modeBtns[0].classList.add('active');
                modeBtns[2].classList.remove('active');
            });
        }

        if (document.getElementById('cancelCustom')) {
            document.getElementById('cancelCustom').addEventListener('click', () => {
                customTimeModal.style.display = 'none';
                modeBtns[0].classList.add('active');
                modeBtns[2].classList.remove('active');
            });
        }

        if (document.getElementById('setCustomTime')) {
            document.getElementById('setCustomTime').addEventListener('click', () => {
            const customFocus = parseInt(document.getElementById('customFocusTime').value);
            const customBreak = parseInt(document.getElementById('customBreakTime').value);

            if (customFocus > 0 && customBreak > 0) {
                focusTime = customFocus * 60;
                breakTime = customBreak * 60;
                resetTimer();
                customTimeModal.style.display = 'none';
            } else {
                alert('Please enter valid time values!');
            }
        });
        }

        // Task Selection
        if (taskSelect) {
            taskSelect.addEventListener('change', function() {
                if (this.value === 'custom') {
                    this.style.display = 'none';
                    if (customTaskInput) {
                        customTaskInput.style.display = 'block';
                        customTaskInput.focus();
                    }
                } else {
                    currentTask = this.value;
                }
            });
        }

        if (customTaskInput) {
            customTaskInput.addEventListener('blur', function() {
                if (this.value.trim()) {
                    currentTask = this.value.trim();
                }
                this.style.display = 'none';
                if (taskSelect) {
                    taskSelect.style.display = 'block';
                    taskSelect.value = 'Study';
                }
            });

            customTaskInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') this.blur();
            });
        }

        // Timer Functions
        function updateDisplay() {
            const minutes = Math.floor(currentTime / 60);
            const seconds = currentTime % 60;
            const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            timerDisplay.textContent = display;
            document.title = `${display} - Focus Timer`;
            
            // Update circle progress
            const totalTime = isBreak ? breakTime : focusTime;
            const progress = (currentTime / totalTime) * 1130.97;
            circleProgress.style.strokeDashoffset = 1130.97 - progress;
        }

        function startTimer() {
            isRunning = true;
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Running...';
            pauseBtn.disabled = false;

            timerInterval = setInterval(() => {
                if (currentTime > 0) {
                    currentTime--;
                    updateDisplay();
                } else {
                    completeSession();
                }
            }, 1000);
        }

        function pauseTimer() {
            clearInterval(timerInterval);
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
            pauseBtn.disabled = true;
        }

        function resetTimer() {
            stopTimer();
            isBreak = false;
            currentTime = focusTime;
            updateDisplay();
            timerLabel.textContent = 'Focus Time';
        }

        function stopTimer() {
            isRunning = false;
            clearInterval(timerInterval);
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start';
            pauseBtn.disabled = true;
        }

        function completeSession() {
            stopTimer();
            playBreakSound();

            if (!isBreak) {
                sessionsCompleted++;
                totalFocusMinutes += Math.floor(focusTime / 60);
                currentStreak++;    
                updateStats();
                sendSessionToBackend();    // 🔥 SEND DATA TO BACKEND
                breakModal.style.display = 'flex';
            } else {
                resetTimer();
                alert('Break completed! Ready for another session? 💪');
            }
        }

        function updateStats() {
            if (document.getElementById('sessionsCount')) document.getElementById('sessionsCount').textContent = sessionsCompleted;
            if (document.getElementById('totalTime')) document.getElementById('totalTime').textContent = sessionsCompleted;
            if (document.getElementById('streakCount')) document.getElementById('streakCount').textContent = currentStreak;
        }


        // Send to BackEnd
        function sendSessionToBackend() {
            const formData = new FormData();
            formData.append("task", currentTask);
            // Send only the current session duration, not the historical total
            formData.append("duration", Math.floor(focusTime / 60));
            formData.append("sessions", 1);
            formData.append("stacks", 1);

            fetch('/api/save-focus', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) console.log('Focus saved');
            })
            .catch(error => console.error('Error:', error));
        }


        // Break Modal
        if (document.getElementById('startBreakBtn')) {
            document.getElementById('startBreakBtn').addEventListener('click', () => {
                breakModal.style.display = 'none';
                isBreak = true;
                currentTime = breakTime;
                timerLabel.textContent = 'Break Time';
                updateDisplay();
                startTimer();
            });
        }

        if (document.getElementById('skipBreakBtn')) {
            document.getElementById('skipBreakBtn').addEventListener('click', () => {
                breakModal.style.display = 'none';
                resetTimer();
            });
        }

        // Event Listeners
        if (startBtn) startBtn.addEventListener('click', startTimer);
        if (pauseBtn) pauseBtn.addEventListener('click', pauseTimer);
        resetBtn.addEventListener('click', () => {
            if ((isRunning || currentTime !== focusTime) && confirm('Reset timer?')) {
                resetTimer();
            }
        });

        // Settings Button
        const settingsBtnEl = document.getElementById('settingsBtn');
        if (settingsBtnEl) settingsBtnEl.addEventListener('click', () => {
            alert('Settings panel will be integrated soon!');
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

        

        // ── Web Audio API: Loud Notification Sound ──────────────
        function playBreakSound() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();

                // 3-tone ding: high → mid → low (pleasant alarm)
                const tones = [
                    { freq: 880,  start: 0,    dur: 0.35 },
                    { freq: 659,  start: 0.38, dur: 0.35 },
                    { freq: 523,  start: 0.76, dur: 0.55 },
                ];

                tones.forEach(({ freq, start, dur }) => {
                    const osc  = ctx.createOscillator();
                    const gain = ctx.createGain();

                    osc.connect(gain);
                    gain.connect(ctx.destination);

                    osc.type = 'sine';
                    osc.frequency.value = freq;

                    // Loud attack, smooth decay
                    gain.gain.setValueAtTime(0, ctx.currentTime + start);
                    gain.gain.linearRampToValueAtTime(1.0, ctx.currentTime + start + 0.02);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);

                    osc.start(ctx.currentTime + start);
                    osc.stop(ctx.currentTime + start + dur);
                });

                // Close context after all tones finish
                setTimeout(() => ctx.close(), 2000);
            } catch (e) {
                console.warn('Web Audio API not supported:', e);
            }
        }

        // Prevent page close during timer
        window.addEventListener('beforeunload', (e) => {
            if (isRunning) {
                e.preventDefault();
                e.returnValue = '';
            }
        });