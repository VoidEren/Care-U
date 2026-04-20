import { createContext, useContext, useEffect, useState } from 'react'; 
import { setAuthToken } from '../api/http';

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const raw = localStorage.getItem('careu_auth');
    return raw ? JSON.parse(raw) : { user: null, token: null };
  });

  // 🔥 Cargar token guardado al iniciar la app
  useEffect(() => {
    if (auth.token) {
      setAuthToken(auth.token);
    }
  }, []);

  const login = (user, token) => {
    localStorage.setItem('careu_auth', JSON.stringify({ user, token }));
    setAuth({ user, token });
    setAuthToken(token);
  };

  const logout = () => {
    localStorage.removeItem('careu_auth');
    setAuth({ user: null, token: null });
    setAuthToken(null);
  };

  return (
    <AuthCtx.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
