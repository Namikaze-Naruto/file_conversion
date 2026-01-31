// Batch Conversion API Handler

const BatchAPI = {
    /**
     * Upload multiple files for batch conversion
     */
    async uploadBatch(files) {
        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }
        
        const response = await fetch(`${API.BASE_URL}/batch/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Batch upload failed');
        }
        
        return await response.json();
    },
    
    /**
     * Convert multiple files to target format
     */
    async convertBatch(conversionIds, targetFormat) {
        const response = await fetch(`${API.BASE_URL}/batch/convert?target_format=${targetFormat}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(conversionIds)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Batch conversion failed');
        }
        
        return await response.json();
    },
    
    /**
     * Check batch conversion status
     */
    async checkBatchStatus(conversionIds) {
        const ids = conversionIds.join(',');
        const response = await fetch(`${API.BASE_URL}/batch/status?conversion_ids=${ids}`);
        
        if (!response.ok) {
            throw new Error('Failed to get batch status');
        }
        
        return await response.json();
    },
    
    /**
     * Download all converted files as ZIP
     */
    async downloadBatchZip(conversionIds) {
        const response = await fetch(`${API.BASE_URL}/batch/download-zip`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(conversionIds)
        });
        
        if (!response.ok) {
            throw new Error('Failed to download ZIP');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted_files_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};

// Batch Conversion State
let batchState = {
    files: [],
    conversionIds: [],
    targetFormat: null,
    isProcessing: false
};

/**
 * Enable batch mode
 */
function enableBatchMode() {
    const fileInput = document.getElementById('fileInput');
    fileInput.setAttribute('multiple', 'multiple');
    
    // Update UI
    document.querySelector('.upload-area h2').textContent = 'Drag & drop multiple files';
    document.querySelector('.upload-desc').textContent = 'or click to select up to 20 files';
    
    // Show batch indicator
    const indicator = document.createElement('div');
    indicator.className = 'batch-indicator';
    indicator.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>
        </svg>
        Batch Mode Active
    `;
    document.querySelector('.upload-section').insertBefore(
        indicator,
        document.querySelector('.upload-area')
    );
}

/**
 * Handle batch file selection
 */
async function handleBatchUpload(files) {
    if (files.length > 20) {
        UI.showError('Maximum 20 files allowed per batch');
        return;
    }
    
    batchState.files = Array.from(files);
    batchState.isProcessing = true;
    
    // Show batch upload UI
    showBatchUploadUI();
    
    try {
        // Upload all files
        const result = await BatchAPI.uploadBatch(files);
        
        // Store conversion IDs
        batchState.conversionIds = result.files
            .filter(f => f.status === 'uploaded')
            .map(f => f.id);
        
        // Show format selection
        showBatchFormatSelection(result);
        
    } catch (error) {
        UI.showError('Batch upload failed: ' + error.message);
        batchState.isProcessing = false;
    }
}

/**
 * Show batch upload UI
 */
function showBatchUploadUI() {
    const section = document.getElementById('uploadSection');
    section.classList.add('hidden');
    
    // Create batch file list UI
    const batchSection = document.createElement('section');
    batchSection.id = 'batchSection';
    batchSection.className = 'batch-section';
    batchSection.innerHTML = `
        <div class="batch-container">
            <h2>Batch Conversion (${batchState.files.length} files)</h2>
            <div class="batch-file-list" id="batchFileList">
                ${batchState.files.map((file, index) => `
                    <div class="batch-file-item" data-index="${index}">
                        <div class="file-icon">${getFileIcon(file.name)}</div>
                        <div class="file-info">
                            <h4>${file.name}</h4>
                            <p>${formatFileSize(file.size)}</p>
                        </div>
                        <div class="file-status">
                            <span class="status-badge uploading">Uploading...</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="batch-format-selection hidden" id="batchFormatSelection">
                <h3>Convert all files to:</h3>
                <select id="batchTargetFormat" class="format-select">
                    <option value="">Select format...</option>
                    <optgroup label="Documents">
                        <option value="pdf">PDF</option>
                        <option value="docx">DOCX</option>
                        <option value="txt">TXT</option>
                    </optgroup>
                    <optgroup label="Images">
                        <option value="jpg">JPG</option>
                        <option value="png">PNG</option>
                        <option value="webp">WebP</option>
                    </optgroup>
                    <optgroup label="Audio">
                        <option value="mp3">MP3</option>
                        <option value="wav">WAV</option>
                    </optgroup>
                </select>
                <button class="btn btn-primary" onclick="startBatchConversion()">
                    Convert All Files
                </button>
            </div>
            <div class="batch-progress hidden" id="batchProgress">
                <div class="progress-header">
                    <h3>Converting files...</h3>
                    <span id="batchProgressText">0 / ${batchState.files.length} complete</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="batchProgressFill" style="width: 0%"></div>
                </div>
            </div>
            <div class="batch-results hidden" id="batchResults">
                <button class="btn btn-success" onclick="downloadBatchZip()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="7 10 12 15 17 10" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <line x1="12" y1="15" x2="12" y2="3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Download All as ZIP
                </button>
            </div>
        </div>
    `;
    
    document.querySelector('.main-content').appendChild(batchSection);
}

/**
 * Show format selection after upload
 */
function showBatchFormatSelection(result) {
    // Update status badges
    result.files.forEach((file, index) => {
        const item = document.querySelector(`.batch-file-item[data-index="${index}"] .status-badge`);
        if (file.status === 'uploaded') {
            item.textContent = 'Ready';
            item.className = 'status-badge success';
        } else {
            item.textContent = 'Failed';
            item.className = 'status-badge error';
        }
    });
    
    // Show format selection
    document.getElementById('batchFormatSelection').classList.remove('hidden');
}

/**
 * Start batch conversion
 */
async function startBatchConversion() {
    const targetFormat = document.getElementById('batchTargetFormat').value;
    
    if (!targetFormat) {
        UI.showError('Please select a target format');
        return;
    }
    
    batchState.targetFormat = targetFormat;
    
    // Hide format selection, show progress
    document.getElementById('batchFormatSelection').classList.add('hidden');
    document.getElementById('batchProgress').classList.remove('hidden');
    
    try {
        // Start conversion
        await BatchAPI.convertBatch(batchState.conversionIds, targetFormat);
        
        // Poll for status
        await pollBatchStatus();
        
    } catch (error) {
        UI.showError('Batch conversion failed: ' + error.message);
    }
}

/**
 * Poll batch conversion status
 */
async function pollBatchStatus() {
    const interval = setInterval(async () => {
        try {
            const status = await BatchAPI.checkBatchStatus(batchState.conversionIds);
            
            // Update progress
            const progress = (status.completed / status.total) * 100;
            document.getElementById('batchProgressFill').style.width = `${progress}%`;
            document.getElementById('batchProgressText').textContent = 
                `${status.completed} / ${status.total} complete`;
            
            // Update individual file statuses
            status.results.forEach(result => {
                const item = document.querySelector(`.batch-file-item[data-index="${result.id}"]`);
                if (item) {
                    const badge = item.querySelector('.status-badge');
                    if (result.status === 'completed') {
                        badge.textContent = 'Completed';
                        badge.className = 'status-badge success';
                    } else if (result.status === 'failed') {
                        badge.textContent = 'Failed';
                        badge.className = 'status-badge error';
                    } else if (result.status === 'processing') {
                        badge.textContent = 'Processing...';
                        badge.className = 'status-badge processing';
                    }
                }
            });
            
            // Check if all complete
            if (status.all_complete) {
                clearInterval(interval);
                showBatchComplete();
            }
            
        } catch (error) {
            clearInterval(interval);
            UI.showError('Failed to check status');
        }
    }, 2000);
}

/**
 * Show batch completion
 */
function showBatchComplete() {
    document.getElementById('batchProgress').classList.add('hidden');
    document.getElementById('batchResults').classList.remove('hidden');
}

/**
 * Download batch as ZIP
 */
async function downloadBatchZip() {
    try {
        await BatchAPI.downloadBatchZip(batchState.conversionIds);
        UI.showSuccess('Downloaded all files successfully!');
    } catch (error) {
        UI.showError('Failed to download ZIP: ' + error.message);
    }
}

/**
 * Helper: Get file icon
 */
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'xls': '📊', 'xlsx': '📊',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️',
        'mp3': '🎵', 'wav': '🎵',
        'mp4': '🎬', 'avi': '🎬',
        'zip': '📦', 'rar': '📦'
    };
    return icons[ext] || '📁';
}

/**
 * Helper: Format file size
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}
