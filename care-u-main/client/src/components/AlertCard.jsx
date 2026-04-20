import '../styles/theme.css';
import { useAuth } from '../context/AuthContext';
import { updateAlertStatus } from '../api/alerts';
import { useState } from 'react';

const CAT_LABEL = { maintenance:'Mantenimiento', safety:'Seguridad', cleaning:'Limpieza', it:'TI', other:'Otro' };
const STATUS_LABEL = { open:'Abierta', in_progress:'En progreso', resolved:'Resuelta' };

export default function AlertCard({ alert, onChanged, isResolved }) {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  
  // Verificamos si el usuario puede gestionar (admin o personal)
  const canManage = user && (user.role === 'admin' || user.role === 'staff');

  // Función para actualizar el estado de la publicación
  async function setStatus(status) {
    if (!canManage) return;  // Si el usuario no tiene permisos, no hacer nada
    setLoading(true);
    try {
      await updateAlertStatus(alert._id, status, '', token);
      onChanged?.(); // Actualizar el feed
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      background: isResolved ? '#2c3e50' : '#0c162a',  // Color de fondo diferente para las publicaciones resueltas
      border: '1px solid #1f2a44',
      borderRadius: 12,
      padding: 16,
      display: 'grid',
      gap: 8,
      opacity: isResolved ? 0.6 : 1  // Disminuir la opacidad si está resuelta
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <div style={{ fontWeight: 700 }}>
          {alert.user?.name ?? 'Usuario'}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{
            fontSize: 12,
            padding: '4px 8px',
            borderRadius: 999,
            background: 'rgba(97,168,255,.14)',
            border: '1px solid #284a7a'
          }}>
            {CAT_LABEL[alert.category] || alert.category}
          </span>
          <span style={{
            fontSize: 12,
            padding: '4px 8px',
            borderRadius: 999,
            background: 'rgba(65,209,167,.12)',
            border: '1px solid #2b6b58'
          }}>
            {STATUS_LABEL[alert.status] || alert.status}
          </span>
        </div>
      </div>

      <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.45 }}>
        {alert.text}
      </div>
      <div className="helper">📍 {alert.location?.label} • {new Date(alert.createdAt).toLocaleString()}</div>

      {/* Mostrar botones solo si el usuario tiene permisos */}
      {canManage && (
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          {/* Botón para marcar como en progreso */}
          <button
            className="btn"
            disabled={loading || alert.status === 'in_progress' || alert.status === 'resolved'}
            onClick={() => setStatus('in_progress')}
          >
            Marcar en progreso
          </button>
          
          {/* Botón para marcar como resuelta */}
          <button
            className="btn"
            disabled={loading || alert.status === 'resolved'}
            onClick={() => setStatus('resolved')}
          >
            Marcar resuelta
          </button>
        </div>
      )}
    </div>
  );
}
