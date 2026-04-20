import { useState } from 'react';
import { http } from '../api/http';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

export default function Login() {
  const nav = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: null, text: '' });

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  async function onSubmit(e) {
    e.preventDefault();
    setMsg({ type: null, text: '' });
    setLoading(true);

    try {
      const { data } = await http.post('/auth/login', form);
      login(data.user, data.token);
      nav('/dashboard');
    } catch (err) {
      const api = err?.response?.data?.error;
      const text =
        api === 'Invalid credentials'
          ? 'Credenciales inválidas'
          : api || 'Error del servidor';
      setMsg({ type: 'error', text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <img src="/logo.png" alt="Care-U" />
        </div>

        <h2>Bienvenido</h2>
        <p>Inicia sesión para continuar</p>

        <form onSubmit={onSubmit} className="login-form">
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
            placeholder="Contraseña"
            value={form.password}
            onChange={onChange}
            required
          />

          <button className="login-btn" disabled={loading}>
            {loading ? 'Ingresando...' : 'Iniciar Sesión'}
          </button>

          {msg.text && (
            <div className={msg.type === 'error' ? 'login-error' : 'login-success'}>
              {msg.text}
            </div>
          )}
        </form>

        <div className="login-footer">
          <span>¿No tienes una cuenta? </span>
          <Link to="/signup">Regístrate</Link>
        </div>
      </div>
    </div>
  );
}