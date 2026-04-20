import { useEffect, useState } from 'react';
import { listNotifications, readAllNotifications } from '../api/notifications';
import { useAuth } from '../context/AuthContext';

export default function NotificationsBell() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const unread = items.filter(i => !i.read).length;

  async function load() {
    try {
      const { data } = await listNotifications(token);
      setItems(data.items);
    } catch (e) {
      console.error('Error loading notifications', e);
    }
  }

  useEffect(() => {
    if (token) load();
  }, [token]);

  async function markAll() {
    try {
      await readAllNotifications(token);
      load();
    } catch (e) {
      console.error("Error marking notifications", e);
    }
  }

  function renderNotification(n) {
    const date = new Date(n.createdAt).toLocaleString();

    // 🔔 NOTIFICACIÓN DE ALERTA (cuando alguien crea una alerta)
    if (n.type === 'alert') {
      return (
        <>
          <b>🚨 Nueva alerta creada</b>  
          <br />{n.payload.text}
          <br /><i>Categoría:</i> {n.payload.category}
          <br /><i>Creador:</i> {n.payload.creator}
          <br />ID: {n.payload.alertId}
          <br /><span className="helper">{date}</span>
        </>
      );
    }

    // 🔧 NOTIFICACIÓN DE PROGRESO
    if (n.type === 'alert_progress') {
      return (
        <>
          <b>🔧 Tu alerta está en progreso</b>
          <br />ID: {n.payload.alertId}
          <br /><span className="helper">{date}</span>
        </>
      );
    }

    // ✅ NOTIFICACIÓN DE RESOLUCIÓN
    if (n.type === 'alert_resolved') {
      return (
        <>
          <b>✅ Tu alerta fue resuelta</b>
          <br />ID: {n.payload.alertId}
          <br /><span className="helper">{date}</span>
        </>
      );
    }

    // fallback
    return (
      <>
        Notificación desconocida  
        <br /><span className="helper">{date}</span>
      </>
    );
  }

  return (
    <div style={{ position: 'fixed', right: 16, bottom: 16, zIndex: 9999 }}>
      <button className="btn" onClick={() => setOpen(o => !o)}>
        🔔 Notificaciones {unread > 0 ? `(${unread})` : ''}
      </button>

      {open && (
        <div
          style={{
            marginTop: 8,
            width: 340,
            background: '#0c162a',
            border: '1px solid #1f2a44',
            borderRadius: 12,
            padding: 12,
            boxShadow: '0 10px 30px rgba(0,0,0,.35)'
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 8
            }}
          >
            <b>Notificaciones</b>
            <button className="btn" onClick={markAll}>
              Marcar como leídas
            </button>
          </div>

          <div style={{ display: 'grid', gap: 10, maxHeight: 260, overflowY: 'auto' }}>
            {items.map(n => (
              <div
                key={n._id}
                className="helper"
                style={{
                  borderBottom: '1px solid #1f2a44',
                  paddingBottom: 8
                }}
              >
                {renderNotification(n)}
              </div>
            ))}

            {items.length === 0 && (
              <div className="helper">Sin notificaciones</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
