import { useState, useEffect } from 'react';
import { http } from '../api/http';
import { useNavigate } from 'react-router-dom';

export default function AdminPanel() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Cargar los usuarios
    async function fetchUsers() {
      try {
        const { data } = await http.get('/api/users');
        setUsers(data.users);
      } catch (err) {
        setError('Error al cargar los usuarios');
      } finally {
        setLoading(false);
      }
    }

    fetchUsers();
  }, []);

  // Función para banear a un usuario
  async function banUser(userId) {
    try {
      const bannedUntil = new Date();
      bannedUntil.setDate(bannedUntil.getDate() + 7); // Baneo por 7 días
      const reason = prompt('Razón del baneo:', 'Violación de normas');
      
      if (!reason) return;

      await http.patch(`/api/users/ban/${userId}`, { bannedUntil, reason });
      alert('Usuario baneado exitosamente');
      // Refrescar la lista de usuarios
      setUsers(users.filter(user => user._id !== userId));
    } catch (err) {
      alert('Error al banear al usuario');
    }
  }

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="container">
      <div className="card" style={{ minWidth: 420 }}>
        <h2>Gestión de usuarios</h2>

        {error && <div className="error">{error}</div>}

        <table style={{ width: '100%', marginTop: '16px' }}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user._id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <button className="btn" onClick={() => banUser(user._id)}>
                    Banear
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
