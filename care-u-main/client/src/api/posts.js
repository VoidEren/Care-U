import { http } from './http';

export function createPost(payload, token){
  return http.post('/posts', payload, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function listPosts(params = {}){
  return http.get('/posts', { params });
}

export function listCategories(){
  return http.get('/posts/categories');
}

export function updatePostStatus(id, status, note, token){
  return http.patch(`/posts/${id}/status`, { status, note }, {
    headers: { Authorization: `Bearer ${token}` }
  });
}