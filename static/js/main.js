// StudySahayak Main JavaScript

// Global variables
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check authentication
    if (authToken) {
        setAuthHeader();
    }
    
    // Initialize upload areas
    initializeUploadAreas();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize content cards
    initializeContentCards();
}

// Authentication helpers
function setAuthHeader() {
    // Set default headers for fetch requests
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        if (args[1]) {
            args[1].headers = {
                ...args[1].headers,
                'Authorization': `Bearer ${authToken}`
            };
        } else {
            args[1] = {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            };
        }
        return originalFetch.apply(this, args);
    };
}

function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
}

// Upload functionality
function initializeUploadAreas() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        // Drag and drop handlers
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('dragleave', handleDragLeave);
        area.addEventListener('drop', handleDrop);
        
        // Click to upload
        area.addEventListener('click', function() {
            const input = area.querySelector('input[type="file"]');
            if (input) input.click();
        });
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    const area = e.currentTarget;
    area.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0], area);
    }
}

function handleFileUpload(file, uploadArea) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading state
    uploadArea.classList.add('uploading');
    uploadArea.innerHTML = `
        <div class="spinner-border text-primary mb-2" role="status">
            <span class="visually-hidden">Uploading...</span>
        </div>
        <p>Processing ${file.name}...</p>
        <p class="small text-muted">This may take a moment</p>
    `;
    
    // Upload file
    fetch('/api/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.content_id) {
            showSuccessMessage('File uploaded successfully!');
            // Redirect to content options
            window.location.href = `/content/${data.content_id}/options`;
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        showErrorMessage('Upload failed: ' + error.message);
        resetUploadArea(uploadArea);
    });
}

function resetUploadArea(uploadArea) {
    uploadArea.classList.remove('uploading');
    uploadArea.innerHTML = `
        <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
        <h5>Upload Content</h5>
        <p class="text-muted">Drag and drop files here or click to browse</p>
        <p class="small text-muted">Supports: PDF, MP4, MOV, AVI, TXT</p>
        <input type="file" class="d-none" accept=".pdf,.mp4,.mov,.avi,.txt">
    `;
}

// Content management
function initializeContentCards() {
    const contentCards = document.querySelectorAll('.content-card');
    
    contentCards.forEach(card => {
        // Add click handlers for selection
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
                updateBulkActions();
            });
        }
    });
}

function updateBulkActions() {
    const checkedBoxes = document.querySelectorAll('.content-card input[type="checkbox"]:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        if (checkedBoxes.length > 0) {
            bulkActions.classList.remove('d-none');
            bulkActions.querySelector('.selected-count').textContent = checkedBoxes.length;
        } else {
            bulkActions.classList.add('d-none');
        }
    }
}

function selectAllContent() {
    const checkboxes = document.querySelectorAll('.content-card input[type="checkbox"]');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
        const card = checkbox.closest('.content-card');
        if (checkbox.checked) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    updateBulkActions();
}

function deleteSelectedContent() {
    const checkedBoxes = document.querySelectorAll('.content-card input[type="checkbox"]:checked');
    const contentIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    if (contentIds.length === 0) {
        showErrorMessage('No content selected');
        return;
    }
    
    if (confirm(`Delete ${contentIds.length} selected item(s)?`)) {
        deleteMultipleContent(contentIds);
    }
}

function deleteContent(contentId) {
    if (confirm('Are you sure you want to delete this content?')) {
        fetch(`/api/content/${contentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage('Content deleted successfully');
                // Remove card from DOM
                const card = document.querySelector(`[data-content-id="${contentId}"]`);
                if (card) {
                    card.remove();
                }
            } else {
                throw new Error(data.error || 'Delete failed');
            }
        })
        .catch(error => {
            showErrorMessage('Delete failed: ' + error.message);
        });
    }
}

function deleteMultipleContent(contentIds) {
    fetch('/api/content/bulk-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ content_ids: contentIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showSuccessMessage(`${data.deleted_count} item(s) deleted successfully`);
            // Remove cards from DOM
            contentIds.forEach(id => {
                const card = document.querySelector(`[data-content-id="${id}"]`);
                if (card) {
                    card.remove();
                }
            });
            updateBulkActions();
        } else {
            throw new Error(data.error || 'Bulk delete failed');
        }
    })
    .catch(error => {
        showErrorMessage('Delete failed: ' + error.message);
    });
}

// Content generation
function generateContent(contentId, type) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    button.disabled = true;
    
    fetch(`/api/${type}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ content_id: contentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data[type]) {
            showSuccessMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} generated successfully!`);
            // Redirect to view the generated content
            window.location.href = `/content/${contentId}/${type}`;
        } else {
            throw new Error(data.error || `${type} generation failed`);
        }
    })
    .catch(error => {
        showErrorMessage(`${type} generation failed: ` + error.message);
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// UI helpers
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function showSuccessMessage(message) {
    showAlert(message, 'success');
}

function showErrorMessage(message) {
    showAlert(message, 'danger');
}

function showAlert(message, type) {
    const alertContainer = document.querySelector('.alert-container') || document.body;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    }, 5000);
}

// Quiz specific functions (for quiz page)
function startQuiz(contentId) {
    window.location.href = `/content/${contentId}/quiz`;
}

// Search functionality
function searchContent(query) {
    const cards = document.querySelectorAll('.content-card');
    
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const content = card.querySelector('.card-text').textContent.toLowerCase();
        
        if (title.includes(query.toLowerCase()) || content.includes(query.toLowerCase())) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function timeAgo(date) {
    const now = new Date();
    const past = new Date(date);
    const diffTime = Math.abs(now - past);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
}

// Export functions for global use
window.StudySahayak = {
    deleteContent,
    generateContent,
    selectAllContent,
    deleteSelectedContent,
    searchContent,
    showSuccessMessage,
    showErrorMessage
};
