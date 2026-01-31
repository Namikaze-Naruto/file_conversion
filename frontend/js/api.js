// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

class FileConversionAPI {
    /**
     * Upload a file to the server
     */
    static async uploadFile(file, targetFormat = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (targetFormat) {
            formData.append('target_format', targetFormat);
        }

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * Get conversion status
     */
    static async getConversionStatus(conversionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversions/${conversionId}`);
            
            if (!response.ok) {
                throw new Error('Failed to get conversion status');
            }

            return await response.json();
        } catch (error) {
            console.error('Status check error:', error);
            throw error;
        }
    }

    /**
     * Convert a file
     */
    static async convertFile(conversionId, sourceFormat, targetFormat) {
        try {
            // Determine the conversion category/router based on format
            let endpoint = 'documents'; // default to documents
            
            const imageFormats = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'svg', 'ico', 'heic', 'raw', 'cr2', 'nef', 'arw'];
            const audioFormats = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'opus'];
            const videoFormats = ['mp4', 'mkv', 'avi', 'mov', 'webm', 'flv', 'wmv'];
            const archiveFormats = ['zip', 'rar', '7z', 'tar', 'gz', 'gzip', 'tgz'];
            const codeFormats = ['json', 'xml', 'yaml', 'yml', 'csv', 'html', 'md', 'markdown', 'ipynb'];
            const designFormats = ['psd', 'ai', 'dxf', 'dwg'];
            const databaseFormats = ['sql', 'parquet', 'avro'];
            const securityFormats = ['base64', 'encrypted', 'locked'];
            
            // Categorize by source format
            const sf = sourceFormat.toLowerCase();
            const tf = targetFormat.toLowerCase();
            
            if (imageFormats.includes(sf) || (imageFormats.includes(tf) && sf === 'pdf')) {
                endpoint = 'images';
            } else if (audioFormats.includes(sf) || (audioFormats.includes(tf) && sf === 'txt')) {
                endpoint = 'audio';
            } else if (videoFormats.includes(sf)) {
                endpoint = 'video';
            } else if (archiveFormats.includes(sf) || archiveFormats.includes(tf)) {
                endpoint = 'archives';
            } else if (codeFormats.includes(sf) || codeFormats.includes(tf)) {
                endpoint = 'code';
            } else if (designFormats.includes(sf)) {
                endpoint = 'design';
            } else if (databaseFormats.includes(sf) || (tf === 'sql' && ['csv', 'json', 'xlsx', 'xls'].includes(sf))) {
                endpoint = 'database';
            } else if (tf === 'hash' || tf === 'base64' || tf === 'encrypted' || tf === 'locked') {
                endpoint = 'security';
            } else if (tf === 'txt' && imageFormats.includes(sf)) {
                // OCR conversion
                endpoint = 'ai';
            } else if (tf === 'searchable_pdf' || tf === 'json' && (imageFormats.includes(sf) || sf === 'pdf')) {
                endpoint = 'ai';
            }
            
            // Create form data for the request
            const formData = new FormData();
            formData.append('target_format', targetFormat);
            
            const response = await fetch(`${API_BASE_URL}/${endpoint}/convert/${conversionId}`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Conversion failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Conversion error:', error);
            throw error;
        }
    }

    /**
     * Download converted file
     */
    static getDownloadUrl(conversionId) {
        return `${API_BASE_URL}/download/${conversionId}`;
    }

    /**
     * Get supported formats
     */
    static async getSupportedFormats() {
        try {
            const response = await fetch(`${API_BASE_URL}/formats`);
            
            if (!response.ok) {
                throw new Error('Failed to get supported formats');
            }

            return await response.json();
        } catch (error) {
            console.error('Get formats error:', error);
            // Return default formats if API fails
            return {
                document: ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'epub'],
                image: ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'heic', 'svg', 'ico', 'gif'],
                audio: ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'opus'],
                video: ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'webm'],
                archive: ['zip', 'rar', '7z', 'tar', 'gz'],
                code: ['json', 'xml', 'yaml', 'csv', 'md', 'html']
            };
        }
    }

    /**
     * Delete a conversion
     */
    static async deleteConversion(conversionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversions/${conversionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to delete conversion');
            }

            return await response.json();
        } catch (error) {
            console.error('Delete error:', error);
            throw error;
        }
    }
}

// Export for use in other scripts
window.FileConversionAPI = FileConversionAPI;
