import React, { useState, useEffect } from 'react';
import {
  Box, Button, Card, CardContent, Typography, Grid, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField, Select,
  MenuItem, FormControl, InputLabel, Chip, IconButton, Alert,
  Snackbar, CircularProgress, Avatar, Divider, LinearProgress
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Note as NoteIcon, Person as PersonIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import api from '../api';

const NotesManagement = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [notes, setNotes] = useState([]);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    note_text: '',
    note_type: 'GENERAL'
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/crm/customers?limit=100');
      if (response.data && response.data.data) {
        setCustomers(response.data.data);
      } else {
        setCustomers([]);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoadingCustomers(false);
    }
  };

  const fetchCustomerNotes = async (customerId) => {
    setLoadingNotes(true);
    try {
      const response = await api.get(`/crm/customers/${customerId}/notes`);
      setNotes(response.data || []);
    } catch (error) {
      console.error('Error fetching notes:', error);
      setNotes([]);
    } finally {
      setLoadingNotes(false);
    }
  };

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer);
    fetchCustomerNotes(customer.customer_id);
  };

  const handleSubmit = async () => {
    if (!formData.note_text.trim()) {
      showSnackbar('Please enter note text', 'error');
      return;
    }

    try {
      await api.post(`/crm/customers/${selectedCustomer.customer_id}/notes`, formData);
      showSnackbar('Note added successfully', 'success');
      handleCloseDialog();
      fetchCustomerNotes(selectedCustomer.customer_id);
    } catch (error) {
      showSnackbar('Error adding note', 'error');
    }
  };

  const handleDeleteNote = async (noteId) => {
    if (window.confirm('Delete this note?')) {
      try {
        await api.delete(`/crm/notes/${noteId}`);
        showSnackbar('Note deleted successfully', 'success');
        fetchCustomerNotes(selectedCustomer.customer_id);
      } catch (error) {
        showSnackbar('Error deleting note', 'error');
      }
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({ note_text: '', note_type: 'GENERAL' });
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const getNoteTypeColor = (type) => {
    switch(type) {
      case 'IMPORTANT': return '#f44336';
      case 'FOLLOW_UP': return '#ff9800';
      case 'MEETING': return '#9c27b0';
      case 'CALL': return '#2196f3';
      default: return '#666';
    }
  };

  if (loadingCustomers) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 3, background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)', color: 'white' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" fontWeight="bold">Customers</Typography>
                <IconButton onClick={fetchCustomers} sx={{ color: 'white' }}><RefreshIcon /></IconButton>
              </Box>
              <Typography variant="body2">Select a customer to view notes</Typography>
            </Box>
            <Box sx={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
              {customers.map((customer) => (
                <Box key={customer.customer_id} onClick={() => handleCustomerSelect(customer)} sx={{
                  p: 2.5, borderBottom: '1px solid #eee', cursor: 'pointer',
                  bgcolor: selectedCustomer?.customer_id === customer.customer_id ? '#fff3e0' : 'white',
                  '&:hover': { bgcolor: '#fff8e1' }
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: '#ff9800' }}><PersonIcon /></Avatar>
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">{customer.customer_name}</Typography>
                      <Typography variant="caption" color="textSecondary">{customer.email || 'No email'}</Typography>
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          {!selectedCustomer ? (
            <Card sx={{ borderRadius: 3, textAlign: 'center', py: 8 }}>
              <NoteIcon sx={{ fontSize: 80, color: '#ccc' }} />
              <Typography variant="h6" color="textSecondary">Select a customer to view notes</Typography>
            </Card>
          ) : (
            <Card sx={{ borderRadius: 3, overflow: 'hidden' }}>
              <Box sx={{ p: 3, background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" fontWeight="bold">{selectedCustomer.customer_name} - Notes</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)} sx={{ bgcolor: 'white', color: '#ff9800' }}>
                  Add Note
                </Button>
              </Box>
              <Box sx={{ p: 3, maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
                {loadingNotes ? (
                  <CircularProgress />
                ) : notes.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <NoteIcon sx={{ fontSize: 60, color: '#ccc' }} />
                    <Typography color="textSecondary">No notes for this customer</Typography>
                  </Box>
                ) : (
                  notes.map((note) => (
                    <Card key={note.note_id} sx={{ mb: 2 }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Chip label={note.note_type} size="small" sx={{ bgcolor: getNoteTypeColor(note.note_type) + '20', color: getNoteTypeColor(note.note_type) }} />
                          <IconButton size="small" color="error" onClick={() => handleDeleteNote(note.note_id)}><DeleteIcon /></IconButton>
                        </Box>
                        <Typography variant="body2" sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>{note.note_text}</Typography>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="caption" color="textSecondary">Created by {note.created_by} on {new Date(note.created_at).toLocaleString()}</Typography>
                        {note.is_edited && <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>Edited on {new Date(note.edited_at).toLocaleString()}</Typography>}
                      </CardContent>
                    </Card>
                  ))
                )}
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#ff9800', color: 'white' }}>Add Note for {selectedCustomer?.customer_name}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Note" multiline rows={4} value={formData.note_text} onChange={(e) => setFormData({...formData, note_text: e.target.value})} sx={{ mt: 2 }} required />
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Note Type</InputLabel>
            <Select value={formData.note_type} label="Note Type" onChange={(e) => setFormData({...formData, note_type: e.target.value})}>
              <MenuItem value="GENERAL">General</MenuItem>
              <MenuItem value="IMPORTANT">Important</MenuItem>
              <MenuItem value="FOLLOW_UP">Follow Up</MenuItem>
              <MenuItem value="MEETING">Meeting</MenuItem>
              <MenuItem value="CALL">Call</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" sx={{ bgcolor: '#ff9800' }}>Add Note</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({...snackbar, open: false})}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default NotesManagement;
