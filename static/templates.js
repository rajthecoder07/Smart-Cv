/**
 * Resume Template Management System
 * Handles template selection, localStorage persistence, and CSS injection
 */

class ResumeTemplateManager {
  constructor() {
    this.selectedTemplate = localStorage.getItem('selectedResumeTemplate') || null;
    this.templates = [];
    this.init();
  }

  async init() {
    await this.loadTemplates();
    this.applySelectedTemplate();
    this.initializeUI();
  }

  async loadTemplates() {
    try {
      const response = await fetch('/api/resume-templates');
      if (response.ok) {
        this.templates = await response.json();
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  }

  applySelectedTemplate() {
    if (this.selectedTemplate && this.templates.length > 0) {
      const template = this.templates.find(t => t.id === this.selectedTemplate);
      if (template) {
        this.injectTemplateCSS(template);
        this.markAsSelected(template.id);
      }
    }
  }

  injectTemplateCSS(template) {
    // Remove old template CSS if exists
    let existingStyle = document.getElementById('resume-template-css');
    if (existingStyle) {
      existingStyle.remove();
    }

    // Inject new template CSS
    const style = document.createElement('style');
    style.id = 'resume-template-css';
    style.innerHTML = template.css || '';
    document.head.appendChild(style);

    // Store in session storage for current page
    sessionStorage.setItem('activeTemplateCSS', template.css || '');
  }

  markAsSelected(templateId) {
    const cards = document.querySelectorAll('[data-template-id]');
    cards.forEach(card => {
      if (card.dataset.templateId === templateId) {
        card.classList.add('selected');
        // Add visual indicator
        if (!card.querySelector('.selected-badge')) {
          const badge = document.createElement('div');
          badge.className = 'selected-badge';
          badge.innerHTML = '<i class="bi bi-check-circle-fill"></i> Selected';
          card.style.position = 'relative';
          card.appendChild(badge);
        }
      } else {
        card.classList.remove('selected');
        const badge = card.querySelector('.selected-badge');
        if (badge) badge.remove();
      }
    });
  }

  selectTemplate(templateId) {
    const template = this.templates.find(t => t.id === templateId);
    if (!template) return;

    // Update localStorage
    localStorage.setItem('selectedResumeTemplate', templateId);
    this.selectedTemplate = templateId;

    // Apply CSS
    this.injectTemplateCSS(template);
    this.markAsSelected(templateId);

    // Trigger custom event
    window.dispatchEvent(new CustomEvent('templateSelected', { detail: template }));

    return template;
  }

  getSelectedTemplate() {
    if (!this.selectedTemplate) return null;
    return this.templates.find(t => t.id === this.selectedTemplate);
  }

  clearSelection() {
    localStorage.removeItem('selectedResumeTemplate');
    this.selectedTemplate = null;
    const style = document.getElementById('resume-template-css');
    if (style) style.remove();
    this.markAsSelected(null);
  }

  initializeUI() {
    // Add CSS for selected template cards
    const style = document.createElement('style');
    style.innerHTML = `
      [data-template-id].selected {
        border-color: var(--primary) !important;
        background: linear-gradient(135deg, rgba(14,165,233,0.02), rgba(99,102,241,0.02));
      }
      
      [data-template-id].selected::before {
        opacity: 1 !important;
      }

      .selected-badge {
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        box-shadow: 0 4px 12px rgba(14,165,233,0.3);
        z-index: 10;
      }
    `;
    document.head.appendChild(style);
  }
}

// Initialize globally
let templateManager = null;

document.addEventListener('DOMContentLoaded', () => {
  templateManager = new ResumeTemplateManager();

  // Make available globally
  window.TemplateManager = templateManager;
});

// Helper function to get selected template from anywhere
function getSelectedTemplate() {
  if (templateManager) {
    return templateManager.getSelectedTemplate();
  }
  const templateId = localStorage.getItem('selectedResumeTemplate');
  if (templateId) {
    return { id: templateId };
  }
  return null;
}

// Helper function to display template info in resume form
function showSelectedTemplateInfo() {
  const selected = getSelectedTemplate();
  if (selected) {
    const info = document.createElement('div');
    info.className = 'alert alert-info';
    info.innerHTML = `
      <i class="bi bi-info-circle me-2"></i>
      <strong>Template:</strong> ${selected.name || selected.id}
      <a href="/templates" class="ms-2" style="color: var(--primary); text-decoration: underline;">Change</a>
    `;
    const resumeForm = document.querySelector('form[data-resume-form]');
    if (resumeForm) {
      resumeForm.insertBefore(info, resumeForm.firstChild);
    }
  }
}
