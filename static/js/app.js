// Processing page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-redirect from processing page after simulated processing time
    if (window.location.pathname.includes('/processing/')) {
        const contentId = window.location.pathname.split('/').pop();
        
        // Simulate processing time (3-5 seconds)
        const processingTime = Math.random() * 2000 + 3000; // 3-5 seconds
        
        setTimeout(function() {
            window.location.href = `/options/${contentId}`;
        }, processingTime);
    }
    
    // File upload preview
    const fileInput = document.getElementById('file');
    const textArea = document.getElementById('text_content');
    const previewDiv = document.getElementById('file-preview');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Clear text content when file is selected
                if (textArea) textArea.value = '';
                
                // Show file preview
                if (previewDiv) {
                    const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
                    previewDiv.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-file"></i> 
                            <strong>${file.name}</strong> (${fileSize} MB)
                        </div>
                    `;
                }
            }
        });
    }
    
    if (textArea) {
        textArea.addEventListener('input', function() {
            // Clear file input when text is entered
            if (fileInput) fileInput.value = '';
            if (previewDiv) previewDiv.innerHTML = '';
        });
    }
    
    // Quiz number validation
    const numQuestionsInput = document.getElementById('num_questions');
    if (numQuestionsInput) {
        numQuestionsInput.addEventListener('change', function() {
            const value = parseInt(this.value);
            if (value < 1) this.value = 1;
            if (value > 50) this.value = 50;
        });
    }
    
    // Auto-submit quiz options
    const quizForm = document.getElementById('quiz-options-form');
    if (quizForm) {
        const submitBtn = quizForm.querySelector('button[type="submit"]');
        const numInput = quizForm.querySelector('#num_questions');
        
        if (numInput) {
            numInput.addEventListener('change', function() {
                if (this.value && this.value >= 1 && this.value <= 50) {
                    submitBtn.textContent = `Generate ${this.value} Questions`;
                }
            });
        }
    }
});

// Function to show loading state
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    button.disabled = true;
    
    // Re-enable after processing (fallback)
    setTimeout(function() {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 10000);
}

// Add loading state to form submissions
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        showLoading(submitBtn);
    }
});
