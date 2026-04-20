import mongoose from "mongoose";

const notificationSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref:'User', index:true, required:true },
  type: { 
    type: String, 
    enum: ['post_resolved', 'post_progress', 'alert'],  // Añadimos el tipo 'alert' para las alertas
    required: true 
  },
  payload: { 
    type: Object, 
    default: {} // Esto contiene la información sobre la alerta o incidencia
  },
  read: { type: Boolean, default: false, index: true }
}, { timestamps: true });


export const Notification = mongoose.model("Notification", notificationSchema);
