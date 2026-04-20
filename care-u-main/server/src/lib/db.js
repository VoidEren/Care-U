import mongoose from 'mongoose';

export async function connectDB(uri) {
  mongoose.set('strictQuery', true);
  await mongoose.connect(uri, {
    autoIndex: true,           // crea índices (incl. únicos)
    serverSelectionTimeoutMS: 10000,
  });
  console.log('✅ MongoDB conectado:', mongoose.connection.name);
}
