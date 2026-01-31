// UI State Management
class UIManager {
    static init() {
        // Initialize theme
        UIManager.initTheme();
        
        // Setup theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', UIManager.toggleTheme);
        }
    }

    static initTheme() {
        // Check for saved theme preference or default to 'light'
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    static toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Add animation to button
        const button = document.getElementById('themeToggle');
        button.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            button.style.transform = '';
        }, 300);
    }

    static showSection(sectionId) {
        // Hide all sections
        const sections = ['uploadSection', 'fileInfoSection', 'progressSection', 'downloadSection', 'errorSection'];
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.add('hidden');
            }
        });

        // Show requested section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }
    }

    static showFileInfo(file, uploadData) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileFormat = document.getElementById('fileFormat');
        const fileIcon = document.getElementById('fileIcon');

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        if (fileFormat) {
            const format = file.name.split('.').pop().toUpperCase();
            fileFormat.innerHTML = `Format: <span>${format}</span>`;
        }

        // Set appropriate icon
        if (fileIcon) {
            fileIcon.textContent = UIManager.getFileIcon(file.name);
        }

        UIManager.showSection('fileInfoSection');
    }

    static getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        
        const iconMap = {
            // Documents
            pdf: '📄', doc: '📄', docx: '📄', txt: '📄', rtf: '📄',
            // Images
            jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', svg: '🖼️', webp: '🖼️',
            // Audio
            mp3: '🎵', wav: '🎵', aac: '🎵', ogg: '🎵', flac: '🎵',
            // Video
            mp4: '🎬', mkv: '🎬', avi: '🎬', mov: '🎬', webm: '🎬',
            // Archives
            zip: '📦', rar: '📦', '7z': '📦', tar: '📦',
            // Code
            json: '💻', xml: '💻', html: '💻', css: '💻', js: '💻'
        };

        return iconMap[ext] || '📁';
    }

    static showProgress(percentage = 0) {
        UIManager.showSection('progressSection');
        
        // Update linear progress bar
        const progressFill = document.getElementById('progressFill');
        const progressPercentage = document.getElementById('progressPercentage');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        if (progressPercentage) {
            progressPercentage.textContent = `${percentage}%`;
        }
        
        // Update circular progress ring
        const progressRing = document.getElementById('progressRing');
        if (progressRing) {
            const circumference = 2 * Math.PI * 36; // r = 36
            const offset = circumference - (percentage / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
        }
    }

    static showSuccess(downloadUrl, filename) {
        UIManager.showSection('downloadSection');
        const downloadBtn = document.getElementById('downloadBtn');
        
        if (downloadBtn) {
            downloadBtn.onclick = () => {
                window.location.href = downloadUrl;
            };
        }
    }

    static showError(errorMessage) {
        UIManager.showSection('errorSection');
        const errorMessageEl = document.getElementById('errorMessage');
        
        if (errorMessageEl) {
            errorMessageEl.textContent = errorMessage || 'An unknown error occurred';
        }
    }

    static updateFormatGrid(formats, category = 'all', currentFormat = null) {
        const formatGrid = document.getElementById('formatGrid');
        if (!formatGrid) return;

        formatGrid.innerHTML = '';

        let formatsToShow = [];
        if (category === 'all') {
            Object.values(formats).forEach(categoryFormats => {
                formatsToShow.push(...categoryFormats);
            });
            // Remove duplicates
            formatsToShow = [...new Set(formatsToShow)];
        } else {
            formatsToShow = formats[category] || [];
        }

        // Filter out current format
        if (currentFormat) {
            formatsToShow = formatsToShow.filter(f => f !== currentFormat.toLowerCase());
        }

        // Sort alphabetically
        formatsToShow.sort();

        formatsToShow.forEach(format => {
            const btn = document.createElement('button');
            btn.className = 'format-btn';
            btn.textContent = format.toUpperCase();
            btn.onclick = () => UIManager.selectFormat(format);
            formatGrid.appendChild(btn);
        });
    }

    static selectFormat(format) {
        // Remove previous selection
        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Add selection to clicked button
        event.target.classList.add('selected');

        // Show convert button
        const convertBtn = document.getElementById('convertBtn');
        if (convertBtn) {
            convertBtn.classList.remove('hidden');
            convertBtn.dataset.targetFormat = format;
        }
    }

    static setupCategoryTabs(formats, currentFormat) {
        const tabs = document.querySelectorAll('.tab-btn');
        
        tabs.forEach(tab => {
            tab.onclick = () => {
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update format grid
                const category = tab.dataset.category;
                UIManager.updateFormatGrid(formats, category, currentFormat);
            };
        });
    }

    static simulateProgress(duration = 3000) {
        let progress = 0;
        const interval = 50;
        const increment = (100 / duration) * interval;

        const progressInterval = setInterval(() => {
            progress += increment;
            if (progress >= 100) {
                progress = 100;
                clearInterval(progressInterval);
            }
            UIManager.showProgress(Math.floor(progress));
        }, interval);

        return progressInterval;
    }

    static showToast(title, message, type = 'info', duration = 3000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            info: 'i',
            warning: '⚠'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="18" y1="6" x2="6" y2="18" stroke-width="2" stroke-linecap="round"/>
                    <line x1="6" y1="6" x2="18" y2="18" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        `;

        container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    }
}

// Initialize theme on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => UIManager.init());
} else {
    UIManager.init();
}

// Export for use in other scripts
window.UIManager = UIManager;
