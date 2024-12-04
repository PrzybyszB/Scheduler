import axios from 'axios';
import isBrowser from '../isBrowser';

// if (isBrowser()) {
//   throw new Error('Accessible for sever side only');
// }

// axios instance
const apiClient = axios.create({ 
  baseURL: process.env.NEXT_PUBLIC_BASE_URL,
  timeout: 60000,
});
 
export default apiClient;