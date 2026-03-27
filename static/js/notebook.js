 // Notes Data
        let notes = [];
        let currentNoteId = null;
        let currentCategory = 'all';

        // Load saved data
        window.addEventListener('load', () => {
            // Load user profile
            const userData = JSON.parse(localStorage.getItem('edulink_user'));
            if (userData) {
                document.getElementById('profileName').textContent = userData.fullName || 'Student';
                document.getElementById('profileEmail').textContent = userData.email || 'student@edulink.com';
                document.getElementById('profileAvatar').textContent = (userData.fullName || 'S')[0].toUpperCase();
            }

            // Load notes
            const savedNotes = localStorage.getItem('edulink_notes');
            if (savedNotes) {
                notes = JSON.parse(savedNotes);
                renderNotesList();
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

        // Create New Note
        function createNewNote() {
            const newNote = {
                id: Date.now(),
                title: 'Untitled Note',
                content: '',
                category: 'general',
                tags: [],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };

            notes.unshift(newNote);
            saveNotes();
            renderNotesList();
            selectNote(newNote.id);
        }

        document.getElementById('newNoteBtn').addEventListener('click', createNewNote);

        // Render Notes List
        function renderNotesList() {
            const notesList = document.getElementById('notesList');
            notesList.innerHTML = '';

            const filteredNotes = currentCategory === 'all' 
                ? notes 
                : notes.filter(note => note.category === currentCategory);

            if (filteredNotes.length === 0) {
                notesList.innerHTML = '<div style="padding: 40px 20px; text-align: center; color: var(--text-muted);">No notes found</div>';
                return;
            }

            filteredNotes.forEach(note => {
                const noteItem = document.createElement('div');
                noteItem.className = 'note-item';
                if (note.id === currentNoteId) noteItem.classList.add('active');

                const categoryEmoji = {
                    'general': '📚',
                    'physics': '🔬',
                    'chemistry': '🧪',
                    'math': '📐',
                    'biology': '🧬',
                    'coding': '💻'
                };

                const preview = note.content.substring(0, 60) || 'No content';
                const date = new Date(note.updatedAt).toLocaleDateString();

                noteItem.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div class="note-title">${note.title}</div>
                            <div class="note-preview">${preview}</div>
                            <div class="note-meta">
                                <span class="note-category">
                                    <span>${categoryEmoji[note.category]}</span>
                                    <span>${note.category}</span>
                                </span>
                                <span>${date}</span>
                            </div>
                        </div>
                        <button class="delete-note-btn" onclick="deleteNote(${note.id}, event)" style="background: none; border: none; color: var(--accent-2); cursor: pointer; padding: 4px 8px; font-size: 16px;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;

                noteItem.addEventListener('click', () => selectNote(note.id));
                notesList.appendChild(noteItem);
            });
        }

        // Select Note
        function selectNote(noteId) {
            currentNoteId = noteId;
            const note = notes.find(n => n.id === noteId);

            if (!note) return;

            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('editorContainer').style.display = 'flex';

            document.getElementById('noteTitleInput').value = note.title;
            document.getElementById('noteContent').value = note.content;
            document.getElementById('categorySelect').value = note.category;
            document.getElementById('tagsInput').value = note.tags.join(', ');

            updateWordCount();
            renderNotesList();
        }

        // Auto-save Note
        let saveTimeout;
        function autoSaveNote() {
            clearTimeout(saveTimeout);
            
            const saveStatus = document.getElementById('saveStatus');
            saveStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Saving...</span>';

            saveTimeout = setTimeout(() => {
                if (currentNoteId) {
                    const note = notes.find(n => n.id === currentNoteId);
                    if (note) {
                        note.title = document.getElementById('noteTitleInput').value || 'Untitled Note';
                        note.content = document.getElementById('noteContent').value;
                        note.category = document.getElementById('categorySelect').value;
                        note.tags = document.getElementById('tagsInput').value.split(',').map(t => t.trim()).filter(t => t);
                        note.updatedAt = new Date().toISOString();
                        
                        saveNotes();
                        renderNotesList();

                        saveStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>All changes saved</span>';
                    }
                }
            }, 1000);
        }

        document.getElementById('noteTitleInput').addEventListener('input', autoSaveNote);
        document.getElementById('noteContent').addEventListener('input', () => {
            updateWordCount();
            autoSaveNote();
        });
        document.getElementById('categorySelect').addEventListener('change', autoSaveNote);
        document.getElementById('tagsInput').addEventListener('input', autoSaveNote);

        // Update Word Count
        function updateWordCount() {
            const content = document.getElementById('noteContent').value;
            const words = content.trim().split(/\s+/).filter(w => w.length > 0).length;
            const chars = content.length;

            document.getElementById('wordCount').textContent = `${words} words`;
            document.getElementById('charCount').textContent = `${chars} characters`;
        }

        // Save Notes to LocalStorage
        function saveNotes() {
            localStorage.setItem('edulink_notes', JSON.stringify(notes));
        }

        // Category Filter
        document.querySelectorAll('.category-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                currentCategory = this.dataset.category;
                renderNotesList();
            });
        });

        // Search Notes
        document.getElementById('searchNotes').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const noteItems = document.querySelectorAll('.note-item');

            noteItems.forEach(item => {
                const title = item.querySelector('.note-title').textContent.toLowerCase();
                const preview = item.querySelector('.note-preview').textContent.toLowerCase();

                if (title.includes(searchTerm) || preview.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });

        // Delete Note
        function deleteNote(noteId, event) {
            event.stopPropagation(); // Prevents note selection when clicking delete
            
            if (confirm('Are you sure you want to delete this note?')) {
                notes = notes.filter(n => n.id !== noteId);
                
                if (currentNoteId === noteId) {
                    currentNoteId = null;
                    document.getElementById('emptyState').style.display = 'flex';
                    document.getElementById('editorContainer').style.display = 'none';
                }
                
                saveNotes();
                renderNotesList();
            }
        }

        // Export Dropdown Toggle
        document.getElementById('exportBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            const dropdown = document.getElementById('exportDropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            document.getElementById('exportDropdown').style.display = 'none';
        });

        // Export Note Function
        function exportNote(format) {
            if (!currentNoteId) {
                alert('Please select a note to export');
                return;
            }

            const note = notes.find(n => n.id === currentNoteId);
            
            if (format === 'txt') {
                const blob = new Blob([note.content], { type: 'text/plain' });
                downloadFile(blob, `${note.title}.txt`);
            } 
            else if (format === 'pdf') {
                // Create PDF content
                const pdfContent = `
                    <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; padding: 40px; }
                            h1 { color: #5e72e4; }
                            .meta { color: #6c757d; font-size: 14px; margin-bottom: 20px; }
                        </style>
                    </head>
                    <body>
                        <h1>${note.title}</h1>
                        <div class="meta">Category: ${note.category} | Created: ${new Date(note.createdAt).toLocaleDateString()}</div>
                        <pre style="white-space: pre-wrap; font-family: inherit;">${note.content}</pre>
                    </body>
                    </html>
                `;
                
                const blob = new Blob([pdfContent], { type: 'text/html' });
                downloadFile(blob, `${note.title}.html`);
                alert('Note exported as HTML. You can open it in browser and print as PDF (Ctrl+P)');
            } 
            else if (format === 'excel') {
                // Create CSV format (Excel compatible)
                const csv = `Title,Category,Created,Content\n"${note.title}","${note.category}","${new Date(note.createdAt).toLocaleDateString()}","${note.content.replace(/"/g, '""')}"`;
                const blob = new Blob([csv], { type: 'text/csv' });
                downloadFile(blob, `${note.title}.csv`);
            }
            
            document.getElementById('exportDropdown').style.display = 'none';
        }

        function downloadFile(blob, filename) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }

        // Save to Google Drive
        document.getElementById('driveBtn').addEventListener('click', () => {
            alert('Google Drive integration will be available soon!');
        });

        // AI Format
        document.getElementById('aiFormatBtn').addEventListener('click', () => {
            alert('AI formatting feature coming soon! This will structure your notes automatically.');
        });

        // Share Note
        document.getElementById('shareNoteBtn').addEventListener('click', () => {
            alert('Sharing feature coming soon!');
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => {
            alert('Settings panel will be integrated soon!');
        });

        // Text Formatting
        function formatText(command) {
            const textarea = document.getElementById('noteContent');
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const selectedText = textarea.value.substring(start, end);

            let formattedText = '';
            switch(command) {
                case 'bold':
                    formattedText = `**${selectedText}**`;
                    break;
                case 'italic':
                    formattedText = `*${selectedText}*`;
                    break;
                case 'underline':
                    formattedText = `__${selectedText}__`;
                    break;
                case 'strikethrough':
                    formattedText = `~~${selectedText}~~`;
                    break;
                default:
                    formattedText = selectedText;
            }

            textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start, start + formattedText.length);
            autoSaveNote();
        }