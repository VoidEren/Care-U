import { Router } from 'express';
import { requireAuth } from '../middlewares/requireAuth.js';
import { requireRole } from '../middlewares/roles.js';
import { Alert, CATEGORIES } from '../models/Alert.js';
import { Notification } from '../models/Notification.js';
import mongoose from 'mongoose';

const router = Router();

// HU03 — Crear incidencia
// HU03 — Crear Alerta y notificar a todos
router.post('/', requireAuth, async (req, res) => {
  try {
    const { text, category, location } = req.body;

    if (!text || !category || !location?.label) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    if (!CATEGORIES.includes(category)) {
      return res.status(400).json({ error: 'Invalid category' });
    }

    // 1️⃣ Crear la alerta
    const doc = await Alert.create({
      user: req.user.id,
      text,
      category,
      location: { label: String(location.label) }
    });

    const populated = await doc.populate('user', 'name role');

    // 2️⃣ Obtener todos los usuarios
    const users = await mongoose.model("User").find().select("_id");

    // 3️⃣ Crear notificación para cada usuario
    const notis = users.map(u => ({
      user: u._id,
      type: 'alert',  // 🔔 tipo de notificación
      payload: {
        alertId: doc._id.toString(),
        text: doc.text,
        category: doc.category,
        creator: populated.user.name
      }
    }));

    await Notification.insertMany(notis);

    // Respuesta final
    res.status(201).json({ alert: populated });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});


// **Nueva ruta para obtener las categorías** (esto es lo que falta)
router.get('/categories', (req, res) => {
  try {
    res.json({ categories: CATEGORIES });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

// HU04 — Listar feed con filtros
router.get('/', async (req, res) => {
  try {
    const { category, q, page = 1, limit = 10 } = req.query;
    const filt = {};
    if (category && category !== 'all') filt.category = category;
    if (q) filt.$text = { $search: q };

    const skip = (Number(page) - 1) * Number(limit);

    const [items, total] = await Promise.all([
      Alert.find(filt)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(Number(limit))
        .populate('user', 'name role')
        .lean(),
      Alert.countDocuments(filt)
    ]);

    res.json({ items, total, page: Number(page), pages: Math.ceil(total / Number(limit)) });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

// HU08 — Cambiar estado y notificar (admin/staff)
router.patch('/:id/status', requireAuth, requireRole('admin', 'staff'), async (req, res) => {
  try {
    const { id } = req.params;
    const { status, note } = req.body;

    // Validar si el estado es válido
    if (!['in_progress', 'resolved'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    // Validar si el ID es válido
    if (!mongoose.isValidObjectId(id)) return res.status(400).json({ error: 'Invalid id' });

    // Actualizar el estado de la publicación
    const alert = await Alert.findByIdAndUpdate(
      id,
      { $set: { status } },
      { new: true }
    ).populate('user', 'name role');
    if (!alert) return res.status(404).json({ error: 'Alert not found' });

    // Crear una notificación para el usuario
    await Notification.create({
      user: alert.user._id,
      type: status === 'resolved' ? 'alert_resolved' : 'alert_progress',
      payload: { alertId: alert._id.toString(), status, note: note?.slice(0, 300) }
    });

    res.json({ alert });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router; // 👈 IMPORTANTE
