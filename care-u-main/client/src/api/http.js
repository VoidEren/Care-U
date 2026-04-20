import axios from 'axios';
import { API_URL } from '../config';

// Crea la instancia de axios
export const http = axios.create({
  baseURL: `${API_URL}/api`,
  withCredentials: false
});

// Configura el token en las cabeceras de la solicitud
export const setAuthToken = (token) => {
  if (token) {
    http.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete http.defaults.headers.common['Authorization'];
  }
};

