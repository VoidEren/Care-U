import { useEffect, useRef, useState } from 'react';
import '../styles/theme.css';
import { listCategories, listPosts } from '../api/posts';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Feed() {
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
      const { data } = await listPosts({ category, q, page: p, limit: 6 });
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
    <div className="feed-page">

      {/* TOPBAR */}
      <header className="feed-topbar">
        <div className="feed-logo">CARE-U</div>

        <div className="feed-user">
          🔔 <span>{displayRole}</span>
        </div>
      </header>

      <div className="feed-body">

        {/* SIDEBAR */}
        <aside className="feed-sidebar">
          <div className="feed-icon">🔍</div>
          <div className="feed-icon">🏠</div>
          <div className="feed-icon">⚙</div>
        </aside>

        {/* CONTENIDO */}
        <main className="feed-content">

          <Link to="/dashboard" className="feed-back">← Volver</Link>

          <div className="feed-header">
            <h1>Feed de incidencias</h1>

            <form onSubmit={(e) => { e.preventDefault(); fetchData(1); }}>
              <input
                className="feed-search"
                placeholder="Buscar"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </form>
          </div>

          {/* TARJETAS */}
          <div className="feed-grid">
            {items.map((p) => (
              <div key={p._id} className="feed-card">

                <div className="feed-card-title">
                  ⚠ <span>{p.title || 'Problema detectado'}</span>
                </div>

                <p className="feed-card-text">
                  {p.text?.slice(0, 60)}...
                </p>

                <span className="feed-card-more">Ver más...</span>

              </div>
            ))}
          </div>

          {/* PAGINACIÓN */}
          <div className="feed-pagination">
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