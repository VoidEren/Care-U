import mongoose from 'mongoose';

export const CATEGORIES = ['maintenance','safety','cleaning','it','other'];

const locationSchema = new mongoose.Schema({
  label: { type: String, required: true, trim: true }, // ej. "Edificio A, Aula 203"
  lat: { type: Number }, // opcional
  lng: { type: Number }  // opcional
},{ _id:false });

const postSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  text: { type: String, required: true, trim: true, minlength: 5, maxlength: 500 },
  category: { type: String, enum: CATEGORIES, required: true, index: true },
  location: { type: locationSchema, required: true },
  status: { type: String, enum: ['open','in_progress','resolved'], default: 'open', index: true }
},{ timestamps: true });

postSchema.index({ text: 'text' });
postSchema.index({ createdAt: -1 });

export const Post = mongoose.model('Post', postSchema);
