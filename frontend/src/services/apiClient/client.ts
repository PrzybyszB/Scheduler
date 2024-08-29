import axios from 'axios';
import isBrowser from '../isBrowser';

// if (isBrowser()) {
//   throw new Error('Accessible for sever side only');
// }

// axios instance
const apiClient = axios.create({ 
  baseURL: process.env.BASE_URL, //'http://localhost:8000/api',
  timeout: 60000,
});
 
export default apiClient;