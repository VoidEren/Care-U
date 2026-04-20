import { http } from './http';

export const listNotifications = (token)=>
  http.get('/notifications', { headers:{ Authorization:`Bearer ${token}` } });

export const readAllNotifications = (token)=>
  http.post('/notifications/read-all', {}, { headers:{ Authorization:`Bearer ${token}` } });
