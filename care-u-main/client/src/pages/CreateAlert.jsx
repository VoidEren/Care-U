import { useState } from 'react';
import { createAlert } from '../api/alerts';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/theme.css';

const CATS = [
  { value: 'maintenance', label: 'Mantenimiento' },
  { value: 'safety', label: 'Seguridad' },
  { value: 'cleaning', label: 'Limpieza' },
  { value: 'it', label: 'TI' },
  { value: 'other', label: 'Otro' },
];

export default function CreateAlert() {
  const { token, user } = useAuth();
  const nav = useNavigate();

  const [form, setForm] = useState({
    text: '',
    category: 'maintenance',
    locationLabel: '',
  });

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: null, text: '' });

  const displayRole =
    user?.role === 'student'
      ? 'Alumno'
      : user?.role === 'staff'
      ? 'Personal'
      : user?.role === 'admin'
      ? 'Administrador'
      : 'Usuario';

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  async function onSubmit(e) {
    e.preventDefault();
    setMsg({ type: null, text: '' });
    setLoading(true);

    try {
      await createAlert(
        {
          text: form.text.trim(),
          category: form.category,
          location: { label: form.locationLabel.trim() },
        },
        token
      );

      nav('/alert-feed');
    } catch (err) {
      const text = err?.response?.data?.error || 'Error del servidor';
      setMsg({ type: 'error', text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="alert-create-page">
      <header className="alert-create-topbar">
        <div className="alert-create-brand">
          <div className="alert-create-brand-box">
            <div className="alert-create-brand-title">CARE-U</div>
            <div className="alert-create-brand-subtitle">Academic Alert System</div>
          </div>
        </div>

        <div className="alert-create-topbar-right">
          <div className="alert-create-bell">🔔</div>
          <div className="alert-create-user">
            <div className="alert-create-user-avatar">👤</div>
            <span>{displayRole}</span>
          </div>
        </div>
      </header>

      <div className="alert-create-body">
        <aside className="alert-create-sidebar">
          <div className="alert-create-side-icon">⌕</div>
          <div className="alert-create-side-icon">⌂</div>
          <div className="alert-create-side-icon">⚙</div>
        </aside>

        <main className="alert-create-content">
          <Link to="/dashboard" className="alert-create-back">
            ← Volver
          </Link>

          <h1 className="alert-create-title">Reportar alerta</h1>
          <p className="alert-create-subtitle">
            Describe, categoriza y localiza el problema
          </p>

          <form onSubmit={onSubmit} className="alert-create-form">
            <label className="alert-create-label">Descripción del problema</label>

            <textarea
              className="alert-create-textarea"
              name="text"
              rows={7}
              placeholder="¿Qué paso?"
              value={form.text}
              onChange={onChange}
              required
              minLength={5}
              maxLength={500}
            />

            <div className="alert-create-row">
              <select
                className="alert-create-input"
                name="category"
                value={form.category}
                onChange={onChange}
              >
                {CATS.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>

              <input
                className="alert-create-input"
                name="locationLabel"
                placeholder="Describe la ubicación de la incidencia"
                value={form.locationLabel}
                onChange={onChange}
                required
              />
            </div>

            <button className="alert-create-btn" disabled={loading}>
              {loading ? 'Enviando…' : 'Crear Incidencia'}
            </button>

            {msg.text && (
              <div className={msg.type === 'error' ? 'alert-create-error' : 'alert-create-success'}>
                {msg.text}
              </div>
            )}
          </form>
        </main>
      </div>
    </div>
  );
}