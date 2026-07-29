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
  try {
    const jsonStr = JSON.stringify(userData);
    const b64 = btoa(unescape(encodeURIComponent(jsonStr)));
    // Python expects: base64.b64decode(data[:-5][::-1])
    // So we must: 1) get base64 2) reverse it 3) append 5 random chars
    const reversed = b64.split('').reverse().join('');
    const randomChars = Math.random().toString(36).substring(2, 7).padEnd(5, 'x'); // Ensure exactly 5
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
