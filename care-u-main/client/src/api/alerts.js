import { http } from './http';

export function createAlert(payload, token){
  return http.post('/alerts', payload, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function listAlert(params = {}){
  return http.get('/alerts', { params });
}

export function listCategories(){
  return http.get('/alerts/categories');
}

export function updateAlertStatus(id, status, note, token){
  return http.patch(`/alerts/${id}/status`, { status, note }, {
    headers: { Authorization: `Bearer ${token}` }
  });
}