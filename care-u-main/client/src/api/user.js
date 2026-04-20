import { http } from './http';

export const getMe = (token) =>
  http.get('/users/me', { headers:{ Authorization:`Bearer ${token}` } });

export const updateMe = (payload, token) =>
  http.put('/users/me', payload, { headers:{ Authorization:`Bearer ${token}` } });

export const changePassword = (payload, token) =>
  http.put('/users/me/password', payload, { headers:{ Authorization:`Bearer ${token}` } });

export const banUser = async (userId, bannedUntil, reason) => {
  try {
    const response = await http.patch(`/users/ban/${userId}`, {
      bannedUntil,
      reason
    });
    return response.data; // Devuelve la respuesta del backend
  } catch (error) {
    console.error('Error al banear el usuario:', error);
    throw new Error('Error al banear el usuario');
  }
};


export const getUsers = async () => {
  try {
    const response = await http.get('/users'); // Llamada a la ruta del backend para obtener usuarios
    console.log('Usuarios obtenidos:', response.data); // Imprime la respuesta para ver su estructura
    return response.data; // Devuelve los usuarios
  } catch (error) {
    console.error('Error al obtener los usuarios:', error);
    throw error; // Lanza el error si algo sale mal
  }
};