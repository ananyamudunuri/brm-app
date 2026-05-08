// frontend/src/components/Navigation.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Notes as NotesIcon,
  Business as BusinessIcon,
  ContactPhone as ContactIcon,  // Add this import
  AdminPanelSettings as AdminIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { Avatar, Badge } from '@mui/material';

const Navigation = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <DashboardIcon />, color: '#667eea' },
    { path: '/customers', label: 'Customers', icon: <PeopleIcon />, color: '#4caf50' },
    { path: '/contacts', label: 'Contacts', icon: <ContactIcon />, color: '#2196f3' },  // Now ContactIcon is defined
    { path: '/notes', label: 'Notes', icon: <NotesIcon />, color: '#ff9800' },
    { path: '/affiliations', label: 'Affiliations', icon: <BusinessIcon />, color: '#9c27b0' },
    { path: '/users', label: 'Users', icon: <AdminIcon />, color: '#f44336' },
  ];

  return (
    <nav style={styles.nav}>
      <div style={styles.navContainer}>
        <div style={styles.logo}>
          <Avatar sx={{ bgcolor: 'white', color: '#667eea', width: 40, height: 40 }}>
            <BusinessIcon />
          </Avatar>
          <h2 style={styles.logoText}>BRM Platform</h2>
        </div>
        <div style={styles.navLinks}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                ...styles.navLink,
                ...(location.pathname === item.path ? styles.activeNavLink : {}),
                borderBottom: location.pathname === item.path ? `3px solid ${item.color}` : 'none'
              }}
            >
              <span style={{ color: item.color }}>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
        <div style={styles.userSection}>
          <Badge
            overlap="circular"
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            variant="dot"
            sx={{ '& .MuiBadge-badge': { bgcolor: '#4caf50' } }}
          >
            <Avatar sx={{ bgcolor: '#667eea' }}>
              {user?.email?.charAt(0).toUpperCase()}
            </Avatar>
          </Badge>
          <div style={styles.userInfo}>
            <span style={styles.userName}>{user?.full_name || user?.email?.split('@')[0]}</span>
            <span style={styles.userEmail}>{user?.email}</span>
          </div>
          <button onClick={logout} style={styles.logoutButton}>
            <LogoutIcon /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    background: 'white',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
  },
  navContainer: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: '70px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logoText: {
    margin: 0,
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    fontSize: '1.5rem',
  },
  navLinks: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  navLink: {
    textDecoration: 'none',
    color: '#666',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    borderRadius: '8px',
    transition: 'all 0.3s',
    fontSize: '14px',
    fontWeight: 500,
  },
  activeNavLink: {
    color: '#667eea',
    background: '#f0f0ff',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userInfo: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
  },
  userName: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#333',
  },
  userEmail: {
    fontSize: '12px',
    color: '#999',
  },
  logoutButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    background: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 500,
    transition: 'all 0.3s',
  },
};

export default Navigation;