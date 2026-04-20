import { Router } from 'express';
import { signToken } from '../lib/jwt.js';
import { User, USER_ROLES } from '../models/User.js';

const router = Router();

// HU01 — Registro (Sign up)
router.post('/register', async (req, res) => {
  try {
    const { name, email, password, role } = req.body;

    // Validación de campos
    if (!name || !email || !password || !role) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    // Validar que el rol sea uno de los permitidos
    if (!USER_ROLES.includes(role)) {
      return res.status(400).json({ error: 'Invalid role' });
    }

    // Verificar si el email ya está registrado
    const exists = await User.findOne({ email: email.toLowerCase() }).lean();
    if (exists) return res.status(409).json({ error: 'Email already registered' });

    // Crear el usuario y asignar el rol
    const user = new User({ name, email, role });
    user.password = password; // El rol ya se asigna al crear el objeto de usuario
    await user.save();

    // Generar el token JWT
    const token = signToken({ id: user._id.toString(), role: user.role });

    // Limpio la respuesta para no enviar el campo passwordHash
    const { passwordHash, ...safe } = user.toObject();

    // Responder con el usuario y el token
    return res.status(201).json({ user: safe, token });
  } catch (e) {
    // Detección de índice único (duplicate key)
    if (e?.code === 11000) {
      return res.status(409).json({ error: 'Email already registered' });
    }
    console.error(e);
    return res.status(500).json({ error: 'Server error' });
  }
});

// HU02 — Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validar que se proporcionen las credenciales
    if (!email || !password)
      return res.status(400).json({ error: 'Missing credentials' });

    // Buscar al usuario y traer también el passwordHash
    const user = await User.findOne({ email: email.toLowerCase() }).select('+passwordHash');
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    // Comparar la contraseña
    const ok = await user.comparePassword(password);
    if (!ok) return res.status(401).json({ error: 'Invalid credentials' });

    // Generar el token JWT
    const token = signToken({ id: user._id.toString(), role: user.role });

    // Limpiar la respuesta para no enviar el passwordHash
    const { passwordHash, ...safe } = user.toObject();

    // Responder con el usuario y el token
    return res.json({ user: safe, token });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: 'Server error' });
  }
});


export default router;
