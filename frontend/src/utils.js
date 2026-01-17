/**
 * Utility functions for the application
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

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
