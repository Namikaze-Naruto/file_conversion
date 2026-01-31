// Add batch mode toggle button
function addBatchModeToggle() {
    const header = document.querySelector('.header-content');
    if (!header) return;
    
    const toggle = document.createElement('button');
    toggle.id = 'batchModeToggle';
    toggle.className = 'batch-toggle';
    toggle.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>
        </svg>
        Batch Mode
    `;
    toggle.onclick = toggleBatchMode;
    header.appendChild(toggle);
}

function toggleBatchMode() {
    isBatchMode = !isBatchMode;
    const toggle = document.getElementById('batchModeToggle');
    const fileInput = document.getElementById('fileInput');
    
    if (isBatchMode) {
        toggle.classList.add('active');
        fileInput.setAttribute('multiple', 'multiple');
        document.querySelector('.upload-area h2').textContent = 'Drag & drop multiple files';
        document.querySelector('.upload-desc').textContent = 'or click to select up to 20 files';
    } else {
        toggle.classList.remove('active');
        fileInput.removeAttribute('multiple');
        document.querySelector('.upload-area h2').textContent = 'Drag & drop your file';
        document.querySelector('.upload-desc').textContent = 'or click to browse from your device';
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    addBatchModeToggle();
    window.isBatchMode = false;
});
