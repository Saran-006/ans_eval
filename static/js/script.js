console.log('AI evaluator UI loaded');

// Handle retry button clicks
document.addEventListener('DOMContentLoaded', function() {
  const uploadForm = document.getElementById('upload-form');
  if (uploadForm) {
    uploadForm.addEventListener('submit', handleAsyncUpload);
  }
  
  // Handle retry buttons
  const retryButtons = document.querySelectorAll('.retry-btn');
  retryButtons.forEach(btn => {
    btn.addEventListener('click', handleRetry);
  });
});

async function handleRetry(e) {
  e.preventDefault();
  
  const btn = e.target;
  const evalId = btn.getAttribute('data-eval-id');
  const scoreElement = document.getElementById(`score-${evalId}`);
  
  // Disable button and keep it disabled until evaluation completes
  btn.disabled = true;
  const originalText = btn.textContent;
  btn.textContent = 'Processing...';
  
  try {
    const response = await fetch(`/re_eval/${evalId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Retry failed: ${response.statusText}`);
    }
    
    // Clear the score and show processing badge
    scoreElement.innerHTML = '<span class="badge bg-warning text-dark">Pending</span>';
    
    // Initialize timer for this evaluation
    if (!evalTimers[evalId]) {
      evalTimers[evalId] = {
        startTime: Date.now(),
        timerInterval: null
      };
    }
    
    // Start polling immediately
    setTimeout(() => {
      scoreElement.innerHTML = '<span class="badge bg-info">Processing... 0m 0s</span>';
      startTimer(evalId, scoreElement);
      pollEvaluationStatus(evalId, scoreElement, btn); // Pass button reference
    }, 500);
    
  } catch (error) {
    console.error('Error:', error);
    alert(`Error: ${error.message}`);
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

async function handleAsyncUpload(e) {
  e.preventDefault();
  
  const form = e.target;
  const submitBtn = document.getElementById('submit-btn');
  const studentName = document.getElementById('student_name');
  const answerPdf = document.getElementById('answer_pdf');
  
  // Validate
  if (!studentName.value.trim()) {
    alert('Please enter student name');
    return;
  }
  if (!answerPdf.files.length) {
    alert('Please select a PDF file');
    return;
  }
  
  // Disable button and show loading state
  submitBtn.disabled = true;
  const originalText = submitBtn.textContent;
  submitBtn.textContent = 'Uploading...';
  
  try {
    // Get subject ID from URL
    const subjectId = window.location.pathname.split('/').pop();
    
    // Create form data
    const formData = new FormData();
    formData.append('student_name', studentName.value.trim());
    formData.append('answer_pdf', answerPdf.files[0]);
    
    // Upload and start evaluation
    const response = await fetch(`/subject/${subjectId}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    // Reset form
    form.reset();
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
    
    // Reload page to show new evaluation
    setTimeout(() => {
      location.reload();
    }, 1000);
    
  } catch (error) {
    console.error('Error:', error);
    alert(`Error: ${error.message}`);
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

// Store timers for each evaluation
const evalTimers = {};

// Poll for evaluation updates
function startEvaluationPolling() {
  const evaluationRows = document.querySelectorAll('[id^="score-"]');
  
  evaluationRows.forEach(scoreElement => {
    const evalId = scoreElement.id.replace('score-', '');
    // Check if this evaluation is still processing
    const badge = scoreElement.querySelector('.badge');
    if (badge && badge.classList.contains('bg-warning')) {
      // Start timer if not already running
      if (!evalTimers[evalId]) {
        evalTimers[evalId] = {
          startTime: Date.now(),
          timerInterval: null
        };
        startTimer(evalId, scoreElement);
      }
    }
    // Find the corresponding retry button to pass along
    const retryBtn = document.querySelector(`button.retry-btn[data-eval-id="${evalId}"]`);
    pollEvaluationStatus(evalId, scoreElement, retryBtn);
  });
}

function startTimer(evalId, scoreElement) {
  const timerData = evalTimers[evalId];
  
  const updateDisplay = () => {
    const elapsed = Math.floor((Date.now() - timerData.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timeStr = `${minutes}m ${seconds}s`;
    
    // Update the badge with timer
    const badge = scoreElement.querySelector('.badge');
    if (badge && badge.classList.contains('bg-info')) {
      badge.textContent = `Processing... ${timeStr}`;
    }
  };
  
  // Update immediately and then every second
  updateDisplay();
  timerData.timerInterval = setInterval(updateDisplay, 1000);
}

async function pollEvaluationStatus(evalId, scoreElement, retryBtn = null) {
  // Check if already has a score
  const badge = scoreElement.querySelector('.badge');
  if (badge && !badge.classList.contains('bg-warning') && !badge.classList.contains('bg-info')) {
    // Clear timer if it exists
    if (evalTimers[evalId]) {
      clearInterval(evalTimers[evalId].timerInterval);
      delete evalTimers[evalId];
    }
    // Re-enable retry button when evaluation completes
    if (retryBtn) {
      retryBtn.disabled = false;
      retryBtn.textContent = 'Retry';
    }
    // Update View button text from "Check Error" to "View"
    const viewBtn = document.getElementById(`view-btn-${evalId}`);
    if (viewBtn) {
      viewBtn.textContent = 'View';
    }
    return; // Already completed
  }
  
  try {
    const response = await fetch(`/evaluation_status/${evalId}`);
    const data = await response.json();
    
    if (data.score !== null && data.score !== undefined) {
      // Update UI with score and clear timer
      scoreElement.innerHTML = `<span class="badge bg-success">${data.score}</span>`;
      if (evalTimers[evalId]) {
        clearInterval(evalTimers[evalId].timerInterval);
        delete evalTimers[evalId];
      }
      // Re-enable retry button when evaluation completes
      if (retryBtn) {
        retryBtn.disabled = false;
        retryBtn.textContent = 'Retry';
      }
      // Update View button text from "Check Error" to "View"
      const viewBtn = document.getElementById(`view-btn-${evalId}`);
      if (viewBtn) {
        viewBtn.textContent = 'View';
      }
    } else if (data.processing) {
      // Still processing - ensure we have the processing badge
      if (!badge || !badge.classList.contains('bg-info')) {
        scoreElement.innerHTML = `<span class="badge bg-info">Processing... 0m 0s</span>`;
        // Initialize timer if not already started
        if (!evalTimers[evalId]) {
          evalTimers[evalId] = {
            startTime: Date.now(),
            timerInterval: null
          };
          startTimer(evalId, scoreElement);
        }
      }
      // Poll again in 5 seconds (increased from 2s for longer evaluation process)
      setTimeout(() => pollEvaluationStatus(evalId, scoreElement, retryBtn), 5000);
    }
  } catch (error) {
    console.error(`Error polling evaluation ${evalId}:`, error);
    // Retry in 5 seconds on error
    setTimeout(() => pollEvaluationStatus(evalId, scoreElement, retryBtn), 5000);
  }
}

// Start polling when page loads
document.addEventListener('DOMContentLoaded', startEvaluationPolling);
