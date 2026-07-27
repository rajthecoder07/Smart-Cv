// ========== RESUME EDITOR & FORM HANDLER ==========

class ResumeFormManager {
    constructor() {
        this.resumeData = this.getDefaultData();
        this.currentTemplate = localStorage.getItem('selectedResumeTemplate') || 'sidebar-professional';
        this.autoSaveInterval = null;
    }
    
    getDefaultData() {
        return {
            personal: {
                fullName: '',
                title: '',
                email: '',
                phone: '',
                location: '',
                profileImage: null
            },
            profile: '',
            skills: [],
            languages: [],
            experience: [],
            education: [],
            references: []
        };
    }
    
    // ===== FORM BUILDING =====
    async buildDynamicForm(templateId) {
        try {
            const response = await fetch(`/api/form-fields?template=${templateId}`);
            const fields = await response.json();
            this.renderFormSections(fields);
            this.setupEventListeners();
            this.startAutoSave();
        } catch (error) {
            console.error('Error building form:', error);
            this.showError('Failed to load form fields');
        }
    }
    
    renderFormSections(fields) {
        const formContainer = document.getElementById('resumeForm');
        if (!formContainer) return;
        
        formContainer.innerHTML = '';
        
        for (const [groupKey, groupData] of Object.entries(fields.fieldGroups)) {
            const section = document.createElement('div');
            section.className = 'form-section';
            section.dataset.group = groupKey;
            
            // Section header
            const header = document.createElement('div');
            header.className = 'form-section-header';
            header.innerHTML = `
                <h3><i class="bi bi-${groupData.icon}"></i> ${groupData.label}</h3>
                <p class="form-section-description">${groupData.description || ''}</p>
            `;
            section.appendChild(header);
            
            // Form fields
            const fieldsDiv = document.createElement('div');
            fieldsDiv.className = 'form-fields';
            
            for (const [fieldKey, fieldDef] of Object.entries(groupData.fields)) {
                const fieldHTML = this.createFormField(fieldKey, fieldDef, groupKey);
                fieldsDiv.appendChild(fieldHTML);
            }
            
            section.appendChild(fieldsDiv);
            formContainer.appendChild(section);
        }
    }
    
    createFormField(fieldKey, fieldDef, groupKey) {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-field-wrapper';
        wrapper.dataset.field = fieldKey;
        
        let fieldHTML = '';
        
        if (fieldDef.type === 'text' || fieldDef.type === 'email') {
            fieldHTML = `
                <label class="form-label">${fieldDef.label}
                    ${fieldDef.required ? '<span class="required">*</span>' : ''}
                </label>
                <input type="${fieldDef.type}" 
                       class="form-control" 
                       data-field="${fieldKey}"
                       data-group="${groupKey}"
                       placeholder="${fieldDef.placeholder || ''}"
                       ${fieldDef.required ? 'required' : ''}>
                ${fieldDef.help ? `<small class="form-help">${fieldDef.help}</small>` : ''}
            `;
        }
        
        else if (fieldDef.type === 'textarea') {
            fieldHTML = `
                <label class="form-label">${fieldDef.label}
                    ${fieldDef.required ? '<span class="required">*</span>' : ''}
                </label>
                <textarea class="form-control" 
                          data-field="${fieldKey}"
                          data-group="${groupKey}"
                          rows="${fieldDef.rows || 4}"
                          placeholder="${fieldDef.placeholder || ''}"
                          ${fieldDef.maxLength ? `maxlength="${fieldDef.maxLength}"` : ''}
                          ${fieldDef.required ? 'required' : ''}></textarea>
                ${fieldDef.help ? `<small class="form-help">${fieldDef.help}</small>` : ''}
            `;
        }
        
        else if (fieldDef.type === 'image') {
            fieldHTML = `
                <label class="form-label">${fieldDef.label}</label>
                <div class="image-upload-wrapper">
                    <input type="file" 
                           class="image-input" 
                           accept="image/jpeg,image/png"
                           data-field="${fieldKey}"
                           data-group="${groupKey}">
                    <div class="image-preview-area">
                        <div class="image-preview-placeholder">
                            <i class="bi bi-image"></i>
                            <p>Click or drag to upload</p>
                        </div>
                        <img class="image-preview" style="display:none;">
                    </div>
                </div>
                ${fieldDef.help ? `<small class="form-help">${fieldDef.help}</small>` : ''}
            `;
        }
        
        else if (fieldDef.type === 'tags') {
            fieldHTML = `
                <label class="form-label">${fieldDef.label}</label>
                <div class="tags-input-wrapper">
                    <div class="tags-list"></div>
                    <input type="text" 
                           class="tags-input" 
                           data-field="${fieldKey}"
                           data-group="${groupKey}"
                           placeholder="${fieldDef.placeholder || ''}"
                           autocomplete="off">
                </div>
            `;
        }
        
        else if (fieldDef.type === 'repeatable') {
            fieldHTML = `
                <label class="form-label">${fieldDef.label}</label>
                <div class="repeatable-container" data-field="${fieldKey}" data-group="${groupKey}">
                    <div class="repeatable-items"></div>
                    <button type="button" class="btn btn-outline-primary btn-sm add-item-btn">
                        <i class="bi bi-plus"></i> Add ${fieldDef.label}
                    </button>
                </div>
            `;
        }
        
        wrapper.innerHTML = fieldHTML;
        return wrapper;
    }
    
    setupEventListeners() {
        // Text and textarea inputs
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('change', () => this.updateResumeData());
            input.addEventListener('blur', () => this.updateResumeData());
        });
        
        // Image upload
        document.querySelectorAll('.image-input').forEach(input => {
            input.addEventListener('change', (e) => this.handleImageUpload(e));
        });
        
        // Tags
        document.querySelectorAll('.tags-input').forEach(input => {
            input.addEventListener('keydown', (e) => this.handleTagInput(e));
        });
        
        // Repeatable items
        document.querySelectorAll('.add-item-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.addRepeatableItem(e));
        });
    }
    
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64Data = e.target.result;
            
            // Update preview
            const preview = event.target.parentElement.querySelector('.image-preview');
            const placeholder = event.target.parentElement.querySelector('.image-preview-placeholder');
            preview.src = base64Data;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
            
            // Update resume data
            this.resumeData.personal.profileImage = base64Data;
            this.updatePreview();
        };
        reader.readAsDataURL(file);
    }
    
    handleTagInput(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const value = event.target.value.trim();
            if (!value) return;
            
            const container = event.target.parentElement;
            const tag = document.createElement('span');
            tag.className = 'tag-badge';
            tag.innerHTML = `
                ${value}
                <button type="button" class="tag-remove" data-value="${value}">&times;</button>
            `;
            
            const list = container.querySelector('.tags-list');
            list.appendChild(tag);
            event.target.value = '';
            
            // Add remove listener
            tag.querySelector('.tag-remove').addEventListener('click', () => {
                tag.remove();
                this.updateResumeData();
            });
            
            this.updateResumeData();
        }
    }
    
    addRepeatableItem(event) {
        event.preventDefault();
        const container = event.target.closest('.repeatable-container');
        const field = container.dataset.field;
        const itemsDiv = container.querySelector('.repeatable-items');
        
        // Add empty object to data
        if (!this.resumeData[field]) {
            this.resumeData[field] = [];
        }
        
        this.resumeData[field].push({});
        
        // Re-render form
        this.updateResumeData();
    }
    
    updateResumeData() {
        // Collect all form data
        document.querySelectorAll('[data-field]').forEach(input => {
            const field = input.dataset.field;
            const group = input.dataset.group;
            
            if (input.classList.contains('form-control')) {
                if (!this.resumeData[group]) {
                    this.resumeData[group] = {};
                }
                this.resumeData[group][field] = input.value;
            }
        });
        
        // Collect tags
        document.querySelectorAll('.tags-input-wrapper').forEach(wrapper => {
            const field = wrapper.querySelector('.tags-input').dataset.field;
            const tags = Array.from(wrapper.querySelectorAll('.tag-badge')).map(tag => 
                tag.textContent.replace('×', '').trim()
            );
            this.resumeData[field] = tags;
        });
        
        this.updatePreview();
    }
    
    updatePreview() {
        const previewFrame = document.getElementById('resumePreview');
        if (!previewFrame) return;
        
        // Send data to preview
        fetch(`/api/resume/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: this.currentTemplate,
                resume_data: this.resumeData
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                previewFrame.innerHTML = data.html;
            }
        })
        .catch(err => console.error('Preview error:', err));
    }
    
    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            this.saveResume();
        }, 30000); // Auto-save every 30 seconds
    }
    
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
    
    async saveResume() {
        try {
            const response = await fetch(`/api/resume/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: this.currentTemplate,
                    resume_data: this.resumeData
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.showSuccess('Resume saved');
                if (!this.resumeId) {
                    this.resumeId = data.resume_id;
                }
            }
        } catch (error) {
            console.error('Save error:', error);
        }
    }
    
    showSuccess(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.insertBefore(alert, document.body.firstChild);
        setTimeout(() => alert.remove(), 3000);
    }
    
    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.insertBefore(alert, document.body.firstChild);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const formManager = new ResumeFormManager();
    const templateId = localStorage.getItem('selectedResumeTemplate') || 'sidebar-professional';
    formManager.buildDynamicForm(templateId);
    
    // Save on form submit
    const form = document.getElementById('resumeForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            formManager.saveResume();
        });
    }
});
