import { useEffect, useRef, useState } from 'react';
import '../styles/theme.css';
import { useAuth } from '../context/AuthContext';
import { listCategories, listAlert } from '../api/alerts';
import { Link } from 'react-router-dom';

export default function AlertFeed() {
  const { user } = useAuth();

  const [cats, setCats] = useState(['maintenance', 'safety', 'cleaning', 'it', 'other']);
  const [category, setCategory] = useState('all');
  const [q, setQ] = useState('');
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(false);

  const mounted = useRef(false);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await listCategories();
        if (Array.isArray(data?.categories)) setCats(data.categories);
      } catch {}
    })();
  }, []);

  async function fetchData(p = 1) {
    setLoading(true);
    try {
      const { data } = await listAlert({ category, q, page: p, limit: 6 });
      setItems(data.items || []);
      setPage(Number(data.page) || p);
      setPages(Number(data.pages) || 1);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      fetchData(1);
      return;
    }
    fetchData(1);
  }, [category]);

  const displayRole =
    user?.role === 'student' ? 'Alumno' :
    user?.role === 'staff' ? 'Personal' :
    user?.role === 'admin' ? 'Administrador' : 'Usuario';

  return (
    <div className="alert-feed-page">

      {/* TOPBAR */}
      <header className="alert-feed-topbar">
        <div className="alert-feed-logo">CARE-U</div>

        <div className="alert-feed-user">
          🔔 <span>{displayRole}</span>
        </div>
      </header>

      <div className="alert-feed-body">

        {/* SIDEBAR */}
        <aside className="alert-feed-sidebar">
          <div className="alert-feed-icon">🔍</div>
          <div className="alert-feed-icon">🏠</div>
          <div className="alert-feed-icon">⚙</div>
        </aside>

        {/* CONTENT */}
        <main className="alert-feed-content">

          <Link to="/dashboard" className="alert-feed-back">← Volver</Link>

          <div className="alert-feed-header">
            <h1>Feed de alertas</h1>

            <form onSubmit={(e) => { e.preventDefault(); fetchData(1); }}>
              <input
                className="alert-feed-search"
                placeholder="Buscar"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </form>
          </div>

          {/* CARDS */}
          <div className="alert-feed-grid">
            {items.map((p) => (
              <div key={p._id} className="alert-feed-card">

                <div className="alert-feed-card-title">
                  🔔 <span>{p.title || 'Alerta detectada'}</span>
                </div>

                <p className="alert-feed-card-text">
                  {p.text?.slice(0, 60)}...
                </p>

                <span className="alert-feed-card-more">Ver más...</span>

              </div>
            ))}
          </div>

          {/* PAGINATION */}
          <div className="alert-feed-pagination">
            <button disabled={page <= 1} onClick={() => fetchData(page - 1)}>
              Anterior
            </button>

            <button disabled={page >= pages} onClick={() => fetchData(page + 1)}>
              Siguiente
            </button>
          </div>

        </main>
      </div>
    </div>
  );
}