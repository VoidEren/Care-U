import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getMe, updateMe, changePassword } from '../api/user';
import '../styles/theme.css';

export default function Profile() {
  const { token, login, user } = useAuth();

  const [info, setInfo] = useState({ name: '', email: '' });
  const [pwd, setPwd] = useState({ currentPassword: '', newPassword: '' });
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await getMe(token);
        setInfo({
          name: data.user?.name || '',
          email: data.user?.email || '',
        });
      } catch {}
    })();
  }, [token]);

  const displayRole =
    user?.role === 'student'
      ? 'Alumno'
      : user?.role === 'staff'
      ? 'Personal'
      : user?.role === 'admin'
      ? 'Administrador'
      : 'Usuario';

  async function saveAll(e) {
    e.preventDefault();
    setMsg('');
    setLoading(true);

    try {
      const { data } = await updateMe(info, token);
      login(data.user, token);

      if (pwd.currentPassword && pwd.newPassword) {
        await changePassword(pwd, token);
        setPwd({ currentPassword: '', newPassword: '' });
      }

      setMsg('Datos guardados correctamente');
    } catch (err) {
      const api = err?.response?.data?.error;
      setMsg(
        api === 'Email already registered'
          ? 'El correo ya está registrado'
          : api === 'Wrong current password'
          ? 'Contraseña actual incorrecta'
          : api || 'Error'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="profile-page">
      <header className="profile-topbar">
        <div className="profile-brand">
          <div className="profile-brand-box">
            <div className="profile-brand-title">CARE-U</div>
            <div className="profile-brand-subtitle">Academic Alert System</div>
          </div>
        </div>

        <div className="profile-topbar-right">
          <div className="profile-bell">🔔</div>
          <div className="profile-user">
            <div className="profile-user-avatar">👤</div>
            <span>{displayRole}</span>
          </div>
        </div>
      </header>

      <div className="profile-body">
        <aside className="profile-sidebar">
          <div className="profile-side-icon">⌕</div>
          <div className="profile-side-icon">⌂</div>
          <div className="profile-side-icon">⚙</div>
        </aside>

        <main className="profile-content">
          <Link to="/dashboard" className="profile-back">
            ← Volver
          </Link>

          <h1 className="profile-title">Editar perfil</h1>

          <form onSubmit={saveAll} className="profile-form-layout">
            <div className="profile-left">
              <label className="profile-upload-label">Subir imagen</label>
              <input className="profile-file-input" type="file" accept="image/*" />
            </div>

            <div className="profile-right">
              <input
                className="profile-input"
                type="text"
                placeholder="Nombre completo"
                value={info.name}
                onChange={(e) => setInfo({ ...info, name: e.target.value })}
                required
              />

              <input
                className="profile-input"
                type="email"
                placeholder="Correo electrónico"
                value={info.email}
                onChange={(e) => setInfo({ ...info, email: e.target.value })}
                required
              />

              <input
                className="profile-input"
                type="password"
                placeholder="Contraseña actual"
                value={pwd.currentPassword}
                onChange={(e) =>
                  setPwd({ ...pwd, currentPassword: e.target.value })
                }
              />

              <input
                className="profile-input"
                type="password"
                placeholder="Contraseña nueva"
                value={pwd.newPassword}
                onChange={(e) =>
                  setPwd({ ...pwd, newPassword: e.target.value })
                }
                minLength={6}
              />

              <button className="profile-btn" disabled={loading}>
                {loading ? 'Guardando…' : 'Guardar'}
              </button>

              {msg && <div className="profile-msg">{msg}</div>}
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}