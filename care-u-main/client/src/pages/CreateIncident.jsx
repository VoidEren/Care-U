import { useState } from 'react';
import { createPost } from '../api/posts';
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

export default function CreateIncident() {
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
      await createPost(
        {
          text: form.text.trim(),
          category: form.category,
          location: { label: form.locationLabel.trim() },
        },
        token
      );

      nav('/feed');
    } catch (err) {
      const text = err?.response?.data?.error || 'Error del servidor';
      setMsg({ type: 'error', text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="incident-page">
      <header className="incident-topbar">
        <div className="incident-brand">
          <div className="incident-brand-box">
            <div className="incident-brand-title">CARE-U</div>
            <div className="incident-brand-subtitle">Academic Alert System</div>
          </div>
        </div>

        <div className="incident-topbar-right">
          <div className="incident-bell">🔔</div>
          <div className="incident-user">
            <div className="incident-user-avatar">👤</div>
            <span>{displayRole}</span>
          </div>
        </div>
      </header>

      <div className="incident-body">
        <aside className="incident-sidebar">
          <div className="incident-side-icon">⌕</div>
          <div className="incident-side-icon">⌂</div>
          <div className="incident-side-icon">⚙</div>
        </aside>

        <main className="incident-content">
          <Link to="/dashboard" className="incident-back">
            ← Volver
          </Link>

          <h1 className="incident-title">Reportar Incidencia</h1>
          <p className="incident-subtitle">
            Describe, categoriza y localiza el problema
          </p>

          <form onSubmit={onSubmit} className="incident-form">
            <label className="incident-label">Descripción del problema</label>

            <textarea
              className="incident-textarea"
              name="text"
              rows={7}
              placeholder="¿Qué paso?"
              value={form.text}
              onChange={onChange}
              required
              minLength={5}
              maxLength={500}
            />

            <div className="incident-row">
              <select
                className="incident-input"
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
                className="incident-input"
                name="locationLabel"
                placeholder="Describe la ubicación de la incidencia"
                value={form.locationLabel}
                onChange={onChange}
                required
              />
            </div>

            <button className="incident-btn" disabled={loading}>
              {loading ? 'Enviando…' : 'Crear Incidencia'}
            </button>

            {msg.text && (
              <div className={msg.type === 'error' ? 'incident-error' : 'incident-success'}>
                {msg.text}
              </div>
            )}
          </form>
        </main>
      </div>
    </div>
  );
}