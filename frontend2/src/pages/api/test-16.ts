import { NextApiHandler, NextApiRequest, NextApiResponse } from 'next';
import apiClient from '@/services/apiClient/client';

const fetchData = async (req: NextApiRequest, res: NextApiResponse) => {
  try {
   const response = await apiClient.get('/test-16');
   
   res.status(200).json(response.data);
 } catch(e) {
  console.log('error',e)
  res.status(500).end();
 }
}

export default fetchData