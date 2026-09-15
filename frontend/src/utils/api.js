import axios from 'axios';

// Base API Configuration
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Utility to encode user data as required by the Python backend architecture.
 * The backend expects a JSON string that is then Base64 encoded.
 * Note: The Python side uses 'decode()' which usually implies a specific encoding,
 * but based on typical patterns in this codebase, Base64 is the primary candidate.
 */
export const encodeUserData = (userData) => {
  // Return JWT/itsdangerous token if present (for modern endpoints)
  if (userData && userData.token) {
    return userData.token;
  }
  
  // Legacy base64 encoding for manually constructed payloads (like editProfileUser, generateApiKey)
  try {
    const jsonStr = JSON.stringify(userData);
    const b64 = btoa(unescape(encodeURIComponent(jsonStr)));
    const reversed = b64.split('').reverse().join('');
    const randomChars = Math.random().toString(36).substring(2, 7).padEnd(5, 'x');
    return reversed + randomChars;
  } catch (e) {
    console.error('Encoding error:', e);
    return '';
  }
};

/**
 * Helper for POST requests that require the 'user' payload.
 */
export const postWithUser = async (url, userData, extraData = {}) => {
  const payload = {
    user: encodeUserData(userData),
    ...extraData,
  };
  return apiClient.post(url, payload);
};

export default apiClient;
