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

    // Init resizing
    initResizing();

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

        const preview = (note.content || '').replace(/<[^>]*>/g, '').substring(0, 60) || 'No content';
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
                        <button class="delete-note-btn" onclick="deleteNote('${note.id}', event)" style="background: none; border: none; color: var(--accent-2); cursor: pointer; padding: 4px 8px; font-size: 16px;">
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
    if (document.getElementById('noteContent')) {
        document.getElementById('noteContent').innerHTML = note.content;
    }
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
    note.content = document.getElementById('noteContent') ? document.getElementById('noteContent').innerHTML : '';
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

let lastSelectionRange = null;
if (document.getElementById('noteContent')) {
    const editor = document.getElementById('noteContent');
    editor.addEventListener('input', () => {
        updateWordCount();
        markUnsaved();
    });

    // Save selection range on blur
    editor.addEventListener('blur', () => {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            lastSelectionRange = selection.getRangeAt(0);
        }
    });

    // If focus is regained, restore or update range
    editor.addEventListener('mouseup', () => {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            lastSelectionRange = selection.getRangeAt(0);
        }
    });
}
if (document.getElementById('categorySelect')) document.getElementById('categorySelect').addEventListener('change', markUnsaved);
if (document.getElementById('tagsInput')) document.getElementById('tagsInput').addEventListener('input', markUnsaved);

// Update Word Count
function updateWordCount() {
    const content = document.getElementById('noteContent').innerText || '';
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

// AI Format
const aiFormatBtn = document.getElementById('aiFormatBtn');
if (aiFormatBtn) {
    aiFormatBtn.addEventListener('click', () => {
        alert('AI formatting feature coming soon! This will structure your notes automatically.');
    });
}

// Export Note Function
function exportNote(format) {
    if (!currentNoteId) {
        alert('Please select a note to export');
        return;
    }

    const note = notes.find(n => n.id === currentNoteId);

    if (format === 'txt') {
        const text = (note.content || '').replace(/<[^>]*>/g, '');
        const blob = new Blob([text], { type: 'text/plain' });
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
                            img { max-width: 100%; border-radius: 8px; }
                        </style>
                    </head>
                    <body>
                        <h1>${note.title}</h1>
                        <div class="meta">Category: ${note.category} | Created: ${new Date(note.createdAt).toLocaleDateString()}</div>
                        <div class="content">${note.content}</div>
                    </body>
                    </html>
                `;

        const blob = new Blob([pdfContent], { type: 'text/html' });
        downloadFile(blob, `${note.title}.html`);
        alert('Note exported as HTML. You can open it in browser and print as PDF (Ctrl+P)');
    }
    else if (format === 'excel') {
        const text = (note.content || '').replace(/<[^>]*>/g, '').replace(/"/g, '""');
        const csv = `Title,Category,Created,Content\n"${note.title}","${note.category}","${new Date(note.createdAt).toLocaleDateString()}","${text}"`;
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

// Text Formatting
function formatText(command, value = null) {
    if (command === 'createLink') {
        const url = prompt('Enter the link URL:');
        if (url) document.execCommand(command, false, url);
    } else {
        document.execCommand(command, false, value);
    }
    document.getElementById('noteContent').focus();
    markUnsaved();
}

// Media Upload
function triggerMediaUpload() {
    document.getElementById('noteFileUtils').click();
}

function uploadNoteMedia(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];

    const fd = new FormData();
    fd.append('file', file);

    showToast('Uploading media...', 'info');

    fetch('/api/upload-file', { method: 'POST', body: fd })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const fullUrl = `${window.location.origin}/static/${data.file_path}`;
                if (data.file_type === 'image') {
                    const imgHtml = `
                        <div class="note-media-item" style="margin: 10px 0; border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; background: var(--bg-primary); max-width: 100%;">
                            <img src="${fullUrl}" alt="${data.file_original}" style="max-width:100%; display: block;">
                            <div style="padding: 8px 12px; border-top: 1px solid var(--border-color); display: flex; align-items: center; gap: 8px; font-size: 11px; background: var(--bg-secondary);">
                                <i class="fas fa-link" style="color: var(--primary); font-size: 10px;"></i>
                                <span style="color: var(--text-muted);">Direct Link:</span>
                                <a href="${fullUrl}" target="_blank" style="color: var(--primary); text-decoration: none; word-break: break-all; font-family: monospace;">${fullUrl}</a>
                            </div>
                        </div><p></p>`;
                    insertHtmlAtCursor(imgHtml);
                } else {
                    const fileHtml = `
                        <div class="note-media-item" style="margin: 10px 0; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-primary); overflow: hidden; max-width: 500px;">
                            <div style="padding: 12px; display: flex; align-items: center; gap: 12px;">
                                <div style="width: 48px; height: 48px; border-radius: 10px; background: rgba(94, 114, 228, 0.1); display: flex; align-items: center; justify-content: center; color: var(--primary); flex-shrink: 0;">
                                    <i class="fas fa-file-alt fa-lg"></i>
                                </div>
                                <div style="flex: 1; min-width: 0;">
                                    <div style="font-weight: 700; color: var(--text-primary); font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${data.file_original}</div>
                                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${(data.file_size / 1024).toFixed(1)} KB</div>
                                </div>
                                <a href="${fullUrl}" target="_blank" style="padding: 8px 16px; background: var(--primary); color: white; border-radius: 8px; font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap;">View / Download</a>
                            </div>
                            <div style="padding: 8px 12px; border-top: 1px solid var(--border-color); display: flex; align-items: center; gap: 8px; font-size: 11px; background: var(--bg-secondary);">
                                <i class="fas fa-link" style="color: var(--primary); font-size: 10px;"></i>
                                <span style="color: var(--text-muted);">Direct Link:</span>
                                <a href="${fullUrl}" target="_blank" style="color: var(--primary); text-decoration: none; word-break: break-all; font-family: monospace;">${fullUrl}</a>
                            </div>
                        </div><p></p>`;
                    insertHtmlAtCursor(fileHtml);
                }
                showToast('Media inserted!', 'success');
                markUnsaved();
            } else {
                showToast(data.error || 'Upload failed', 'error');
            }
        });
}

function insertHtmlAtCursor(html) {
    const editor = document.getElementById('noteContent');
    const selection = window.getSelection();
    let range;

    if (lastSelectionRange) {
        range = lastSelectionRange;
        // Optional: refocus the editor
        editor.focus();
        selection.removeAllRanges();
        selection.addRange(range);
    } else if (selection.rangeCount > 0) {
        range = selection.getRangeAt(0);
    } else {
        editor.focus();
        range = document.createRange();
        range.selectNodeContents(editor);
        range.collapse(false);
    }

    range.deleteContents();
    const node = range.createContextualFragment(html);
    range.insertNode(node);
    
    // Move cursor after the inserted content
    range.collapse(false);
    selection.removeAllRanges();
    selection.addRange(range);
    
    // Update last range
    lastSelectionRange = range;
}

function insertTable() {
    const rows = prompt('Number of rows:', '3');
    const cols = prompt('Number of columns:', '3');
    if (!rows || !cols) return;

    let table = '<table style="width:100%; border-collapse:collapse; margin:10px 0; border:1px solid var(--border-color);">';
    for (let i = 0; i < rows; i++) {
        table += '<tr>';
        for (let j = 0; j < cols; j++) {
            table += '<td style="border:1px solid var(--border-color); padding:8px; min-width:50px; height:24px;"></td>';
        }
        table += '</tr>';
    }
    table += '</table><p><br></p>';
    insertHtmlAtCursor(table);
    markUnsaved();
}

// Drive Save
document.getElementById('driveBtn').addEventListener('click', () => {
    if (!currentNoteId) {
        showToast('Please select a note first', 'error');
        return;
    }
    
    const fd = new FormData();
    fd.append('notes_title', document.getElementById('noteTitleInput').value);
    fd.append('notes_description', document.getElementById('noteContent').innerHTML);

    showToast('Saving to Drive...', 'info');

    fetch('/api/save-to-drive', { method: 'POST', body: fd })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                window.open(data.file_path, '_blank');
            } else {
                showToast(data.error || 'Failed to save to Drive', 'error');
            }
        });
});

// --- Image Resizing Logic ---
let currentResizingImg = null;

function initResizing() {
    const editor = document.getElementById('noteContent');
    if (!editor) return;

    editor.addEventListener('click', (e) => {
        if (e.target.tagName === 'IMG') {
            e.stopPropagation();
            selectImageForResizing(e.target);
        } else if (!e.target.closest('.resize-handle')) {
            clearImageSelection();
        }
    });
    
    // Also clear on scroll or window resize
    window.addEventListener('scroll', clearImageSelection, true);
    window.addEventListener('resize', clearImageSelection);
}

function selectImageForResizing(img) {
    clearImageSelection();
    currentResizingImg = img;
    img.classList.add('resizing-active');
    
    const handle = document.createElement('div');
    handle.className = 'resize-handle';
    handle.style.cssText = `
        position: absolute; width: 12px; height: 12px; background: var(--primary);
        cursor: nwse-resize; z-index: 9999; border-radius: 2px;
    `;
    
    document.body.appendChild(handle);
    updateHandlePosition(img, handle);
    
    let isDragging = false;
    
    handle.onmousedown = (e) => {
        isDragging = true;
        e.preventDefault();
        e.stopPropagation();
        
        const startX = e.clientX;
        const startWidth = img.clientWidth;
        
        function onMouseMove(moveEvent) {
            if (!isDragging) return;
            const delta = moveEvent.clientX - startX;
            const newWidth = startWidth + delta;
            if (newWidth > 30) {
                img.style.width = newWidth + 'px';
                img.style.height = 'auto'; // Maintain aspect ratio
                updateHandlePosition(img, handle);
            }
        }
        
        function onMouseUp() {
            isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            markUnsaved();
        }
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
    
    img._resizeHandle = handle;
}

function updateHandlePosition(img, handle) {
    const rect = img.getBoundingClientRect();
    handle.style.left = (window.scrollX + rect.right - 6) + 'px';
    handle.style.top = (window.scrollY + rect.bottom - 6) + 'px';
}

function clearImageSelection() {
    if (currentResizingImg) {
        currentResizingImg.classList.remove('resizing-active');
        if (currentResizingImg._resizeHandle) {
            currentResizingImg._resizeHandle.remove();
            delete currentResizingImg._resizeHandle;
        }
        currentResizingImg = null;
    }
}