import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function AdminRoute({ children }) {
  const { user } = useAuth();
  /*
  // Verifica si el usuario tiene el rol de "admin"
  if (!user || user.role !== 'admin') {
    return <Navigate to="/login" replace />;
  }

  */
  return children;
}

export default AdminRoute;
