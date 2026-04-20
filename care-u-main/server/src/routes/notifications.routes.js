import { Router } from 'express';
import { requireAuth } from '../middlewares/requireAuth.js';
import { Notification } from '../models/Notification.js';

const router = Router();

// Mis notificaciones (no leídas primero)
router.get('/', requireAuth, async (req,res)=>{
  const items = await Notification.find({ user: req.user.id })
    .sort({ read:1, createdAt:-1 })
    .limit(50)
    .lean();
  res.json({ items, unread: items.filter(i=>!i.read).length });
});

// Marcar todas como leídas
router.post('/read-all', requireAuth, async (req,res)=>{
  await Notification.updateMany({ user: req.user.id, read:false }, { $set:{ read:true } });
  res.json({ ok:true });
});

export default router;
