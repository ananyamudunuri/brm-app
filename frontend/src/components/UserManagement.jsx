import React, { useState, useEffect } from 'react';
import {
  Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, Typography, CircularProgress, Alert, Snackbar, Avatar,
  Card, Grid, Button, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, FormControl, InputLabel, Select, MenuItem,
  Switch, FormControlLabel, LinearProgress
} from '@mui/material';
import { People, AdminPanelSettings, Person, Email, CalendarToday, Refresh, Add, Edit, Delete } from '@mui/icons-material';
import api from '../api';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    roles: 'user',
    is_active: true
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data || []);
    } catch (error) {
      if (error.response?.status === 403) {
        setError('Admin access required.');
      } else {
        setError('Failed to load users');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.email || !formData.username) {
      showSnackbar('Email and username are required', 'error');
      return;
    }

    if (!editingUser && !formData.password) {
      showSnackbar('Password is required for new users', 'error');
      return;
    }

    setSaving(true);
    try {
      if (editingUser) {
        const updateData = { email: formData.email, username: formData.username, full_name: formData.full_name, roles: formData.roles, is_active: formData.is_active };
        if (formData.password) updateData.password = formData.password;
        await api.put(`/admin/users/${editingUser.id}`, updateData);
        showSnackbar('User updated successfully', 'success');
      } else {
        await api.post('/admin/users', formData);
        showSnackbar('User created successfully', 'success');
      }
      handleCloseDialog();
      fetchUsers();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Error saving user', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (user) => {
    if (window.confirm(`Delete user "${user.email}"?`)) {
      try {
        await api.delete(`/admin/users/${user.id}`);
        showSnackbar('User deleted successfully', 'success');
        fetchUsers();
      } catch (error) {
        showSnackbar('Error deleting user', 'error');
      }
    }
  };

  const handleOpenDialog = (user = null) => {
    if (user) {
      setEditingUser(user);
      setFormData({ email: user.email, username: user.username, password: '', full_name: user.full_name || '', roles: user.roles || 'user', is_active: user.is_active });
    } else {
      setEditingUser(null);
      setFormData({ email: '', username: '', password: '', full_name: '', roles: 'user', is_active: true });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  if (loading) return <LinearProgress />;
  if (error) return <Alert severity="error" sx={{ m: 3 }}>{error}</Alert>;

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', p: 3 }}>
      <Card sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Box sx={{ p: 3, background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}><People sx={{ fontSize: 32 }} /></Avatar>
            <Typography variant="h5" fontWeight="bold">User Management</Typography>
          </Box>
          <Button variant="contained" startIcon={<Add />} onClick={() => handleOpenDialog()} sx={{ bgcolor: 'white', color: '#2196f3' }}>Add User</Button>
        </Box>

        <Grid container spacing={2} sx={{ p: 3, bgcolor: '#fafafa' }}>
          <Grid item xs={12} sm={4}><Paper sx={{ p: 2, textAlign: 'center' }}><Typography variant="h3" fontWeight="bold" color="#2196f3">{users.length}</Typography><Typography variant="body2">Total Users</Typography></Paper></Grid>
          <Grid item xs={12} sm={4}><Paper sx={{ p: 2, textAlign: 'center' }}><Typography variant="h3" fontWeight="bold" color="#f44336">{users.filter(u => u.roles?.includes('admin')).length}</Typography><Typography variant="body2">Admins</Typography></Paper></Grid>
          <Grid item xs={12} sm={4}><Paper sx={{ p: 2, textAlign: 'center' }}><Typography variant="h3" fontWeight="bold" color="#4caf50">{users.filter(u => u.is_active).length}</Typography><Typography variant="body2">Active Users</Typography></Paper></Grid>
        </Grid>

        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#f5f5f5' }}>
              <TableRow><TableCell><strong>User</strong></TableCell><TableCell><strong>Email</strong></TableCell><TableCell><strong>Username</strong></TableCell><TableCell><strong>Roles</strong></TableCell><TableCell><strong>Status</strong></TableCell><TableCell><strong>Actions</strong></TableCell></TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id} hover>
                  <TableCell><Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}><Avatar sx={{ bgcolor: user.roles?.includes('admin') ? '#f44336' : '#4caf50' }}>{user.roles?.includes('admin') ? <AdminPanelSettings /> : <Person />}</Avatar><Box><Typography variant="body1" fontWeight="bold">{user.full_name || user.username}</Typography></Box></Box></TableCell>
                  <TableCell><Email sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />{user.email}</TableCell>
                  <TableCell>@{user.username}</TableCell>
                  <TableCell>{user.roles?.split(',').map((role, i) => <Chip key={i} label={role.trim()} size="small" sx={{ mr: 0.5, bgcolor: role.trim() === 'admin' ? '#ffebee' : '#e8f5e9', color: role.trim() === 'admin' ? '#f44336' : '#4caf50' }} />)}</TableCell>
                  <TableCell><Chip label={user.is_active ? 'Active' : 'Inactive'} size="small" sx={{ bgcolor: user.is_active ? '#e8f5e9' : '#ffebee', color: user.is_active ? '#4caf50' : '#f44336' }} /></TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary" onClick={() => handleOpenDialog(user)}><Edit /></IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(user)}><Delete /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: editingUser ? '#2196f3' : '#4caf50', color: 'white' }}>{editingUser ? 'Edit User' : 'Add New User'}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Email" type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} sx={{ mt: 2 }} required disabled={!!editingUser} />
          <TextField fullWidth label="Username" value={formData.username} onChange={(e) => setFormData({...formData, username: e.target.value})} sx={{ mt: 2 }} required disabled={!!editingUser} />
          <TextField fullWidth label={editingUser ? "Password (leave blank to keep)" : "Password"} type="password" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} sx={{ mt: 2 }} required={!editingUser} />
          <TextField fullWidth label="Full Name" value={formData.full_name} onChange={(e) => setFormData({...formData, full_name: e.target.value})} sx={{ mt: 2 }} />
          <FormControl fullWidth sx={{ mt: 2 }}><InputLabel>Role</InputLabel><Select value={formData.roles} label="Role" onChange={(e) => setFormData({...formData, roles: e.target.value})}><MenuItem value="user">User</MenuItem><MenuItem value="admin">Admin</MenuItem></Select></FormControl>
          <FormControlLabel control={<Switch checked={formData.is_active} onChange={(e) => setFormData({...formData, is_active: e.target.checked})} />} label="Active Account" sx={{ mt: 2 }} />
        </DialogContent>
        <DialogActions><Button onClick={handleCloseDialog}>Cancel</Button><Button onClick={handleSubmit} variant="contained" disabled={saving}>{saving ? <CircularProgress size={24} /> : (editingUser ? 'Update' : 'Create')}</Button></DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({...snackbar, open: false})}><Alert severity={snackbar.severity}>{snackbar.message}</Alert></Snackbar>
    </Box>
  );
};

export default UserManagement;
