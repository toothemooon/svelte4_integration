// Test script to check connection between Vercel frontend and local backend
async function testBackendConnection() {
  console.log('Starting backend connection test...');
  
  try {
    console.log('Attempting to connect to local backend at http://localhost:5001/api/health');
    const startTime = Date.now();
    const response = await fetch('http://localhost:5001/api/health');
    const endTime = Date.now();
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Successfully connected to backend!');
      console.log('Response data:', data);
      console.log(`Request took ${endTime - startTime}ms`);
    } else {
      console.error('❌ Backend returned an error status:', response.status);
    }
  } catch (err) {
    console.error('❌ Failed to connect to backend:', err.message);
    console.log('This error is expected when Vercel frontend tries to connect to localhost.');
    console.log('CORS error or network error are typical in this scenario.');
  }
  
  console.log('\nConclusion:');
  console.log('- If you\'re seeing this in your browser console on your local development server (localhost:8080),');
  console.log('  a successful connection means your local frontend can talk to your local backend.');
  console.log('- If you\'re seeing this in your browser console on your Vercel deployment (sarada.online),');
  console.log('  a connection error is expected and normal - Vercel cannot connect to your local machine.');
}

// Run the test
testBackendConnection(); 