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
  if (userData && userData.token) {
    return userData.token;
  }
  return '';
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
