/**
 * Application configuration
 */

// Set the API URL based on the environment
// In production (determined by checking the URL), use the Azure backend URL
// In development, use the local backend URL
const isProduction = window.location.hostname !== 'localhost' && 
                    window.location.hostname !== '127.0.0.1';

export const API_URL = isProduction
  ? 'https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net'
  : 'http://localhost:5001';

// Export other configuration as needed
export default {
  API_URL
}; 