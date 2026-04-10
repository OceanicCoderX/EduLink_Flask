// Notes Data
let notes = [];
let currentNoteId = null;
let currentCategory = 'all';

// helper functions for storage/back-end sync
function loadNotesFromLocal() {
    const saved = localStorage.getItem('edulink_notes');
    if (saved) {
        notes = JSON.parse(saved);
        renderNotesList();
    }
}

function saveNotesToLocal() {
    localStorage.setItem('edulink_notes', JSON.stringify(notes));
}

function fetchNotesFromServer() {
    fetch('/api/notes')
        .then(res => res.json())
        .then(data => {
            notes = data.map(n => ({
                id: n.notes_id,
                title: n.notes_title || 'Untitled Note',
                content: n.notes_description || '',
                category: n.category || 'general',
                tags: n.tags ? n.tags.split(',').map(t => t.trim()).filter(t => t) : [],
                createdAt: n.created_date || new Date().toISOString(),
                updatedAt: n.created_date || new Date().toISOString()
            }));
            renderNotesList();
        })
        .catch(err => {
            console.error('server load failed, falling back to local', err);
            loadNotesFromLocal();
        });
}

function saveNoteToServer(note) {
    const form = new FormData();
    const isUpdate = note.id && !String(note.id).startsWith('temp');

    if (isUpdate) form.append('notes_id', note.id);
    form.append('notes_title', note.title);
    form.append('notes_description', note.content);
    form.append('category', note.category);
    form.append('tags', note.tags.join(', '));

    const endpoint = isUpdate ? '/api/update-note' : '/api/save-note';

    return fetch(endpoint, { method: 'POST', body: form })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.notes_id) {
                const oldId = note.id;
                note.id = data.notes_id;
                // if we had a temporary id, update array and re-render selection
                if (String(oldId).startsWith('temp')) {
                    renderNotesList();
                    if (currentNoteId === oldId) {
                        currentNoteId = note.id;
                    }
                }
            }
            return data;
        });
}

function deleteNoteFromServer(id) {
    const form = new FormData();
    form.append('notes_id', id);
    fetch('/api/delete-note', { method: 'POST', body: form })
        .then(res => res.json())
        .then(data => {
            if (!data.success) console.warn('deleteNoteFromServer failed', data);
        })
        .catch(err => console.error('deleteNoteFromServer error', err));
}

// Load saved data
window.addEventListener('load', () => {
    // Load user profile
    const userData = JSON.parse(localStorage.getItem('edulink_user'));
    if (userData) {
        if (document.getElementById('profileName')) document.getElementById('profileName').textContent = userData.fullName || 'Student';
        if (document.getElementById('profileEmail')) document.getElementById('profileEmail').textContent = userData.email || 'student@edulink.com';
        if (document.getElementById('profileAvatar')) document.getElementById('profileAvatar').textContent = (userData.fullName || 'S')[0].toUpperCase();
    }

    // fetch notes from server, fallback to local storage
    fetchNotesFromServer();

    // save button handler
    const saveBtn = document.getElementById('saveNoteBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', manualSaveNote);
    }
    updateSaveBtnState();
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
    const tempId = 'temp' + Date.now();
    const newNote = {
        id: tempId, // temporary, replaced when server responds
        title: 'Untitled Note',
        content: '',
        category: 'general',
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    notes.unshift(newNote);
    saveNotesToLocal();
    renderNotesList();
    selectNote(newNote.id);
    markUnsaved();

    // push to backend (server will return a real numeric id)
    saveNoteToServer(newNote).then(() => {
        // after server assigns id, we can consider it saved
        unsavedChanges = false;
        updateSaveBtnState();
    });
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

    if (document.getElementById('noteTitleInput')) document.getElementById('noteTitleInput').value = note.title;
    if (document.getElementById('noteContent')) document.getElementById('noteContent').value = note.content;
    if (document.getElementById('categorySelect')) document.getElementById('categorySelect').value = note.category;
    if (document.getElementById('tagsInput')) document.getElementById('tagsInput').value = note.tags.join(', ');

    updateWordCount();
    renderNotesList();

    // reset save state
    unsavedChanges = false;
    document.getElementById('saveStatus').innerHTML = '<i class="fas fa-check-circle"></i><span>All changes saved</span>';
    updateSaveBtnState();
}

// manual-save workflow
let unsavedChanges = false;
function updateSaveBtnState() {
    const btn = document.getElementById('saveNoteBtn');
    if (!btn) return;
    btn.disabled = !unsavedChanges;
}

function markUnsaved() {
    unsavedChanges = true;
    const saveStatus = document.getElementById('saveStatus');
    saveStatus.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>Unsaved changes</span>';
    updateSaveBtnState();
}

function manualSaveNote() {
    if (!currentNoteId) return;
    const note = notes.find(n => n.id === currentNoteId);
    if (!note) return;

    note.title = document.getElementById('noteTitleInput') ? document.getElementById('noteTitleInput').value || 'Untitled Note' : 'Untitled Note';
    note.content = document.getElementById('noteContent') ? document.getElementById('noteContent').value : '';
    note.category = document.getElementById('categorySelect') ? document.getElementById('categorySelect').value : 'general';
    note.tags = document.getElementById('tagsInput') ? document.getElementById('tagsInput').value.split(',').map(t => t.trim()).filter(t => t) : [];
    note.updatedAt = new Date().toISOString();

    saveNotesToLocal();
    renderNotesList();

    const saveStatus = document.getElementById('saveStatus');
    const saveBtn = document.getElementById('saveNoteBtn');
    if (saveBtn) saveBtn.disabled = true;
    saveStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Saving...</span>';

    saveNoteToServer(note).then(() => {
        saveStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>All changes saved</span>';
        unsavedChanges = false;
        updateSaveBtnState();
    }).catch(err => {
        console.error('manualSaveNote error', err);
        saveStatus.innerHTML = '<i class="fas fa-times-circle"></i><span>Save failed</span>';
    });
}


if (document.getElementById('noteTitleInput')) document.getElementById('noteTitleInput').addEventListener('input', markUnsaved);
if (document.getElementById('noteContent')) {
    document.getElementById('noteContent').addEventListener('input', () => {
        updateWordCount();
        markUnsaved();
    });
}
if (document.getElementById('categorySelect')) document.getElementById('categorySelect').addEventListener('change', markUnsaved);
if (document.getElementById('tagsInput')) document.getElementById('tagsInput').addEventListener('input', markUnsaved);

// Update Word Count
function updateWordCount() {
    const content = document.getElementById('noteContent').value;
    const words = content.trim().split(/\s+/).filter(w => w.length > 0).length;
    const chars = content.length;

    document.getElementById('wordCount').textContent = `${words} words`;
    document.getElementById('charCount').textContent = `${chars} characters`;
}

// legacy compatibility function (calls new local helper)
function saveNotes() {
    saveNotesToLocal();
}

// Category Filter
document.querySelectorAll('.category-tag').forEach(tag => {
    tag.addEventListener('click', function () {
        document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        currentCategory = this.dataset.category;
        renderNotesList();
    });
});

// Search Notes
document.getElementById('searchNotes').addEventListener('input', function (e) {
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

        saveNotesToLocal();
        deleteNoteFromServer(noteId);
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

// Settings
const settingsBtn = document.getElementById('settingsBtn');
if (settingsBtn) {
    settingsBtn.addEventListener('click', () => {
        alert('Settings panel will be integrated soon!');
    });
}

// Text Formatting
function formatText(command) {
    const textarea = document.getElementById('noteContent');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    let formattedText = '';
    switch (command) {
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
    markUnsaved();
}