/**
 * Application configuration
 */

// API URL - Pointing to the live Azure backend for local development testing
// NOTE: When deploying the frontend to Vercel, this correctly points to Azure.
//       When running locally (`npm run dev`), this will ALSO point to Azure.
export const API_URL = 'https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net';

// Use the local backend for development
// export const API_URL = 'http://localhost:5001';

// Export other configuration as needed
export default {
  API_URL
}; 