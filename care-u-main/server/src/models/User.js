import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';

export const USER_ROLES = ['admin', 'staff', 'student'];

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, minlength: 2, maxlength: 120 },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    },
    // OJO: lo llenamos antes de validar (pre('validate'))
    passwordHash: { type: String, required: true, select: false },
    role: { type: String, enum: USER_ROLES, required: true, default: 'student' },
    bannedUntil: { type: Date, default: null },  // Fecha de baneo
    banReason: { type: String, default: '' },   // Razón del baneo
  },
  { timestamps: true }
);

// virtual para recibir el password en texto plano
userSchema.virtual('password')
  .set(function (plain) { this._password = plain; })
  .get(function () { return this._password; });

/**
 * Hasheamos ANTES de validar, para que passwordHash exista cuando corra la validación.
 */
userSchema.pre('validate', async function (next) {
  try {
    if (this._password) {
      if (this._password.length < 6) {
        return next(new Error('Password must be 6+ chars'));
      }
      this.passwordHash = await bcrypt.hash(this._password, 10);
    }

    // Si es nuevo y no llegó password ni passwordHash, marcamos error claramente
    if (this.isNew && !this.passwordHash) {
      return next(new Error('Password is required'));
    }

    next();
  } catch (err) {
    next(err);
  }
});

// método para comparar contraseñas
userSchema.methods.comparePassword = function (plain) {
  return bcrypt.compare(plain, this.passwordHash);
};

// Método para verificar si el usuario está baneado
userSchema.methods.isBanned = function () {
  return this.bannedUntil && new Date(this.bannedUntil) > new Date();
};

export const User = mongoose.model('User', userSchema);
