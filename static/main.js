
document.addEventListener('DOMContentLoaded', function () {

    const alerts = document.querySelectorAll('.alert.auto-dismiss');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Add Bootstrap's fade class and then remove the element
            alert.classList.add('fade');
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(function () { alert.remove(); }, 500);
        }, 5000); // 5000 milliseconds = 5 seconds
    });


    const uploadZone = document.getElementById('uploadZone');
    const fileInput  = document.getElementById('resume_pdf');

    if (uploadZone && fileInput) {

        // When user clicks the zone, trigger file browser
        uploadZone.addEventListener('click', function () {
            fileInput.click();
        });

        // When a file is dragged over the zone, highlight it
        uploadZone.addEventListener('dragover', function (e) {
            e.preventDefault();           // Must prevent default to allow drop
            uploadZone.classList.add('dragover');
        });

        // When the drag leaves the zone, remove highlight
        uploadZone.addEventListener('dragleave', function () {
            uploadZone.classList.remove('dragover');
        });

        // When a file is dropped onto the zone
        uploadZone.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadZone.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                // Attach the dropped file to the hidden input
                fileInput.files = files;
                updateFileDisplay(files[0].name);
            }
        });

        // When user selects a file via file browser
        fileInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                updateFileDisplay(this.files[0].name);
            }
        });

        // Helper function to show selected filename in the upload zone
        function updateFileDisplay(filename) {
            const uploadText = document.getElementById('uploadText');
            if (uploadText) {
                uploadText.innerHTML =
                    '<strong style="color: var(--primary)">✓ File selected:</strong> ' +
                    escapeHtml(filename);
            }
        }
    }

    const jobSelect    = document.getElementById('target_job');
    const skillPreview = document.getElementById('skillPreview');
    const skillList    = document.getElementById('skillList');

    if (jobSelect && skillPreview) {

        jobSelect.addEventListener('change', function () {
            const selectedJob = this.value;

            if (!selectedJob) {
                skillPreview.style.display = 'none';
                return;
            }

            // Fetch the required skills for the selected job via API
            fetch('/api/job-skills/' + encodeURIComponent(selectedJob))
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.skills && skillList) {
                        // Split skills by comma and create badge for each
                        const skills = data.skills.split(',');
                        skillList.innerHTML = '';  // Clear previous skills

                        skills.forEach(function (skill) {
                            const badge = document.createElement('span');
                            badge.className = 'skill-badge skill-missing';
                            badge.textContent = skill.trim();
                            skillList.appendChild(badge);
                        });

                        // Show the description too
                        const desc = document.getElementById('jobDescription');
                        if (desc && data.description) {
                            desc.textContent = data.description;
                        }

                        skillPreview.style.display = 'block';
                    }
                })
                .catch(function (error) {
                    console.error('Error fetching job skills:', error);
                });
        });
    }


    const progressBars = document.querySelectorAll('.progress-bar[data-width]');
    progressBars.forEach(function (bar) {
        const targetWidth = bar.getAttribute('data-width');
        // Start at 0 then animate to target width
        bar.style.width = '0%';
        setTimeout(function () {
            bar.style.width = targetWidth + '%';
        }, 300); // 300ms delay so animation is visible
    });


    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function (textarea) {
        const maxLen  = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'text-muted-sm d-block mt-1';
        counter.textContent = '0 / ' + maxLen + ' characters';
        textarea.parentNode.appendChild(counter);

        textarea.addEventListener('input', function () {
            counter.textContent = this.value.length + ' / ' + maxLen + ' characters';
        });
    });


    
    const forms = document.querySelectorAll('form.show-loading');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Analyzing...';

                // Re-enable after 15 seconds (in case of error)
                setTimeout(function () {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 15000);
            }
        });
    });


    const toggleBtns = document.querySelectorAll('.toggle-password');
    toggleBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const input    = document.getElementById(targetId);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '🙈';
                } else {
                    input.type = 'password';
                    this.textContent = '👁';
                }
            }
        });
    });


    const skillsInput = document.getElementById('skills');
    if (skillsInput) {
        skillsInput.addEventListener('blur', function () {
            // Clean up the skills input: lowercase, trim spaces
            let val = this.value;
            val = val.split(',')
                     .map(function (s) { return s.trim().toLowerCase(); })
                     .filter(function (s) { return s.length > 0; })
                     .join(', ');
            this.value = val;
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

}); // End of DOMContentLoaded


function printResults() {
    window.print();
}

function copyToClipboard(text, btnElement) {
    navigator.clipboard.writeText(text).then(function () {
        const original = btnElement.textContent;
        btnElement.textContent = '✓ Copied!';
        btnElement.style.color = 'var(--success)';
        setTimeout(function () {
            btnElement.textContent = original;
            btnElement.style.color = '';
        }, 2000);
    }).catch(function (err) {
        console.error('Copy failed:', err);
    });
}