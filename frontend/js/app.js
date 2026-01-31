// Application State
let currentFile = null;
let currentUploadData = null;
let supportedFormats = null;
let selectedCategory = null; // Track selected category

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('File Conversion Platform initialized');
    
    // Load supported formats
    try {
        supportedFormats = await FileConversionAPI.getSupportedFormats();
        console.log('Supported formats loaded:', supportedFormats);
    } catch (error) {
        console.error('Failed to load formats:', error);
    }

    // Setup drag and drop
    setupDragAndDrop();
    
    // Setup file input
    setupFileInput();
});

// Open category-specific converter
function openCategoryConverter(category) {
    console.log('Opening converter for category:', category);
    
    // Store selected category
    selectedCategory = category;
    
    const categoryNames = {
        'document': 'Documents',
        'image': 'Images',
        'audio': 'Audio',
        'video': 'Videos',
        'archive': 'Archives',
        'code': 'Code & Data'
    };
    
    // Show toast notification
    UIManager.showToast(
        `${categoryNames[category]} Converter`,
        'Select a file to start converting',
        'info',
        2500
    );
    
    // Scroll to upload section
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Add visual feedback
    highlightCategory(category);
    
    // Update upload area with category info
    updateUploadAreaForCategory(category);
    
    // Trigger file input after a short delay
    setTimeout(() => {
        document.getElementById('fileInput').click();
    }, 600);
}

// Highlight selected category
function highlightCategory(category) {
    // Remove previous highlights
    document.querySelectorAll('.feature-card').forEach(card => {
        card.classList.remove('selected-category');
    });
    
    // Add highlight to selected category
    const selectedCard = document.querySelector(`.feature-card[data-category="${category}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected-category');
    }
}

// Update upload area to show category context
function updateUploadAreaForCategory(category) {
    const categoryNames = {
        'document': 'Documents',
        'image': 'Images',
        'audio': 'Audio',
        'video': 'Videos',
        'archive': 'Archives',
        'code': 'Code & Data'
    };
    
    // Update main heading
    const uploadArea = document.querySelector('.upload-area h2');
    if (uploadArea) {
        uploadArea.innerHTML = `Drop your <span class="gradient-text">${categoryNames[category]}</span> file`;
    }
    
    // Show category indicator
    const categoryIndicator = document.getElementById('categoryIndicator');
    const categoryName = document.getElementById('categoryName');
    if (categoryIndicator && categoryName) {
        categoryName.textContent = categoryNames[category];
        categoryIndicator.classList.remove('hidden');
    }
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    if (!uploadArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        }, false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Setup file input
function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
    }
}

// Handle file selection
async function handleFile(file) {
    console.log('File selected:', file.name);
    
    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        UIManager.showError('File size exceeds 50MB limit');
        return;
    }

    currentFile = file;

    try {
        // Show progress
        UIManager.showProgress(10);
        
        // Upload file
        const uploadData = await FileConversionAPI.uploadFile(file);
        currentUploadData = uploadData;
        
        console.log('Upload successful:', uploadData);
        
        // Show file info and format selection
        UIManager.showFileInfo(file, uploadData);
        
        // Get current file format
        const currentFormat = uploadData.source_format;
        
        // Determine category from file format or use selected category
        let category = selectedCategory;
        if (!category) {
            category = detectCategoryFromFormat(currentFormat);
        }
        
        // Setup format selection with category pre-selected
        if (supportedFormats) {
            UIManager.updateFormatGrid(supportedFormats, category || 'all', currentFormat);
            UIManager.setupCategoryTabs(supportedFormats, currentFormat);
            
            // Auto-select the category tab
            if (category) {
                const categoryTab = document.querySelector(`.tab-btn[data-category="${category}"]`);
                if (categoryTab) {
                    document.querySelectorAll('.tab-btn').forEach(tab => tab.classList.remove('active'));
                    categoryTab.classList.add('active');
                }
            }
        }
        
        // Reset selected category
        selectedCategory = null;
        
    } catch (error) {
        console.error('Upload failed:', error);
        UIManager.showError(error.message || 'Failed to upload file');
    }
}

// Start conversion
async function startConversion() {
    if (!currentFile || !currentUploadData) {
        UIManager.showError('No file selected');
        return;
    }

    const convertBtn = document.getElementById('convertBtn');
    const targetFormat = convertBtn.dataset.targetFormat;
    
    if (!targetFormat) {
        UIManager.showError('Please select a target format');
        return;
    }

    console.log(`Converting ${currentUploadData.source_format} to ${targetFormat}`);

    try {
        // Show progress
        const progressInterval = UIManager.simulateProgress(3000);
        
        // Call conversion API (placeholder for now)
        const result = await FileConversionAPI.convertFile(
            currentUploadData.id,
            currentUploadData.source_format,
            targetFormat
        );
        
        clearInterval(progressInterval);
        UIManager.showProgress(100);
        
        // Wait a moment then show success
        setTimeout(() => {
            const downloadUrl = FileConversionAPI.getDownloadUrl(currentUploadData.id);
            const outputFilename = currentFile.name.replace(
                /\.[^/.]+$/, 
                `.${targetFormat}`
            );
            UIManager.showSuccess(downloadUrl, outputFilename);
        }, 500);
        
    } catch (error) {
        console.error('Conversion failed:', error);
        UIManager.showError(error.message || 'Conversion failed');
    }
}

// Reset and start new conversion
function resetUpload() {
    currentFile = null;
    currentUploadData = null;
    selectedCategory = null;
    
    // Reset file input
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Reset upload area title
    const uploadTitle = document.querySelector('.upload-area h2');
    if (uploadTitle) {
        uploadTitle.textContent = 'Drag & drop your file';
    }
    
    // Hide category indicator
    const categoryIndicator = document.getElementById('categoryIndicator');
    if (categoryIndicator) {
        categoryIndicator.classList.add('hidden');
    }
    
    // Remove category highlights
    document.querySelectorAll('.feature-card').forEach(card => {
        card.classList.remove('selected-category');
    });
    
    // Show upload section
    UIManager.showSection('uploadSection');
}

// Detect category from file format
function detectCategoryFromFormat(format) {
    const formatLower = format.toLowerCase();
    
    const categoryMap = {
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'epub'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff', 'tif', 'bmp', 'heic', 'svg', 'ico', 'raw'],
        'audio': ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'opus', 'wma'],
        'video': ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'webm', 'mpeg', 'mpg'],
        'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'gzip', 'bz2'],
        'code': ['json', 'xml', 'yaml', 'yml', 'csv', 'sql', 'md', 'html', 'css', 'js']
    };
    
    for (const [category, formats] of Object.entries(categoryMap)) {
        if (formats.includes(formatLower)) {
            return category;
        }
    }
    
    return null;
}
    
    // Show upload section
    UIManager.showSection('uploadSection');
}

// Make functions globally available
window.startConversion = startConversion;
window.resetUpload = resetUpload;
