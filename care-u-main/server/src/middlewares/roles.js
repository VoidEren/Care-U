export function requireRole(...roles) {
  return (req, res, next) => {
    // Verificamos si el usuario está autenticado (req.user viene de requireAuth)
    if (!req.user) return res.status(401).json({ error: 'No token' });

    // Verificamos si el rol del usuario está incluido en los roles permitidos
    if (!roles.includes(req.user.role)) return res.status(403).json({ error: 'Forbidden' });

    // Si el rol está permitido, pasamos al siguiente middleware
    next();
  };
}
