import { request } from './request';

export const API_BASE_URL = 'http://localhost:8000/api';

export async function checkHealth() {
  await request({
    url: API_BASE_URL + '/health',
  });
}
