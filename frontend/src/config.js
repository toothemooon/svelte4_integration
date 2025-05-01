/**
 * Application configuration
 */

// Set the API URL based on the environment
// In production (Vercel), use the Azure backend URL
// In development, use the local backend URL
export const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net'
  : 'http://localhost:5001';

// Export other configuration as needed
export default {
  API_URL
}; 