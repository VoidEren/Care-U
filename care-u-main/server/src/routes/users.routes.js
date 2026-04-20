import { Router } from 'express';
import { requireAuth } from '../middlewares/requireAuth.js';
import { requireRole } from '../middlewares/roles.js';  // Para verificar que el usuario sea admin
import { User } from '../models/User.js';

import bcrypt from 'bcryptjs';

const router = Router();

// Obtener mi perfil
router.get('/me', requireAuth, async (req, res) => {
  const user = await User.findById(req.user.id).lean();
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json({ user });
});

// Actualizar nombre/correo
router.put('/me', requireAuth, async (req, res) => {
  try {
    const { name, email } = req.body;
    if (!name || !email) return res.status(400).json({ error: 'Missing fields' });

    const exists = await User.findOne({ _id: { $ne: req.user.id }, email: email.toLowerCase() }).lean();
    if (exists) return res.status(409).json({ error: 'Email already registered' });

    const updated = await User.findByIdAndUpdate(
      req.user.id,
      { $set: { name, email: email.toLowerCase() } },
      { new: true }
    ).lean();

    res.json({ user: updated });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

// Cambiar contraseña (requiere contraseña actual)
router.put('/me/password', requireAuth, async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  if (!currentPassword || !newPassword) return res.status(400).json({ error: 'Missing fields' });
  if (newPassword.length < 6) return res.status(400).json({ error: 'Password must be 6+ chars' });

  const user = await User.findById(req.user.id).select('+passwordHash');
  if (!user) return res.status(404).json({ error: 'Not found' });

  const ok = await user.comparePassword(currentPassword);
  if (!ok) return res.status(401).json({ error: 'Wrong current password' });

  user.password = newPassword; // virtual → se hashea
  await user.save();

  res.json({ ok: true });
});

// Obtener todos los usuarios (solo para admin)
router.get('/', requireAuth, requireRole('admin'), async (req, res) => {
  try {
    const users = await User.find().lean(); // Trae todos los usuarios
    res.json({ users });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

// RUTA para banear un usuario
router.patch('/ban/:id', requireAuth, requireRole('admin'), async (req, res) => {
  const { id } = req.params;
  const { bannedUntil, reason } = req.body;

  try {
    const user = await User.findById(id);
    if (!user) return res.status(404).json({ error: 'User not found' });

    user.bannedUntil = new Date(bannedUntil);  // Guardando la fecha de baneo
    user.banReason = reason; // Guardando la razón
    await user.save();

    res.status(200).json({ message: 'User banned successfully', user });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al banear el usuario' });
  }
});


export default router;
