import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateIncident from './pages/CreateIncident';
import Feed from './pages/Feed';
import Profile from './pages/Profile';
import UserManagement from './pages/UserManagement';
import CreateAlert from './pages/CreateAlert';
import AlertFeed from './pages/AlertFeed';
import AdminPanel from './pages/AdminPanel';

export default function App(){
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/signup" element={<Signup/>} />
          <Route path="/login" element={<Login/>} />
          <Route path="/dashboard" element={<Dashboard/>} />
          <Route path="/feed" element={<Feed/>} />
          <Route path="/new" element={<CreateIncident/>} />
          <Route path="/profile" element={<Profile/>} />
          <Route path="/admin" element={<UserManagement/>} />
          <Route path="/create-alert" element={<CreateAlert/>} />
          <Route path="/alert-feed" element={<AlertFeed/>} />
          <Route path="/admin-panel" element={<AdminPanel/>} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}