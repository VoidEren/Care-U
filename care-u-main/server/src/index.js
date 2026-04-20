import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import authRouter from './routes/auth.routes.js';
import { connectDB } from './lib/db.js';
import { requireAuth } from './middlewares/requireAuth.js';
import postsRouter from './routes/posts.routes.js';
import notificationsRouter from './routes/notifications.routes.js';
import usersRouter from './routes/users.routes.js';
import alertRoutes from './routes/alert.routes.js';

const app = express();

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(express.json());
app.use(cookieParser());

app.get('/api/me', requireAuth, (req, res) => res.json({ user: req.user }));

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'CARE-U API', ts: new Date().toISOString() });
});

app.use('/api/auth', authRouter);
app.use('/api/posts', postsRouter);
app.use('/api/notifications', notificationsRouter);
app.use('/api/users', usersRouter);
app.use('/api/alerts', alertRoutes);

const { PORT = 4000, MONGODB_URI } = process.env;

connectDB(MONGODB_URI)
  .then(() => {
    app.listen(PORT, () => console.log(`✅ API http://localhost:${PORT}`));
  })
  .catch((err) => {
    console.error('❌ Error conectando a MongoDB:', err.message);
    process.exit(1);
  });
