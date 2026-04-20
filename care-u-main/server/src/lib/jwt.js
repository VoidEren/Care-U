import jwt from 'jsonwebtoken';

// Se asegura de que `JWT_SECRET` esté disponible en el entorno de producción
const { JWT_SECRET = 'change_me' } = process.env;

// Función para firmar el token con el payload y una fecha de expiración de 7 días por defecto
export function signToken(payload, options = {}) {
  try {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d', ...options });
  } catch (error) {
    console.error("Error al firmar el token:", error);
    throw new Error("Error al generar el token");
  }
}

// Función para verificar el token JWT recibido y obtener el payload
export function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    console.error("Error al verificar el token:", error);
    throw new Error("Token inválido o expirado");
  }
}
