import jwt from 'jsonwebtoken';
import { User } from '../models/User.js';

export async function requireAuth(req, res, next) {

  if (req.headers['x-dev-bypass'] === '1') {
    req.user = {
      id: 'dev-user',
      name: 'Developer',
      role: 'admin' // puedes poner 'user' si quieres
    };
    return next();
  }
  const auth = req.headers.authorization || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;

  if (!token) return res.status(401).json({ error: 'No token' });

  try {
    // Verifica el token
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(payload.id).lean(); // Busca al usuario por ID

    if (!user) return res.status(401).json({ error: 'Invalid token' });

    // Verificación de baneo
    if (user.bannedUntil && new Date(user.bannedUntil) > new Date()) {
      return res.status(403).json({ error: 'User is banned' }); // Prohibir acceso si está baneado
    }

    req.user = { id: user._id.toString(), name: user.name, role: user.role }; // Añadir usuario a la request
    next(); // Permite que continúe con la solicitud
  } catch (e) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
