import { useState } from 'react';
import { http } from '../api/http';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

export default function Signup() {
  const nav = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: null, text: '' });

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  async function onSubmit(e) {
    e.preventDefault();
    setMsg({ type: null, text: '' });
    setLoading(true);

    try {
      const { data } = await http.post('/auth/register', form);
      login(data.user, data.token);
      nav('/dashboard');
    } catch (err) {
      const api = err?.response?.data?.error;
      const text =
        api === 'Email already registered'
          ? 'El correo ya está registrado'
          : api || 'Error del servidor';

      setMsg({ type: 'error', text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card signup-card">
        <div className="login-logo">
          <img src="/logo.png" alt="Care-U" />
        </div>

        <h2>Crea tu cuenta</h2>
        <p>Regístrate para iniciar sesión con Care - U</p>

        <form onSubmit={onSubmit} className="login-form">
          <input
            className="login-input"
            name="name"
            placeholder="Nombre completo"
            value={form.name}
            onChange={onChange}
            required
          />

          <input
            className="login-input"
            name="email"
            type="email"
            placeholder="Correo electrónico"
            value={form.email}
            onChange={onChange}
            required
          />

          <input
            className="login-input"
            name="password"
            type="password"
            placeholder="Contraseña (mín 6)"
            value={form.password}
            onChange={onChange}
            minLength={6}
            required
          />

          <div className="signup-row">
            <select
              className="login-input signup-select"
              name="role"
              value={form.role}
              onChange={onChange}
            >
              <option value="student">Estudiante</option>
              <option value="staff">Personal</option>
              <option value="admin">Administrador</option>
            </select>

            <button className="login-btn signup-btn" disabled={loading}>
              {loading ? 'Creando...' : 'Registrarme'}
            </button>
          </div>

          {msg.text && (
            <div className={msg.type === 'error' ? 'login-error' : 'login-success'}>
              {msg.text}
            </div>
          )}
        </form>

        <div className="login-footer">
          <span>¿Ya tienes una cuenta? </span>
          <Link to="/login">Iniciar Sesión</Link>
        </div>
      </div>
    </div>
  );
}