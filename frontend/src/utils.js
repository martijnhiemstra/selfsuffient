/**
 * Utility functions for the application
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Default max upload size in bytes (5MB) - can be overridden by backend config
let MAX_UPLOAD_SIZE = 5 * 1024 * 1024;
let MAX_UPLOAD_SIZE_MB = 5;

/**
 * Fetch and cache the app configuration from the backend
 */
export const fetchAppConfig = async () => {
  try {
    const response = await fetch(`${API_URL}/api/config`);
    if (response.ok) {
      const config = await response.json();
      MAX_UPLOAD_SIZE = config.max_upload_size_bytes || MAX_UPLOAD_SIZE;
      MAX_UPLOAD_SIZE_MB = config.max_upload_size_mb || MAX_UPLOAD_SIZE_MB;
      return config;
    }
  } catch (error) {
    console.error('Failed to fetch app config:', error);
  }
  return { max_upload_size_bytes: MAX_UPLOAD_SIZE, max_upload_size_mb: MAX_UPLOAD_SIZE_MB };
};

/**
 * Get the maximum upload size in bytes
 * @returns {number} Maximum file size in bytes
 */
export const getMaxUploadSize = () => MAX_UPLOAD_SIZE;

/**
 * Get the maximum upload size in MB for display
 * @returns {number} Maximum file size in MB
 */
export const getMaxUploadSizeMB = () => MAX_UPLOAD_SIZE_MB;

/**
 * Validate file size before upload
 * @param {File} file - The file to validate
 * @returns {{ valid: boolean, error?: string }} Validation result
 */
export const validateFileSize = (file) => {
  if (!file) return { valid: false, error: 'No file selected' };
  
  if (file.size > MAX_UPLOAD_SIZE) {
    return {
      valid: false,
      error: `File too large. Maximum size is ${MAX_UPLOAD_SIZE_MB}MB. Your file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`
    };
  }
  
  return { valid: true };
};

/**
 * Validate image file type
 * @param {File} file - The file to validate
 * @returns {{ valid: boolean, error?: string }} Validation result
 */
export const validateImageType = (file) => {
  if (!file) return { valid: false, error: 'No file selected' };
  
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type. Allowed: JPEG, PNG, GIF, WEBP'
    };
  }
  
  return { valid: true };
};

/**
 * Validate an image file (both type and size)
 * @param {File} file - The file to validate
 * @returns {{ valid: boolean, error?: string }} Validation result
 */
export const validateImageFile = (file) => {
  const typeResult = validateImageType(file);
  if (!typeResult.valid) return typeResult;
  
  const sizeResult = validateFileSize(file);
  if (!sizeResult.valid) return sizeResult;
  
  return { valid: true };
};

/**
 * Get the full URL for an uploaded file/image
 * Uses the API endpoint to ensure CORS headers are applied
 * @param {string} imagePath - The image path from the database (e.g., "/uploads/projects/123/cover.png")
 * @param {string} token - Optional auth token for private images
 * @returns {string} The full URL to access the image
 */
export const getImageUrl = (imagePath, token = null) => {
  if (!imagePath) return null;
  
  // If it's already a full URL, return as-is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Convert /uploads/... path to /api/files/... for CORS support
  if (imagePath.startsWith('/uploads/')) {
    const filePath = imagePath.replace('/uploads/', '');
    let url = `${API_URL}/api/files/${filePath}`;
    // Add token for authenticated requests (needed for private gallery images)
    if (token) {
      url += `?token=${encodeURIComponent(token)}`;
    }
    return url;
  }
  
  // Fallback: prepend the API URL
  return `${API_URL}${imagePath}`;
};

/**
 * Strip HTML tags from a string
 * @param {string} html - HTML string to strip
 * @returns {string} Plain text without HTML tags
 */
export const stripHtml = (html) => {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '');
};

/**
 * Truncate text to a maximum length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text with ellipsis if needed
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...'
};
