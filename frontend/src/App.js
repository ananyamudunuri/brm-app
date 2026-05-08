// frontend/src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import CustomerManagement from './components/CustomerManagement';
import NotesManagement from './components/NotesManagement';
import AffiliationsManagement from './components/AffiliationsManagement';
import UserManagement from './components/UserManagement';
import Navigation from './components/Navigation';
import ContactsPage from './components/ContactsPage';


const ProtectedLayout = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;
  
  return (
    <>
      <Navigation />
      <main>{children}</main>
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
          <Route path="/customers" element={<ProtectedLayout><CustomerManagement /></ProtectedLayout>} />
          <Route path="/notes" element={<ProtectedLayout><NotesManagement /></ProtectedLayout>} />
          <Route path="/affiliations" element={<ProtectedLayout><AffiliationsManagement /></ProtectedLayout>} />
          <Route path="/users" element={<ProtectedLayout><UserManagement /></ProtectedLayout>} />
          <Route path="/contacts" element={<ProtectedLayout><ContactsPage /></ProtectedLayout>} />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;