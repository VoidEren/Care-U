import React, { useState, useEffect } from 'react';
import { getUsers, banUser } from '../api/user'; // Asegúrate de que las funciones estén correctamente importadas
import './UserManagement.css';


export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [banUserData, setBanUserData] = useState({ show: false, userId: '', bannedUntil: '', reason: '' });
  const [message, setMessage] = useState(''); // Estado para almacenar el mensaje de confirmación

  useEffect(() => {
    // Cargar los usuarios al montar el componente
    const fetchUsers = async () => {
      try {
        const data = await getUsers(); // Obtener los datos de la API
        console.log('Usuarios obtenidos:', data); // Verifica la estructura de los datos aquí
        // Acceder al array de usuarios dentro del objeto
        if (Array.isArray(data.users)) {
          setUsers(data.users); // Actualiza el estado con el array de usuarios
        } else {
          console.error('Los datos no contienen un array de usuarios', data);
        }
      } catch (error) {
        console.error('Error al cargar los usuarios:', error); // Manejo de errores
      }
    };
    fetchUsers();
  }, []);

  // Manejo del banear usuario
  const handleBan = (userId) => {
    setBanUserData({ ...banUserData, show: true, userId });
  };

  const handleSubmitBan = async () => {
    const { userId, bannedUntil, reason } = banUserData;
    try {
      // Banear al usuario
      const response = await banUser(userId, bannedUntil, reason);

      // Verificar si el usuario fue baneado correctamente
      if (response.status === 200) {
        setMessage(`El usuario ha sido baneado por ${bannedUntil} días.`);
      } else {
        setMessage('Este usuario ya está baneado.');
      }

      // Cerrar el modal
      setBanUserData({ ...banUserData, show: false });

      // Actualizar los usuarios después de banear
      const updatedUsers = await getUsers();
      setUsers(updatedUsers.users); // Asegúrate de acceder al array de usuarios
    } catch (error) {
      setMessage('Error al banear al usuario.');
      console.error('Error al banear el usuario:', error);
    }
  };

  return (
    <div>
      <h2>Gestión de Usuarios</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.length > 0 ? (
            users.map((user) => (
              <tr key={user._id}>
                <td>{user.name}</td>
                <td>{user.role}</td>
                <td>
                  <button onClick={() => handleBan(user._id)}>Banear</button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3">No hay usuarios disponibles</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Mostrar el mensaje de confirmación */}
      {message && <div className="message">{message}</div>}

      {/* Modal para banear */}
      {banUserData.show && (
        <div className="modal">
          <div className="modal-content">
            <h3>Banear Usuario</h3>
            <form>
              <label>Tiempo (en días):</label>
              <input
                type="number"
                value={banUserData.bannedUntil}
                onChange={(e) => setBanUserData({ ...banUserData, bannedUntil: e.target.value })}
              />
              <br />
              <label>Razón:</label>
              <textarea
                value={banUserData.reason}
                onChange={(e) => setBanUserData({ ...banUserData, reason: e.target.value })}
              />
              <br />
              <button type="button" onClick={handleSubmitBan}>Aceptar</button>
              <button type="button" onClick={() => setBanUserData({ ...banUserData, show: false })}>Cancelar</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
