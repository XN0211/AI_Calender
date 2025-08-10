// Global variables
let currentDate = new Date();
let selectedDate = null;
let notesData = {};
let editingNoteIndex = null;

// Calendar functionality
class Calendar {
    constructor() {
        this.currentDate = new Date();
        // Remove the instance selectedDate - use global selectedDate instead
        this.init();
    }

    async init() {
        await this.loadNotes(); // Wait for notes to load first
        this.renderCalendar();
        this.bindEvents();
        this.updateWeekOverview();
    }

    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Update header
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        document.getElementById('current-month').textContent = `${monthNames[month]} ${year}`;
        
        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const calendarDays = document.getElementById('calendar-days');
        calendarDays.innerHTML = '';
        
        // Generate calendar days
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const dayElement = this.createDayElement(date, month);
            calendarDays.appendChild(dayElement);
        }
    }

    createDayElement(date, currentMonth) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day';
        
        const dayNumber = date.getDate();
        const dateString = this.formatDate(date);
        const isCurrentMonth = date.getMonth() === currentMonth;
        const isToday = this.isToday(date);
        const isSelected = selectedDate === dateString;
        
        // Store the date string directly on the element for easy access
        dayDiv.dataset.date = dateString;
        
        // Check for label
        const labelData = labelManager ? labelManager.getLabelsForDate(dateString) : null;
        if (labelData) {
            dayDiv.classList.add('has-label');
        }
        
        // Add classes
        if (!isCurrentMonth) dayDiv.classList.add('other-month');
        if (isToday) dayDiv.classList.add('today');
        if (isSelected) dayDiv.classList.add('selected');
        
        // Create day content
        const dayNumberDiv = document.createElement('div');
        dayNumberDiv.className = 'day-number';
        dayNumberDiv.textContent = dayNumber;
        
        const dayNotesDiv = document.createElement('div');
        dayNotesDiv.className = 'day-notes';
        
        // Add notes preview
        const notes = notesData[dateString] || [];
        if (notes.length > 0) {
            notes.slice(0, 2).forEach(note => {
                const notePreview = document.createElement('div');
                notePreview.className = 'note-preview';
                notePreview.textContent = note.length > 20 ? note.substring(0, 20) + '...' : note;
                dayNotesDiv.appendChild(notePreview);
            });
            if (notes.length > 2) {
                const moreDiv = document.createElement('div');
                moreDiv.className = 'note-preview';
                moreDiv.textContent = `+${notes.length - 2} more`;
                dayNotesDiv.appendChild(moreDiv);
            }
        }
        
        // Add label indicator
        if (labelData) {
            const labelIndicator = document.createElement('div');
            labelIndicator.className = 'day-label';
            labelIndicator.textContent = labelData.label;
            labelIndicator.style.backgroundColor = labelData.color + '20'; // Add transparency
            labelIndicator.style.color = labelData.color;
            labelIndicator.style.borderColor = labelData.color;
            dayDiv.appendChild(labelIndicator);
        }
        
        dayDiv.appendChild(dayNumberDiv);
        dayDiv.appendChild(dayNotesDiv);
        
        // Add click event
        dayDiv.addEventListener('click', () => {
            this.selectDate(dateString);
        });
        
        return dayDiv;
    }

    selectDate(dateString) {
        console.log('selectDate called with:', dateString); // Debug log
        selectedDate = dateString;
        // this.selectedDate = dateString; // This line is removed
        
        console.log('Global selectedDate after setting:', selectedDate); // Debug log
        
        // Update UI - use the stored date string directly
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('selected');
        });
        
        // Find the selected day using the stored date string
        const selectedDay = document.querySelector(`.calendar-day[data-date="${dateString}"]`);
        
        if (selectedDay) {
            selectedDay.classList.add('selected');
            console.log('Found and selected calendar day for date:', dateString); // Debug log
        } else {
            console.log('Could not find calendar day for date:', dateString); // Debug log
        }
        
        // Update notes panel
        this.updateNotesPanel();
        this.updateSelectedDateDisplay();
    }

    getSelectedDate() {
        return selectedDate;
    }

    getDateFromElement(element, dayNumber) {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Find the date by looking at the position in the calendar grid
        const allDays = Array.from(document.querySelectorAll('.calendar-day'));
        const index = allDays.indexOf(element);
        
        const firstDay = new Date(year, month, 1);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + index);
        
        return date;
    }

    updateSelectedDateDisplay() {
        const selectedDateElement = document.getElementById('selected-date');
        const currentSelectedDate = this.getSelectedDate();
        
        if (currentSelectedDate) {
            console.log('Selected date:', currentSelectedDate); // Debug log
            // Parse date string safely without timezone issues
            const [year, month, day] = currentSelectedDate.split('-').map(Number);
            const date = new Date(year, month - 1, day); // month is 0-indexed
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const formattedDate = date.toLocaleDateString('en-US', options);
            console.log('Formatted date:', formattedDate); // Debug log
            selectedDateElement.textContent = formattedDate;
        } else {
            selectedDateElement.textContent = 'Select a date';
        }
    }

    updateNotesPanel() {
        const currentSelectedDate = this.getSelectedDate();
        console.log('updateNotesPanel called with selectedDate:', currentSelectedDate); // Debug log
        console.log('Global selectedDate variable:', selectedDate); // Debug log
        
        const notesList = document.getElementById('notes-list');
        notesList.innerHTML = '';
        
        const notes = notesData[currentSelectedDate] || [];
        console.log('Found notes for date:', currentSelectedDate, 'Notes:', notes); // Debug log
        console.log('Available notesData keys:', Object.keys(notesData)); // Debug log
        
        if (notes.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-notes';
            emptyMessage.textContent = 'No notes for this date. Add one below!';
            emptyMessage.style.textAlign = 'center';
            emptyMessage.style.color = '#666';
            emptyMessage.style.padding = '20px';
            notesList.appendChild(emptyMessage);
            return;
        }
        
        notes.forEach((note, index) => {
            const noteItem = this.createNoteItem(note, index);
            notesList.appendChild(noteItem);
        });
    }

    createNoteItem(note, index) {
        const noteDiv = document.createElement('div');
        noteDiv.className = 'note-item';
        
        const noteContent = document.createElement('div');
        noteContent.className = 'note-content';
        noteContent.textContent = note;
        
        const noteActions = document.createElement('div');
        noteActions.className = 'note-actions';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'edit-btn';
        editBtn.innerHTML = '<i class="fas fa-edit"></i> Edit';
        editBtn.onclick = () => this.editNote(index, note);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
        deleteBtn.onclick = () => this.deleteNote(index);
        
        noteActions.appendChild(editBtn);
        noteActions.appendChild(deleteBtn);
        
        noteDiv.appendChild(noteContent);
        noteDiv.appendChild(noteActions);
        
        return noteDiv;
    }

    editNote(index, currentContent) {
        editingNoteIndex = index;
        const modal = document.getElementById('note-modal');
        const textarea = document.getElementById('edit-note-content');
        textarea.value = currentContent;
        modal.style.display = 'block';
    }

    deleteNote(index) {
        if (!selectedDate || !confirm('Are you sure you want to delete this note?')) {
            return;
        }
        
        this.performDeleteNote(index);
    }

    async performDeleteNote(index) {
        try {
            const response = await fetch('/delete_note', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: selectedDate, note_index: index })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                await this.loadNotes();
                this.renderCalendar();
                this.updateNotesPanel();
                this.updateWeekOverview();
            } else {
                alert('Failed to delete note');
            }
        } catch (error) {
            console.error('Error deleting note:', error);
            alert('Error deleting note');
        }
    }

    async addNote() {
        const content = document.getElementById('new-note-content').value.trim();
        if (!selectedDate) {
            alert('Please select a date first');
            return;
        }
        if (!content) {
            alert('Please enter note content');
            return;
        }
        
        try {
            const response = await fetch('/save_note', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: selectedDate, content })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                document.getElementById('new-note-content').value = '';
                await this.loadNotes();
                this.renderCalendar();
                this.updateNotesPanel();
                this.updateWeekOverview();
            } else {
                alert('Failed to add note');
            }
        } catch (error) {
            console.error('Error adding note:', error);
            alert('Error adding note');
        }
    }

    async loadNotes() {
        try {
            const response = await fetch('/get_notes');
            const data = await response.json();
            notesData = data || {};
            console.log('Notes loaded:', notesData); // Debug log
        } catch (error) {
            console.error('Error loading notes:', error);
            notesData = {};
        }
    }

    async refreshData() {
        await this.loadNotes();
        if (labelManager) {
            await labelManager.loadLabels();
        }
    }

    updateWeekOverview() {
        const weekOverview = document.getElementById('week-overview');
        weekOverview.innerHTML = '';
        
        const today = new Date();
        const weekDates = [];
        
        // Get current week dates
        for (let i = 0; i < 7; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            weekDates.push(date);
        }
        
        weekDates.forEach(date => {
            const dayElement = this.createWeekDayElement(date);
            weekOverview.appendChild(dayElement);
        });
    }

    createWeekDayElement(date) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'week-day';
        
        const dateString = this.formatDate(date);
        const isToday = this.isToday(date);
        const notes = notesData[dateString] || [];
        
        if (isToday) {
            dayDiv.classList.add('today');
        }
        
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayDate = date.getDate();
        
        dayDiv.innerHTML = `
            <div class="week-day-name">${dayName}</div>
            <div class="week-day-date">${dayDate}</div>
            <div class="week-day-notes">${notes.length} note${notes.length !== 1 ? 's' : ''}</div>
        `;
        
        return dayDiv;
    }

    bindEvents() {
        // Navigation buttons
        document.getElementById('prev-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        });
        
        document.getElementById('next-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        });
        
        // Add note button
        document.getElementById('add-note-btn').addEventListener('click', () => {
            this.addNote();
        });
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });
        
        // Modal events
        this.bindModalEvents();
        
        // Enter key for adding notes
        document.getElementById('new-note-content').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.addNote();
            }
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    bindModalEvents() {
        const modal = document.getElementById('note-modal');
        const closeBtn = document.querySelector('.close');
        const saveBtn = document.getElementById('save-note-btn');
        const cancelBtn = document.getElementById('cancel-edit-btn');
        
        closeBtn.onclick = () => modal.style.display = 'none';
        cancelBtn.onclick = () => modal.style.display = 'none';
        
        window.onclick = (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
        
        saveBtn.onclick = async () => {
            const content = document.getElementById('edit-note-content').value.trim();
            if (!content) {
                alert('Please enter note content');
                return;
            }
            
            if (editingNoteIndex !== null && selectedDate) {
                const notes = notesData[selectedDate] || [];
                notes[editingNoteIndex] = content;
                
                try {
                    const response = await fetch('/update_note', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ date: selectedDate, contents: notes })
                    });
                    
                    const data = await response.json();
                    if (data.status === 'success') {
                        await this.loadNotes();
                        this.renderCalendar();
                        this.updateNotesPanel();
                        this.updateWeekOverview();
                        modal.style.display = 'none';
                        editingNoteIndex = null;
                    } else {
                        alert('Failed to update note');
                    }
                } catch (error) {
                    console.error('Error updating note:', error);
                    alert('Error updating note');
                }
            }
        };
    }

    // Utility methods
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }
}

// AI functionality
class AIAssistant {
    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('generate-plan-btn').addEventListener('click', () => {
            this.generatePlan();
        });
        
        document.getElementById('ask-ai-btn').addEventListener('click', () => {
            this.askAI();
        });
    }

    async generatePlan() {
        const goal = document.getElementById('planning-goal').value.trim();
        if (!goal) {
            alert('Please enter a planning goal');
            return;
        }
        
        const resultDisplay = document.getElementById('plan-result');
        resultDisplay.textContent = 'Generating plan with AI... Please wait.';
        
        try {
            const response = await fetch('/generate_plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                resultDisplay.textContent = this.formatPlanResult(data);
                // Refresh calendar to show new plans
                calendar.renderCalendar();
                calendar.updateWeekOverview();
            } else {
                resultDisplay.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            console.error('Error generating plan:', error);
            resultDisplay.textContent = 'Error generating plan. Please try again.';
        }
    }

    async askAI() {
        const question = document.getElementById('ai-question').value.trim();
        if (!question) {
            alert('Please enter a question');
            return;
        }
        
        const resultDisplay = document.getElementById('ai-answer');
        resultDisplay.textContent = 'AI is analyzing your schedule... Please wait.';
        
        try {
            const response = await fetch('/ask_ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            
            const data = await response.json();
            if (data.answer) {
                resultDisplay.textContent = data.answer;
            } else {
                resultDisplay.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            console.error('Error asking AI:', error);
            resultDisplay.textContent = 'Error getting AI response. Please try again.';
        }
    }

    formatPlanResult(data) {
        let result = '✅ AI Plan Generated Successfully!\n\n';
        result += '📅 Weekly Schedule:\n';
        result += '==================\n\n';
        
        Object.entries(data.plan).forEach(([date, activities]) => {
            // Parse date string safely without timezone issues
            const [year, month, day] = date.split('-').map(Number);
            const dateObj = new Date(year, month - 1, day); // month is 0-indexed
            const formattedDate = dateObj.toLocaleDateString('en-US', { 
                weekday: 'long', 
                month: 'short', 
                day: 'numeric' 
            });
            result += `📆 ${formattedDate}:\n`;
            activities.forEach((activity, index) => {
                result += `   ${index + 1}. ${activity}\n`;
            });
            result += '\n';
        });
        
        return result;
    }
}

// Bulk Delete functionality
class BulkDeleteManager {
    constructor() {
        this.bindEvents();
        this.initializeCurrentWeekInfo();
    }

    bindEvents() {
        // Single date delete
        document.getElementById('delete-single-date-btn').addEventListener('click', () => {
            this.deleteSingleDate();
        });

        // Date range delete
        document.getElementById('delete-date-range-btn').addEventListener('click', () => {
            this.deleteDateRange();
        });

        // Current week delete
        document.getElementById('delete-current-week-btn').addEventListener('click', () => {
            this.deleteCurrentWeek();
        });

        // Month delete
        document.getElementById('delete-month-btn').addEventListener('click', () => {
            this.deleteMonth();
        });

        // Multiple dates delete
        document.getElementById('delete-multiple-dates-btn').addEventListener('click', () => {
            this.deleteMultipleDates();
        });

        // Set current year in year input
        document.getElementById('year-input').value = new Date().getFullYear();
    }

    initializeCurrentWeekInfo() {
        const today = new Date();
        const daysSinceMonday = today.getDay() === 0 ? 6 : today.getDay() - 1; // Sunday = 0, but we want Monday = 0
        const monday = new Date(today);
        monday.setDate(today.getDate() - daysSinceMonday);
        
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        
        const weekInfo = document.getElementById('current-week-info');
        weekInfo.textContent = `(${monday.toLocaleDateString()} - ${sunday.toLocaleDateString()})`;
    }

    async deleteSingleDate() {
        const dateInput = document.getElementById('single-date-input');
        const date = dateInput.value;

        if (!date) {
            alert('Please select a date');
            return;
        }

        if (!confirm(`Are you sure you want to delete all notes for ${date}?`)) {
            return;
        }

        try {
            const response = await fetch('/delete_all_notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date })
            });

            const data = await response.json();
            this.showDeleteResult(data);
            
            if (data.status === 'success') {
                dateInput.value = '';
                calendar.loadNotes();
                calendar.renderCalendar();
                calendar.updateWeekOverview();
                if (selectedDate === date) {
                    calendar.updateNotesPanel();
                }
            }
        } catch (error) {
            console.error('Error deleting single date:', error);
            this.showDeleteResult({ error: 'Error deleting date. Please try again.' });
        }
    }

    async deleteDateRange() {
        const startDate = document.getElementById('start-date-input').value;
        const endDate = document.getElementById('end-date-input').value;

        if (!startDate || !endDate) {
            alert('Please select both start and end dates');
            return;
        }

        if (!confirm(`Are you sure you want to delete all notes from ${startDate} to ${endDate}?`)) {
            return;
        }

        try {
            const response = await fetch('/delete_date_range', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_date: startDate, end_date: endDate })
            });

            const data = await response.json();
            this.showDeleteResult(data);
            
            if (data.status === 'success') {
                document.getElementById('start-date-input').value = '';
                document.getElementById('end-date-input').value = '';
                calendar.loadNotes();
                calendar.renderCalendar();
                calendar.updateWeekOverview();
                calendar.updateNotesPanel();
            }
        } catch (error) {
            console.error('Error deleting date range:', error);
            this.showDeleteResult({ error: 'Error deleting date range. Please try again.' });
        }
    }

    async deleteCurrentWeek() {
        if (!confirm('Are you sure you want to delete all notes for the current week?')) {
            return;
        }

        try {
            const response = await fetch('/delete_week', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });

            const data = await response.json();
            this.showDeleteResult(data);
            
            if (data.status === 'success') {
                calendar.loadNotes();
                calendar.renderCalendar();
                calendar.updateWeekOverview();
                calendar.updateNotesPanel();
            }
        } catch (error) {
            console.error('Error deleting current week:', error);
            this.showDeleteResult({ error: 'Error deleting current week. Please try again.' });
        }
    }

    async deleteMonth() {
        const month = document.getElementById('month-select').value;
        const year = document.getElementById('year-input').value;

        if (!year) {
            alert('Please enter a year');
            return;
        }

        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        const monthName = monthNames[parseInt(month) - 1];

        if (!confirm(`Are you sure you want to delete all notes for ${monthName} ${year}?`)) {
            return;
        }

        try {
            const response = await fetch('/delete_month', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ year: parseInt(year), month: parseInt(month) })
            });

            const data = await response.json();
            this.showDeleteResult(data);
            
            if (data.status === 'success') {
                calendar.loadNotes();
                calendar.renderCalendar();
                calendar.updateWeekOverview();
                calendar.updateNotesPanel();
            }
        } catch (error) {
            console.error('Error deleting month:', error);
            this.showDeleteResult({ error: 'Error deleting month. Please try again.' });
        }
    }

    async deleteMultipleDates() {
        const datesInput = document.getElementById('multiple-dates-input').value.trim();
        
        if (!datesInput) {
            alert('Please enter dates to delete');
            return;
        }

        // Parse dates from comma-separated input
        const dateStrings = datesInput.split(',').map(d => d.trim()).filter(d => d);
        const dates = [];

        for (const dateStr of dateStrings) {
            // Validate date format
            if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
                alert(`Invalid date format: ${dateStr}. Please use YYYY-MM-DD format.`);
                return;
            }
            dates.push(dateStr);
        }

        if (dates.length === 0) {
            alert('Please enter at least one valid date');
            return;
        }

        if (!confirm(`Are you sure you want to delete all notes for ${dates.length} date(s)?`)) {
            return;
        }

        try {
            const response = await fetch('/delete_multiple_dates', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dates })
            });

            const data = await response.json();
            this.showDeleteResult(data);
            
            if (data.status === 'success') {
                document.getElementById('multiple-dates-input').value = '';
                calendar.loadNotes();
                calendar.renderCalendar();
                calendar.updateWeekOverview();
                calendar.updateNotesPanel();
            }
        } catch (error) {
            console.error('Error deleting multiple dates:', error);
            this.showDeleteResult({ error: 'Error deleting multiple dates. Please try again.' });
        }
    }

    showDeleteResult(data) {
        const resultDisplay = document.getElementById('delete-result');
        
        if (data.status === 'success') {
            let result = '✅ ' + data.message + '\n\n';
            
            if (data.deleted_dates && data.deleted_dates.length > 0) {
                result += '🗓️ Deleted dates:\n';
                data.deleted_dates.forEach(date => {
                    result += `   • ${date}\n`;
                });
                result += `\n📊 Total notes deleted: ${data.deleted_notes_count}`;
            }
            
            resultDisplay.textContent = result;
            resultDisplay.style.color = '#28a745';
        } else {
            resultDisplay.textContent = '❌ ' + (data.error || 'Unknown error occurred');
            resultDisplay.style.color = '#dc3545';
        }
    }
}

// Label management functionality
class LabelManager {
    constructor() {
        this.labelsData = {};
        this.editingLabelDate = null;
        this.bindEvents();
        this.loadLabels();
    }

    bindEvents() {
        // Save label
        document.getElementById('save-label-btn').addEventListener('click', () => {
            this.saveLabel();
        });

        // Update label
        document.getElementById('update-label-btn').addEventListener('click', () => {
            this.updateLabel();
        });

        // Clear form
        document.getElementById('clear-label-form-btn').addEventListener('click', () => {
            this.clearForm();
        });

        // Template buttons
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.useTemplate(e.currentTarget);
            });
        });

        // Set current date in date input
        document.getElementById('label-date-input').value = new Date().toISOString().split('T')[0];
    }

    async loadLabels() {
        try {
            const response = await fetch('/get_labels');
            const data = await response.json();
            this.labelsData = data || {};
            this.renderLabelsList();
        } catch (error) {
            console.error('Error loading labels:', error);
            this.labelsData = {};
        }
    }

    async saveLabel() {
        const date = document.getElementById('label-date-input').value;
        const label = document.getElementById('label-text-input').value.trim();
        const color = document.getElementById('label-color-input').value;

        if (!date) {
            alert('Please select a date');
            return;
        }

        if (!label) {
            alert('Please enter a label');
            return;
        }

        try {
            const response = await fetch('/save_label', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date, label, color })
            });

            const data = await response.json();
            this.showLabelResult(data);
            
            if (data.status === 'success') {
                await this.loadLabels();
                calendar.renderCalendar();
                this.clearForm();
            }
        } catch (error) {
            console.error('Error saving label:', error);
            this.showLabelResult({ error: 'Error saving label. Please try again.' });
        }
    }

    async updateLabel() {
        if (!this.editingLabelDate) {
            alert('No label selected for editing');
            return;
        }

        const label = document.getElementById('label-text-input').value.trim();
        const color = document.getElementById('label-color-input').value;

        if (!label) {
            alert('Please enter a label');
            return;
        }

        try {
            const response = await fetch('/update_label', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: this.editingLabelDate, label, color })
            });

            const data = await response.json();
            this.showLabelResult(data);
            
            if (data.status === 'success') {
                await this.loadLabels();
                calendar.renderCalendar();
                this.clearForm();
                this.editingLabelDate = null;
            }
        } catch (error) {
            console.error('Error updating label:', error);
            this.showLabelResult({ error: 'Error updating label. Please try again.' });
        }
    }

    async deleteLabel(date) {
        if (!confirm('Are you sure you want to delete this label?')) {
            return;
        }

        try {
            const response = await fetch('/delete_label', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date })
            });

            const data = await response.json();
            this.showLabelResult(data);
            
            if (data.status === 'success') {
                await this.loadLabels();
                calendar.renderCalendar();
            }
        } catch (error) {
            console.error('Error deleting label:', error);
            this.showLabelResult({ error: 'Error deleting label. Please try again.' });
        }
    }

    editLabel(date) {
        const labelData = this.labelsData[date];
        if (!labelData) return;

        document.getElementById('label-date-input').value = date;
        document.getElementById('label-text-input').value = labelData.label;
        document.getElementById('label-color-input').value = labelData.color;

        document.getElementById('save-label-btn').style.display = 'none';
        document.getElementById('update-label-btn').style.display = 'inline-flex';
        
        this.editingLabelDate = date;
    }

    useTemplate(templateBtn) {
        const label = templateBtn.dataset.label;
        const color = templateBtn.dataset.color;

        document.getElementById('label-text-input').value = label;
        document.getElementById('label-color-input').value = color;

        // Switch to save mode
        document.getElementById('save-label-btn').style.display = 'inline-flex';
        document.getElementById('update-label-btn').style.display = 'none';
        this.editingLabelDate = null;
    }

    clearForm() {
        document.getElementById('label-date-input').value = new Date().toISOString().split('T')[0];
        document.getElementById('label-text-input').value = '';
        document.getElementById('label-color-input').value = '#ff6b6b';

        document.getElementById('save-label-btn').style.display = 'inline-flex';
        document.getElementById('update-label-btn').style.display = 'none';
        this.editingLabelDate = null;
    }

    renderLabelsList() {
        const labelsList = document.getElementById('labels-list');
        labelsList.innerHTML = '';

        const sortedDates = Object.keys(this.labelsData).sort();

        if (sortedDates.length === 0) {
            labelsList.innerHTML = '<div class="empty-labels">No labels created yet. Add your first label above!</div>';
            return;
        }

        sortedDates.forEach(date => {
            const labelData = this.labelsData[date];
            const labelItem = this.createLabelItem(date, labelData);
            labelsList.appendChild(labelItem);
        });
    }

    createLabelItem(date, labelData) {
        const labelDiv = document.createElement('div');
        labelDiv.className = 'label-item';

        const formattedDate = new Date(date).toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric' 
        });

        labelDiv.innerHTML = `
            <div class="label-info">
                <div class="label-color-indicator" style="background-color: ${labelData.color}"></div>
                <div class="label-details">
                    <div class="label-date">${formattedDate}</div>
                    <div class="label-text">${labelData.label}</div>
                </div>
            </div>
            <div class="label-actions-small">
                <button class="edit-label-btn" onclick="labelManager.editLabel('${date}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="delete-label-btn" onclick="labelManager.deleteLabel('${date}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;

        return labelDiv;
    }

    showLabelResult(data) {
        const resultDisplay = document.getElementById('label-result');
        
        if (data.status === 'success') {
            resultDisplay.textContent = '✅ Label saved successfully!';
            resultDisplay.style.color = '#28a745';
        } else {
            resultDisplay.textContent = '❌ ' + (data.error || 'Unknown error occurred');
            resultDisplay.style.color = '#dc3545';
        }

        // Clear result after 3 seconds
        setTimeout(() => {
            resultDisplay.textContent = '';
        }, 3000);
    }

    getLabelsForDate(date) {
        return this.labelsData[date] || null;
    }
}

// Analytics functionality
class AnalyticsManager {
    constructor() {
        this.analysisData = null;
        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('analyze-time-btn').addEventListener('click', () => {
            this.analyzeTimeAllocation();
        });

        document.getElementById('show-trends-btn').addEventListener('click', () => {
            this.showTrends();
        });

        document.getElementById('export-data-btn').addEventListener('click', () => {
            this.exportData();
        });
    }

    async analyzeTimeAllocation() {
        try {
            const response = await fetch('/analyze_time_allocation');
            const data = await response.json();
            this.analysisData = data;
            
            this.renderSummaryStats(data);
            this.renderScaleCharts(data);
            this.renderBarChart(data.chart_data);
            this.renderWeeklyChart(data.weekly_analysis, data.weekly_intensities);
            this.renderAICategorizationResults(data);
            this.renderActivityDetails(data.chart_data);
            this.generateInsights(data);
            
            this.showAnalyticsResult('✅ Time allocation analysis completed!');
        } catch (error) {
            console.error('Error analyzing time allocation:', error);
            this.showAnalyticsResult('❌ Error analyzing time allocation. Please try again.');
        }
    }

    async showTrends() {
        try {
            const response = await fetch('/get_activity_trends');
            const data = await response.json();
            
            this.renderTrendsChart(data.trends);
            this.showAnalyticsResult('✅ Activity trends loaded!');
        } catch (error) {
            console.error('Error loading trends:', error);
            this.showAnalyticsResult('❌ Error loading trends. Please try again.');
        }
    }

    renderSummaryStats(data) {
        const summaryStats = document.getElementById('summary-stats');
        
        summaryStats.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${data.total_activities}</div>
                <div class="stat-label">Total Activities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.chart_data.length}</div>
                <div class="stat-label">AI Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${this.getMostActiveCategory(data.chart_data)}</div>
                <div class="stat-label">Most Active Category</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${this.getAverageIntensity(data.chart_data)}</div>
                <div class="stat-label">Avg Intensity</div>
            </div>
        `;
    }

    renderScaleCharts(data) {
        // Render scale charts for each category
        data.chart_data.forEach(item => {
            const scaleChart = document.getElementById(`${item.category}-scale`);
            if (scaleChart) {
                const intensity = item.average_intensity;
                const percentage = (intensity / 10) * 100;
                
                scaleChart.innerHTML = `
                    <h5>${item.icon} ${item.category.charAt(0).toUpperCase() + item.category.slice(1)} Intensity</h5>
                    <div class="scale-meter">
                        <div class="scale-indicator" style="left: ${percentage}%"></div>
                    </div>
                    <div class="scale-labels">
                        <span>Low</span>
                        <span>High</span>
                    </div>
                    <div class="scale-value">${intensity}/10</div>
                    <div class="scale-description">${this.getIntensityDescription(item.category, intensity)}</div>
                `;
            }
        });
    }

    renderPieChart(chartData) {
        const pieChart = document.getElementById('pie-chart');
        
        if (chartData.length === 0) {
            pieChart.innerHTML = '<div style="text-align: center; color: #666;">No data available for pie chart</div>';
            return;
        }

        let pieHTML = '<div style="position: relative; width: 100%; height: 100%;">';
        
        let currentAngle = 0;
        chartData.forEach(item => {
            const sliceAngle = (item.percentage / 100) * 360;
            const rotation = currentAngle;
            
            pieHTML += `
                <div class="pie-slice" style="
                    background: ${item.color};
                    transform: rotate(${rotation}deg);
                    clip-path: polygon(50% 50%, 50% 0%, ${50 + 50 * Math.cos(sliceAngle * Math.PI / 180)}% ${50 - 50 * Math.sin(sliceAngle * Math.PI / 180)}%, 50% 50%);
                "></div>
            `;
            
            currentAngle += sliceAngle;
        });
        
        pieHTML += '</div>';
        
        // Add legend
        pieHTML += '<div class="pie-legend">';
        chartData.forEach(item => {
            pieHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background: ${item.color}"></div>
                    <span>${item.icon} ${item.category} (${item.percentage}%) - Avg: ${item.average_intensity}/10</span>
                </div>
            `;
        });
        pieHTML += '</div>';
        
        pieChart.innerHTML = pieHTML;
    }

    renderBarChart(chartData) {
        const barChart = document.getElementById('bar-chart');
        
        if (chartData.length === 0) {
            barChart.innerHTML = '<div style="text-align: center; color: #666;">No data available for bar chart</div>';
            return;
        }

        const maxCount = Math.max(...chartData.map(item => item.count));
        
        let barHTML = '';
        chartData.forEach(item => {
            const height = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
            const intensityHeight = (item.average_intensity / 10) * 100;
            
            barHTML += `
                <div class="bar-with-intensity">
                    <div class="intensity-bar" style="height: ${height}%">
                        <div class="intensity-fill" style="
                            height: ${intensityHeight}%;
                            background: ${item.color};
                        " title="${item.category}: ${item.count} activities, avg intensity ${item.average_intensity}/10"></div>
                    </div>
                    <div class="intensity-label">${item.category}</div>
                    <div class="intensity-value">${item.count}</div>
                    <div class="intensity-value" style="font-size: 0.8rem; color: #666;">${item.average_intensity}/10</div>
                </div>
            `;
        });
        
        barChart.innerHTML = barHTML;
    }

    renderWeeklyChart(weeklyAnalysis, weeklyIntensities) {
        const weeklyChart = document.getElementById('weekly-chart');
        
        if (Object.keys(weeklyAnalysis).length === 0) {
            weeklyChart.innerHTML = '<div style="text-align: center; color: #666;">No weekly data available</div>';
            return;
        }

        const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const colors = ['#4e79a7', '#f28e2c', '#76b7b2'];
        
        let weeklyHTML = '';
        weekDays.forEach((day, index) => {
            const date = this.getWeekDateByIndex(index);
            const dayData = weeklyAnalysis[date] || {};
            const dayIntensities = weeklyIntensities[date] || {};
            const totalActivities = Object.values(dayData).reduce((sum, count) => sum + count, 0);
            
            let intensityHTML = '';
            let colorIndex = 0;
            Object.entries(dayData).forEach(([category, count]) => {
                if (count > 0) {
                    const categoryIntensities = dayIntensities[category] || [];
                    const avgIntensity = categoryIntensities.length > 0 ? 
                        categoryIntensities.reduce((sum, i) => sum + i, 0) / categoryIntensities.length : 5;
                    const height = totalActivities > 0 ? (count / totalActivities) * 100 : 0;
                    
                    intensityHTML += `
                        <div class="intensity-segment" style="
                            height: ${height}%;
                            background: ${colors[colorIndex % colors.length]};
                            opacity: ${avgIntensity / 10};
                        " title="${category}: ${count} activities, avg intensity ${avgIntensity.toFixed(1)}/10">
                            <div class="intensity-tooltip">${category}: ${count} (${avgIntensity.toFixed(1)}/10)</div>
                        </div>
                    `;
                    colorIndex++;
                }
            });
            
            weeklyHTML += `
                <div class="week-day-intensity">
                    <div class="intensity-stack">
                        ${intensityHTML || '<div style="height: 100%; background: #f0f0f0; border-radius: 2px;"></div>'}
                    </div>
                    <div class="week-day-label">${day}</div>
                </div>
            `;
        });
        
        weeklyChart.innerHTML = weeklyHTML;
    }

    renderAICategorizationResults(data) {
        const aiResults = document.getElementById('ai-categorization-results');
        
        if (data.chart_data.length === 0) {
            aiResults.innerHTML = '<div style="text-align: center; color: #666;">No AI categorization results available</div>';
            return;
        }

        let resultsHTML = '';
        data.chart_data.forEach(item => {
            const sampleActivities = item.details.slice(0, 3);
            const confidence = this.calculateConfidence(item);
            
            resultsHTML += `
                <div class="categorization-card">
                    <div class="categorization-header">
                        <div class="categorization-title">
                            <span>${item.icon}</span>
                            <span>${item.category.charAt(0).toUpperCase() + item.category.slice(1)}</span>
                        </div>
                        <div class="categorization-confidence">${confidence}%</div>
                    </div>
                    <div class="categorization-reason">
                        AI categorized ${item.count} activities with average intensity of ${item.average_intensity}/10. 
                        Sample activities: ${sampleActivities.map(d => d.activity).join(', ')}.
                    </div>
                </div>
            `;
        });
        
        aiResults.innerHTML = resultsHTML;
    }

    renderActivityDetails(chartData) {
        const activityDetails = document.getElementById('activity-details');
        
        if (chartData.length === 0) {
            activityDetails.innerHTML = '<div style="text-align: center; color: #666;">No activity details available</div>';
            return;
        }

        let detailsHTML = '';
        chartData.forEach(item => {
            detailsHTML += `
                <div class="category-detail">
                    <div class="category-header">
                        <div class="category-title">
                            <span>${item.icon}</span>
                            <span>${item.category.charAt(0).toUpperCase() + item.category.slice(1)}</span>
                        </div>
                        <div class="category-count">${item.count} (Avg: ${item.average_intensity}/10)</div>
                    </div>
                    <div class="category-activities">
                        ${item.details.slice(0, 5).map(detail => 
                            `<div class="activity-tag">${detail.activity} (${detail.intensity}/10)</div>`
                        ).join('')}
                        ${item.details.length > 5 ? `<div class="activity-tag">+${item.details.length - 5} more</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        activityDetails.innerHTML = detailsHTML;
    }

    generateInsights(data) {
        const aiInsights = document.getElementById('ai-insights');
        
        if (data.chart_data.length === 0) {
            aiInsights.innerHTML = '<div style="text-align: center; color: #666;">No data available for insights</div>';
            return;
        }

        const insights = [];
        
        // Most active category insight
        const mostActive = data.chart_data[0];
        insights.push({
            title: "Most Active Category",
            text: `AI identified ${mostActive.category} as your most active category (${mostActive.percentage}% of activities) with average intensity of ${mostActive.average_intensity}/10.`
        });
        
        // Intensity balance insight
        const avgIntensity = data.chart_data.reduce((sum, item) => sum + item.average_intensity, 0) / data.chart_data.length;
        if (avgIntensity > 7) {
            insights.push({
                title: "High Intensity Schedule",
                text: "Your activities have high average intensity. Consider adding more low-intensity activities for better balance."
            });
        } else if (avgIntensity < 4) {
            insights.push({
                title: "Low Intensity Schedule",
                text: "Your activities have low average intensity. Consider adding some challenging activities to maintain engagement."
            });
        }
        
        // Study vs rest balance
        const studyData = data.chart_data.find(item => item.category === 'study');
        const restData = data.chart_data.find(item => item.category === 'rest');
        if (studyData && restData) {
            if (studyData.average_intensity > 7 && restData.average_intensity < 5) {
                insights.push({
                    title: "Study-Rest Balance",
                    text: "High study intensity with low rest quality. Consider improving rest quality to maintain productivity."
                });
            }
        }
        
        // Exercise insight
        const exerciseData = data.chart_data.find(item => item.category === 'exercise');
        if (exerciseData) {
            if (exerciseData.average_intensity < 5) {
                insights.push({
                    title: "Exercise Intensity",
                    text: "Consider increasing exercise intensity for better fitness benefits."
                });
            } else if (exerciseData.average_intensity > 8) {
                insights.push({
                    title: "High Exercise Intensity",
                    text: "Great job maintaining high exercise intensity! Make sure to include adequate recovery."
                });
            }
        }
        
        let insightsHTML = '';
        insights.forEach(insight => {
            insightsHTML += `
                <div class="insight-item">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-text">${insight.text}</div>
                </div>
            `;
        });
        
        if (insights.length === 0) {
            insightsHTML = '<div style="text-align: center; color: #666;">No specific insights available</div>';
        }
        
        aiInsights.innerHTML = insightsHTML;
    }

    renderTrendsChart(trends) {
        // This would render a line chart showing activity trends over time
        // For now, we'll show a simple summary
        const weeklyChart = document.getElementById('weekly-chart');
        weeklyChart.innerHTML = '<div style="text-align: center; color: #666;">Trends data loaded. Chart visualization coming soon!</div>';
    }

    exportData() {
        if (!this.analysisData) {
            this.showAnalyticsResult('❌ No data to export. Please run analysis first.');
            return;
        }

        const dataStr = JSON.stringify(this.analysisData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `time_allocation_analysis_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showAnalyticsResult('✅ Data exported successfully!');
    }

    getMostActiveCategory(chartData) {
        if (chartData.length === 0) return 'N/A';
        return chartData[0].category.charAt(0).toUpperCase() + chartData[0].category.slice(1);
    }

    getAverageIntensity(chartData) {
        if (chartData.length === 0) return 0;
        const totalIntensity = chartData.reduce((sum, item) => sum + item.average_intensity, 0);
        return (totalIntensity / chartData.length).toFixed(1);
    }

    getWeekDateByIndex(index) {
        const today = new Date();
        const daysSinceMonday = today.getDay() === 0 ? 6 : today.getDay() - 1;
        const monday = new Date(today);
        monday.setDate(today.getDate() - daysSinceMonday);
        
        const targetDate = new Date(monday);
        targetDate.setDate(monday.getDate() + index);
        
        return targetDate.toISOString().split('T')[0];
    }

    showAnalyticsResult(message) {
        const resultDisplay = document.getElementById('analytics-result');
        resultDisplay.textContent = message;
        resultDisplay.style.color = message.includes('✅') ? '#28a745' : '#dc3545';
        
        setTimeout(() => {
            resultDisplay.textContent = '';
        }, 5000);
    }

    getIntensityDescription(category, intensity) {
        const descriptions = {
            study: {
                low: "Light reading, casual learning",
                medium: "Regular studying, homework",
                high: "Intensive studying, exam prep"
            },
            exercise: {
                low: "Light walking, stretching",
                medium: "Regular workouts, moderate exercise",
                high: "Intense workouts, sports games"
            },
            rest: {
                low: "Light relaxation, short breaks",
                medium: "Regular rest, leisure activities",
                high: "Deep relaxation, meditation"
            }
        };
        
        if (intensity <= 3) return descriptions[category].low;
        if (intensity <= 7) return descriptions[category].medium;
        return descriptions[category].high;
    }

    calculateConfidence(item) {
        // Calculate confidence based on consistency of categorization
        const intensities = item.details.map(d => d.intensity);
        const variance = this.calculateVariance(intensities);
        const baseConfidence = 85;
        const variancePenalty = Math.min(15, variance * 2);
        return Math.round(baseConfidence - variancePenalty);
    }

    calculateVariance(values) {
        if (values.length === 0) return 0;
        const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
        const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
        return Math.sqrt(squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length);
    }
}

// Auto-Display Deadline functionality
class AutoDeadlineManager {
    constructor() {
        this.autoDeadlineData = null;
        this.isVisible = true;
        this.autoRefreshInterval = null;
        this.bindEvents();
        this.initializeAutoDisplay();
    }

    bindEvents() {
        document.getElementById('toggle-deadline-btn').addEventListener('click', () => {
            this.toggleVisibility();
        });

        document.getElementById('refresh-auto-deadline-btn').addEventListener('click', () => {
            this.loadAutoDeadlines();
        });
    }

    async initializeAutoDisplay() {
        // Load deadlines immediately on page load
        await this.loadAutoDeadlines();
        
        // Set up auto-refresh every 5 minutes
        this.autoRefreshInterval = setInterval(() => {
            this.loadAutoDeadlines();
        }, 5 * 60 * 1000);
        
        // Also refresh every hour to update day counts
        setInterval(() => {
            this.loadAutoDeadlines();
        }, 60 * 60 * 1000);
    }

    async loadAutoDeadlines() {
        try {
            const response = await fetch('/get_labeled_deadlines');
            const data = await response.json();
            this.autoDeadlineData = data;
            
            this.renderAutoDeadlineDisplay(data);
        } catch (error) {
            console.error('Error loading auto deadlines:', error);
            this.renderAutoDeadlineError();
        }
    }

    renderAutoDeadlineDisplay(data) {
        const displayContainer = document.getElementById('auto-deadline-display');
        
        if (!data.countdowns || data.countdowns.length === 0) {
            displayContainer.innerHTML = `
                <div class="auto-deadline-empty">
                    <i class="fas fa-check-circle"></i>
                    <h3>No Important Deadlines!</h3>
                    <p>Add labels to important dates to see countdowns here.</p>
                    <p style="margin-top: 10px; font-size: 0.8rem;">
                        <i class="fas fa-info-circle"></i> 
                        Use the "Date Labels" tab to mark important events like exams, deadlines, or meetings.
                    </p>
                </div>
            `;
            return;
        }

        // Get only the most important deadlines (critical, urgent, high priority)
        const importantDeadlines = data.countdowns.filter(item => 
            ['critical', 'urgent', 'high'].includes(item.priority)
        ).slice(0, 6); // Show max 6 items

        const deadlineCards = importantDeadlines.map(item => this.createAutoDeadlineCard(item)).join('');
        
        const summaryStats = this.createAutoDeadlineSummary(data.statistics);
        
        displayContainer.innerHTML = `
            <div class="auto-deadline-grid">
                ${deadlineCards}
            </div>
            ${summaryStats}
        `;
    }

    createAutoDeadlineCard(item) {
        const daysText = item.days_remaining === 0 ? 'TODAY' : 
                        item.days_remaining === 1 ? 'TOMORROW' : 
                        `${item.days_remaining} DAYS`;
        
        const priorityIcon = this.getPriorityIcon(item.priority);
        
        return `
            <div class="auto-deadline-card ${item.priority}">
                <div class="auto-deadline-content">
                    <div class="auto-deadline-info">
                        <div class="auto-deadline-label">
                            <div class="auto-deadline-label-color" style="background-color: ${item.label_color}"></div>
                            ${priorityIcon} ${item.label}
                        </div>
                        <div class="auto-deadline-date">${this.formatDate(item.date)}</div>
                        <div class="auto-deadline-activity">${item.activity}</div>
                    </div>
                    <div class="auto-deadline-timer">
                        <div class="auto-deadline-days ${item.priority}">${item.days_remaining}</div>
                        <div class="auto-deadline-text">${daysText}</div>
                    </div>
                </div>
            </div>
        `;
    }

    createAutoDeadlineSummary(stats) {
        const total = stats.total;
        const critical = stats.critical;
        const urgent = stats.urgent;
        const high = stats.high;
        
        return `
            <div class="auto-deadline-summary">
                <div class="auto-deadline-summary-stats">
                    ${critical > 0 ? `<div class="auto-deadline-summary-stat critical">🚨 ${critical} Critical</div>` : ''}
                    ${urgent > 0 ? `<div class="auto-deadline-summary-stat urgent">⚠️ ${urgent} Urgent</div>` : ''}
                    ${high > 0 ? `<div class="auto-deadline-summary-stat high">⚡ ${high} High</div>` : ''}
                    <div class="auto-deadline-summary-stat">📅 ${total} Total</div>
                </div>
                <a href="#" class="auto-deadline-summary-link" onclick="switchToLabelsTab()">
                    Manage Labels <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        `;
    }

    renderAutoDeadlineError() {
        const displayContainer = document.getElementById('auto-deadline-display');
        displayContainer.innerHTML = `
            <div class="auto-deadline-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Unable to Load Deadlines</h3>
                <p>Please check your connection and try refreshing.</p>
            </div>
        `;
    }

    toggleVisibility() {
        const section = document.getElementById('auto-deadline-section');
        const toggleBtn = document.getElementById('toggle-deadline-btn');
        
        if (this.isVisible) {
            section.style.display = 'none';
            toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Show';
            this.isVisible = false;
        } else {
            section.style.display = 'block';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i> Hide';
            this.isVisible = true;
        }
    }

    getPriorityIcon(priority) {
        const icons = {
            'critical': '🚨',
            'urgent': '⚠️',
            'high': '⚡',
            'medium': '📅',
            'low': '📊'
        };
        return icons[priority] || '📋';
    }

    formatDate(dateString) {
        // Parse date string safely without timezone issues
        const [year, month, day] = dateString.split('-').map(Number);
        const date = new Date(year, month - 1, day); // month is 0-indexed
        return date.toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric' 
        });
    }
}

// Global function to switch to labels tab
function switchToLabelsTab() {
    const labelsTab = document.querySelector('[data-tab="labels"]');
    if (labelsTab) {
        labelsTab.click();
    }
}

// Initialize application
let calendar;
let aiAssistant;
let bulkDeleteManager;
let labelManager;
let analyticsManager;
let autoDeadlineManager;

document.addEventListener('DOMContentLoaded', async () => {
    calendar = new Calendar();
    aiAssistant = new AIAssistant();
    bulkDeleteManager = new BulkDeleteManager();
    labelManager = new LabelManager();
    analyticsManager = new AnalyticsManager();
    autoDeadlineManager = new AutoDeadlineManager();
    
    // Wait for labels to load before rendering calendar
    await labelManager.loadLabels();
    
    // Initialize calendar (which will load notes first)
    await calendar.init();
    
    // Set today as default selected date
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    calendar.selectDate(todayString);
});
