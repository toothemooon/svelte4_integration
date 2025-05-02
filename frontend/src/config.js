// Use environment variable with fallbacks
export const API_URL = import.meta.env.VITE_API_URL || 
                      (import.meta.env.MODE === 'development' 
                       ? 'http://localhost:5001' 
                       : 'https://your-production-api-url.com');

console.log(`API_URL: ${API_URL}`);  // Debug logging