import { useAuth } from '../context/AuthContext';
import '../styles/theme.css';
import { Link, useNavigate } from 'react-router-dom';
import NotificationsBell from '../components/NotificationsBell';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const displayRole =
    user.role === 'student'
      ? 'Alumno'
      : user.role === 'staff'
      ? 'Personal'
      : user.role === 'admin'
      ? 'Administrador'
      : user.role;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dash-page">
      <header className="dash-topbar">
        <div className="dash-brand">
          <div className="dash-brand-box">
            <div className="dash-brand-title">CARE-U</div>
            <div className="dash-brand-subtitle">Academic Alert System</div>
          </div>
        </div>

        <div className="dash-topbar-right">
          <div className="dash-bell-wrap">
            <NotificationsBell />
          </div>

          <div className="dash-user">
            <div className="dash-user-avatar">👤</div>
            <span>{displayRole}</span>
          </div>
        </div>
      </header>

      <main className="dash-content">
        <h1 className="dash-title">Panel de Estudiante</h1>

        <p className="dash-welcome">
          Bienvenido <strong>{displayRole}</strong>
        </p>

        <p className="dash-subtitle">
          Gestiona incidencias y alertas desde este panel
        </p>

        <div className="dash-grid">
          <Link className="dash-card" to="/new">
            <div className="dash-card-icon warning">⚠</div>
            <span>Reportar Incidencia</span>
          </Link>

          <Link className="dash-card" to="/feed">
            <div className="dash-card-icon feed">📰</div>
            <span>Feed incidencias</span>
          </Link>

          <Link className="dash-card" to="/profile">
            <div className="dash-card-icon profile">👤</div>
            <span>Editar perfil</span>
          </Link>

          <Link className="dash-card" to="/create-alert">
            <div className="dash-card-icon alert">🔔</div>
            <span>Crear alerta</span>
          </Link>

          <Link className="dash-card" to="/alert-feed">
            <div className="dash-card-icon megaphone">📣</div>
            <span>Ver alertas</span>
          </Link>

          <button className="dash-card dash-card-button" onClick={handleLogout}>
            <div className="dash-card-icon logout">↪</div>
            <span>Cerrar Sesión</span>
          </button>

          {user.role === 'admin' && (
            <Link className="dash-card dash-card-admin" to="/admin">
              <div className="dash-card-icon admin">🛠</div>
              <span>Gestión de usuarios</span>
            </Link>
          )}
        </div>
      </main>
    </div>
  );
}