import bcrypt from 'bcryptjs';

const users = []; // { id, name, email, passwordHash, role, createdAt }
let lastId = 0;

export async function createUser({ name, email, password, role }) {
  const exists = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (exists) {
    const err = new Error('Email already registered');
    err.code = 'EMAIL_TAKEN';
    throw err;
  }
  const passwordHash = await bcrypt.hash(password, 10);
  const user = {
    id: ++lastId,
    name,
    email: email.toLowerCase(),
    passwordHash,
    role,
    createdAt: new Date().toISOString()
  };
  users.push(user);
  return { ...user, passwordHash: undefined };
}

export async function verifyCredentials(email, password) {
  const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (!user) return null;
  const ok = await bcrypt.compare(password, user.passwordHash);
  if (!ok) return null;
  const { passwordHash, ...safe } = user;
  return safe;
}
